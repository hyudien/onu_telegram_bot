from data.customer_db import load_customers
from olt.get_status import get_pon_info

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

missing = []

for pon in PONS:

    print("SCAN", pon)

    try:

        data = get_pon_info(pon)

        for onu in data:

            key = (
                pon,
                str(onu["onu_id"])
            )

            if key not in db_onu:

                missing.append({
                    "pon": pon,
                    "onu_id": onu["onu_id"],
                    "sn": onu["sn"],
                    "status": onu["status"]
                })

    except Exception as e:

        print(
            f"ERROR {pon} : {e}"
        )

print()
print("ONU DB     =", len(customers))
print("ONU HILANG =", len(missing))
print()

for onu in missing:

    print(
        onu["pon"],
        onu["onu_id"],
        onu["sn"]
    )
