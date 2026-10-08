from data.customer_db import (
    load_customers,
    save_customer
)

from olt.get_status import (
    get_pon_info,
    get_onu_wan_config,
    get_onu_service_config,
    connect_olt
)

PONS = [
    "1/1/1",
    "1/1/3",
    "1/1/4",
    "1/1/5",
    "1/1/6",
    "1/1/7",
    "1/1/8"
]

customers = load_customers()

db_onu = {
    (
        c["pon"],
        str(c["onu_id"])
    )
    for c in customers
}

tn = connect_olt()

added = 0

try:

    for pon in PONS:

        print("SCAN", pon)

        for onu in get_pon_info(pon):

            key = (
                pon,
                str(onu["onu_id"])
            )

            if key in db_onu:
                continue

            print(
                "NEW ONU",
                pon,
                onu["onu_id"]
            )

            wan = get_onu_wan_config(
                pon,
                onu["onu_id"],
                tn
            )

            svc = get_onu_service_config(
                pon,
                onu["onu_id"],
                tn
            )

            cust = {
                "name": f"AUTO_{onu['sn']}",
                "pon": pon,
                "onu_id": str(onu["onu_id"]),
                "sn": onu["sn"],
                "vlan": svc["vlan"],
                "package": svc["pppoe_package"],
                "pppoe_package": svc["pppoe_package"],
                "bridge_package": svc["bridge_package"],
                "bridge_vlan": svc["bridge_vlan"],
                "pppoe_user": wan["pppoe_user"],
                "pppoe_pass": wan["pppoe_pass"],
                "mode": (
                    "PPPOE+BRIDGE"
                    if svc["bridge_package"]
                    else "PPPOE"
                ),
                "onu_type": "AUTO"
            }

            save_customer(cust)

            added += 1

finally:

    tn.close()

print()
print("NEW ONU =", added)
