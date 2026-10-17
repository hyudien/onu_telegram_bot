import telnetlib
import time

STATUS_CACHE = {
    "data": None,
    "last_update": 0
}

from olt.zte import HOST, USER, PASS, open_olt_connection
from olt.register_onu import send_command

def connect_olt():

    tn = open_olt_connection()

    tn.read_until(b"Username:")
    tn.write(USER.encode() + b"\n")

    tn.read_until(b"Password:")
    tn.write(PASS.encode() + b"\n")

    time.sleep(1)

    send_command(
        tn,
        "terminal length 0"
    )

    tn.read_very_eager()

    return tn

def get_pon_info_raw(pon):

    tn = connect_olt()

    output = send_command(
        tn,
        f"show pon onu information gpon-olt_{pon}",
        3
    )

    tn.close()

    return output

def get_onu_states():

    tn = connect_olt()

    output = send_command(
        tn,
        "show gpon onu state",
        15
    )

    tn.close()

    result = []

    for line in output.splitlines():

        line = line.strip()

        if "/" not in line:
            continue

        parts = line.split()

        if len(parts) < 4:
            continue

        try:

            pon, onu_id = parts[0].split(":")

        except:
            continue

        phase = parts[3].lower()

        if phase == "working":

            status = "online"

        elif phase == "dyinggasp":

            status = "dyinggasp"

        elif phase == "los":

            status = "los"

        else:

            status = "offline"

        result.append({
            "pon": pon,
            "onu_id": onu_id,
            "status": status
        })

    return result

def get_cached_onu_states(refresh=False):

    now = time.time()

    if (
        not refresh
        and STATUS_CACHE["data"]
        and now - STATUS_CACHE["last_update"] < 60
    ):
        return STATUS_CACHE["data"]

    data = get_onu_states()

    STATUS_CACHE["data"] = data
    STATUS_CACHE["last_update"] = now

    return data

def get_summary():

    data = get_cached_onu_states()

    result = {
        "online": 0,
        "offline": 0,
        "los": 0,
        "dyinggasp": 0,
        "total": len(data)
    }

    for x in data:

        status = x["status"]

        if status in result:

            result[status] += 1

    return result

def get_problem_onus():

    result = []

    for onu in get_cached_onu_states():

        if onu["status"] != "online":
            result.append(onu)

    return result

def get_pon_summary(pon):

    result = {
        "online": 0,
        "offline": 0,
        "los": 0,
        "dyinggasp": 0,
        "total": 0
    }

    for onu in get_cached_onu_states():

        if onu["pon"] != pon:
            continue

        result["total"] += 1

        status = onu["status"]

        if status in result:
            result[status] += 1

    return result

def get_pon_problems(pon):

    result = []

    for onu in get_problem_onus():

        if onu["pon"] == pon:
            result.append(onu)

    return result

def get_pon_problem_customers(pon):

    from data.customer_db import load_customers

    customers = load_customers()

    result = []

    for onu in get_pon_problems(pon):

        if onu["pon"] != pon:
            continue

        name = "-"

        for c in customers:

            if (
                c.get("pon") == onu["pon"]
                and str(c.get("onu_id")) == str(onu["onu_id"])
            ):
                name = c.get("name", "-")
                break

        result.append({
            "onu_id": onu["onu_id"],
            "name": name,
            "status": onu["status"]
        })

    return result

def get_pon_info(pon):

    output = get_pon_info_raw(pon)

    result = []

    for line in output.splitlines():

        line = line.strip()

        if not line.startswith(f"{pon}:"):
            continue

        parts = line.split()

        onu_id = parts[0].split(":")[1]

        sn = ""

        for p in parts:
            if "SN(" in p:
                sn = (
                    p.replace("SN(", "")
                     .replace(")", "")
                     .strip()
                )
                break

        status = "offline"

        if "working" in line.lower():
            status = "online"

        result.append({
            "onu_id": onu_id,
            "sn": sn,
            "status": status
        })

    return result

def get_pon_summary_live(data):

    result = {
        "online": 0,
        "offline": 0,
        "total": len(data)
    }

    for onu in data:

        if onu["status"] == "online":
            result["online"] += 1
        else:
            result["offline"] += 1

    return result

def get_pon_problem_customers_live(data, pon):

    from data.customer_db import load_customers

    customers = load_customers()

    result = []

    for onu in data:

        if onu["status"] == "online":
            continue

        name = "-"

        for c in customers:

            if (
                c.get("pon") == pon
                and str(c.get("onu_id")) == str(onu["onu_id"])
            ):
                name = c.get("name", "-")
                break

        result.append({
            "onu_id": onu["onu_id"],
            "name": name,
            "status": onu["status"]
        })

    return result

def check_onu_online(pon, onu_id):

    data = get_onu_states()

    for onu in data:

        if (
            onu["pon"] == pon
            and str(onu["onu_id"]) == str(onu_id)
        ):
            return onu["status"] == "online"

    return False

def get_onu_wan_config(pon, onu_id, tn=None):

    own_conn = False
    if tn is None:
        tn = connect_olt()
        own_conn = True

    output = send_command(
        tn,
        f"show onu running config gpon-onu_{pon}:{onu_id}",
        1
    )

    if own_conn:
        tn.close()

    result = {
        "pppoe_user": "",
        "pppoe_pass": ""
    }

    for line in output.splitlines():

        line = line.strip()

        if (
            "wan-ip" in line
            and "username" in line
            and "password" in line
        ):

            try:

                user = (
                    line.split("username")[1]
                    .split("password")[0]
                    .strip()
                )

                passwd = (
                    line.split("password")[1]
                    .strip()
                    .split()[0]
                )

                result["pppoe_user"] = user
                result["pppoe_pass"] = passwd

                break

            except:
                pass

    return result

def get_onu_service_config(pon, onu_id, tn=None):

    own_conn = False

    if tn is None:
        tn = connect_olt()
        own_conn = True

    output = send_command(
        tn,
        f"show running-config interface gpon-onu_{pon}:{onu_id}",
        2
    )

    if own_conn:
        tn.close()

    result = {
        "pppoe_package": "",
        "bridge_package": "",
        "vlan": "",
        "bridge_vlan": ""
    }

    for line in output.splitlines():

        line = line.strip()

        if "tcont 1" in line and "profile" in line:
            result["pppoe_package"] = line.split("profile")[1].strip()

        elif "tcont 2" in line and "profile" in line:
            result["bridge_package"] = line.split("profile")[1].strip()

        elif "service-port 1" in line and "user-vlan" in line:

            try:
                result["vlan"] = (
                    line.split("user-vlan")[1]
                    .split()[0]
                )
            except:
                pass

        elif "service-port 2" in line and "user-vlan" in line:

            try:
                result["bridge_vlan"] = (
                    line.split("user-vlan")[1]
                    .split()[0]
                )
            except:
                pass

    return result
