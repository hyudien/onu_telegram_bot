import json

DB_FILE = "data/customers.json"

with open(DB_FILE, "r") as f:
    customers = json.load(f)

for c in customers:

    if "pppoe_pass" not in c:
        c["pppoe_pass"] = ""

    if "onu_type" not in c:
        c["onu_type"] = "ALL-ONT"

    if "mode" not in c:
        c["mode"] = "PPPoE"

with open(DB_FILE, "w") as f:
    json.dump(
        customers,
        f,
        indent=4
    )

print("Database berhasil diperbaiki")

