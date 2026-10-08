from data.customer_db import load_customers
from data.customer_db import save_all_customers

from olt.get_status import (
    get_onu_wan_config,
    get_onu_service_config,
    connect_olt
)
customers = load_customers()

updated = 0

tn = connect_olt()

for c in customers:
    try:

        wan = get_onu_wan_config(
            c["pon"],
            c["onu_id"],
            tn
        )
        svc = get_onu_service_config(
            c["pon"],
            c["onu_id"],
            tn
        )

        if wan["pppoe_pass"]:

            c["pppoe_user"] = wan["pppoe_user"]
            c["pppoe_pass"] = wan["pppoe_pass"]
            c["pppoe_package"] = svc["pppoe_package"]

            if svc["bridge_package"]:
                c["bridge_package"] = svc["bridge_package"]

            if svc["bridge_vlan"]:
                c["bridge_vlan"] = svc["bridge_vlan"]

            if svc["vlan"]:
                c["vlan"] = svc["vlan"]

            updated += 1

            print(
                f"UPDATE {c['name']} -> {wan['pppoe_user']}"
            )

    except Exception as e:

        print(
            f"ERROR {c['name']} : {e}"
        )

tn.close()

save_all_customers(customers)

print()
print("UPDATED =", updated)
