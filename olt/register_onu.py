import telnetlib
import time

from olt.zte import open_olt_connection
from data.vlans import VLANS

def send_command(tn, cmd, delay=1):

    print(f"SEND > {cmd}")

    tn.write(cmd.encode() + b"\n")

    time.sleep(delay)

    output = tn.read_very_eager().decode(
        errors="ignore"
    )

    print(output)

    return output


def configure_onu_service(tn, data, onu_id):

    mode = data.get(
        "mode",
        "PPPOE"
    ).upper()

    service_name = "PPP"

    if mode == "BRIDGE":
        service_name = "BRG"


    send_command(
        tn,
        "exit"
    )

    send_command(
        tn,
        f"interface gpon-onu_{data['pon']}:{onu_id}"
    )

    send_command(
        tn,
        f"name {data['customer']}"
    )

    send_command(
        tn,
        f"tcont 1 name {service_name} profile {data.get('pppoe_package', data.get('package'))}"
    )

    send_command(
        tn,
        f"gemport 1 name {service_name} tcont 1"
    )

    send_command(
        tn,
        f"gemport 1 traffic-limit upstream {data.get('pppoe_package', data.get('package'))} downstream {data.get('pppoe_package', data.get('package'))}"
    )

    send_command(
        tn,
        f"service-port 1 vport 1 user-vlan {data['vlan']} vlan {data['vlan']}"
    )

    send_command(
        tn,
        f"service-port 1 description {service_name}"
    )

    if mode == "PPPOE+BRIDGE":

        send_command(
            tn,
            f"tcont 2 name BRG profile {data['bridge_package']}"
        )

        send_command(
            tn,
            f"gemport 2 name BRG tcont 2"
        )

        send_command(
            tn,
            f"gemport 2 traffic-limit upstream {data['bridge_package']} "
            f"downstream {data['bridge_package']}"
        )

        send_command(
            tn,
            f"service-port 2 vport 2 "
            f"user-vlan {data['bridge_vlan']} "
            f"vlan {data['bridge_vlan']}"
        )

        send_command(
            tn,
            "service-port 2 description BRG"
        )

def configure_onu_mng(tn, data, onu_id):

    mode = data.get(
        "mode",
        "PPPOE"
    ).upper()

    if mode == "BRIDGE":
        return
    try:
        profile = VLANS[data["vlan"]]["profile"]

        print("MODE =", repr(data.get("mode")))
        print("VLAN =", data["vlan"])
        print("PROFILE =", profile)

        send_command(tn, "exit")

        send_command(
        tn,
        f"pon-onu-mng gpon-onu_{data['pon']}:{onu_id}"
        )

        print("MODE MNG =", mode)
        print("BRIDGE VLAN =", data.get("bridge_vlan"))
        if mode == "PPPOE":

            send_command(
                tn,
                f"service PPP gemport 1 vlan {data['vlan']}"
            )

            send_command(
                tn,
                f"wan-ip 1 mode pppoe "
                f"username {data['pppoe_user']} "
                f"password {data['pppoe_pass']} "
                f"vlan-profile {profile} host 1"
            )

            send_command(
                tn,
                f"wan-ip 1 ping-response enable traceroute-response enable"
            )

            send_command(
                tn,
                f"security-mgmt 1 state enable mode forward"
            )

        elif mode == "BRIDGE":

            send_command(
                tn,
                f"service ServiceName gemport 1 cos 0 vlan {data['vlan']}"
            )

            for port in [1, 2, 3, 4]:

                send_command(
                    tn,
                    f"vlan port eth_0/{port} mode hybrid def-vlan {data['vlan']}"
                )

        elif mode == "PPPOE+BRIDGE":

            send_command(
                tn,
                f"service PPP gemport 1 vlan {data['vlan']}"
            )

            send_command(
                tn,
                f"service BRG gemport 2 vlan {data['bridge_vlan']}"
            )

            send_command(
                tn,
                f"wan-ip 1 mode pppoe "
                f"username {data['pppoe_user']} "
                f"password {data['pppoe_pass']} "
                f"vlan-profile {profile} host 1"
            )

            send_command(
                tn,
                f"wan-ip 1 ping-response enable traceroute-response enable"
            )

            for port in [1, 2, 3, 4]:

                send_command(
                    tn,
                    f"vlan port eth_0/{port} mode hybrid def-vlan {data['bridge_vlan']}"
                )
    except Exception as e:
        print("ERROR CONFIG ONU MNG =", e)

def register_onu(data, onu_id):

    tn = open_olt_connection()

    tn.read_until(b"Username:")
    tn.write(USER.encode() + b"\n")

    tn.read_until(b"Password:")
    tn.write(PASS.encode() + b"\n")

    time.sleep(1)

    send_command(tn, "terminal length 0")
    send_command(tn, "conf t")

    result = send_command(
        tn,
        f"interface gpon-olt_{data['pon']}"
    )

    result += send_command(
        tn,
        f"onu {onu_id} type {data['onu_type']} sn {data['sn']}",
        2
    )

    if "[Successful]" not in result:

        tn.close()

        return result

    configure_onu_service(
        tn,
        data,
        onu_id
    )

    configure_onu_mng(
        tn,
        data,
        onu_id
    )

    send_command(
        tn,
        "end"
    )

    tn.close()

    return result

def save_config(tn):

    send_command(
        tn,
        "write",
        5
    )

    tn.close()
    return result

def enable_remote_access(tn):

    send_command(tn, "security-mgmt 1 state enable")
    send_command(tn, "security-mgmt 1 mode forward")
    send_command(tn, "security-mgmt 1 ingress-type wan")

    send_command(tn, "security-mgmt 1 protocol web https")
