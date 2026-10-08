from olt.delete_onu import delete_onu
from olt.register_onu import register_onu
from olt.get_status import get_onu_wan_config

def change_onu(cust, new_sn):

    wan = get_onu_wan_config(
        cust["pon"],
        cust["onu_id"]
    )

    print("WAN =", wan)

    ok = delete_onu(
        cust["pon"],
        cust["onu_id"]
    )

    if not ok:
        return False

    data = {
        "customer": cust["name"],
        "pon": cust["pon"],
        "sn": new_sn,
        "onu_type": cust.get(
            "onu_type",
            "ALL-ONT"
        ),
        "mode": cust.get(
            "mode",
            "PPPOE"
        ),
        "vlan": cust["vlan"],
        "bridge_vlan": cust.get(
             "bridge_vlan",
             "30"
        ),
        "package": cust["package"],
    }
    if data["mode"] == "PPPOE":
        data["pppoe_user"] = wan["pppoe_user"]
        data["pppoe_pass"] = wan["pppoe_pass"]

    result = register_onu(
        data,
        int(cust["onu_id"])
    )

    if "[Successful]" not in str(result):
        return False

    return True
