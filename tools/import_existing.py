import sys
import os
import re
import json
import telnetlib
import time

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from olt.zte import HOST, USER, PASS


def send_cmd(tn, cmd, delay=2):

    tn.write((cmd + "\n").encode())

    time.sleep(delay)

    return tn.read_very_eager().decode(
        errors="ignore"
    )


all_onus = []

print("LOGIN OLT...")

tn = telnetlib.Telnet(HOST, 23)

tn.read_until(b"Username:")
tn.write(USER.encode() + b"\n")

tn.read_until(b"Password:")
tn.write(PASS.encode() + b"\n")

time.sleep(2)

tn.write(b"enable\n")
time.sleep(1)

tn.write(b"terminal length 0\n")
time.sleep(1)

tn.read_very_eager()


print("SCAN ONU...")

for port in range(1, 9):

    print(f"SCAN PORT {port}")

    output = send_cmd(
        tn,
        f"show gpon onu baseinfo gpon-olt_1/1/{port}",
        5
    )

    matches = re.findall(
        r"gpon-onu_(\d+/\d+/\d+):(\d+)\s+.*?SN:([A-Z0-9]+)",
        output
    )

    for pon, onu_id, sn in matches:

        all_onus.append({
            "pon": pon,
            "onu_id": onu_id,
            "sn": sn
        })

print(f"TOTAL ONU FOUND = {len(all_onus)}")


print("AMBIL DETAIL ONU...")

for i, customer in enumerate(all_onus, start=1):

    pon = customer["pon"]
    onu_id = customer["onu_id"]

    iface = f"gpon-onu_{pon}:{onu_id}"

    print(
        f"[{i}/{len(all_onus)}] {iface}"
    )

    cfg1 = send_cmd(
        tn,
        f"show running-config interface {iface}",
        2
    )

    cfg2 = send_cmd(
        tn,
        f"show onu running config {iface}",
        2
    )

    m = re.search(
        r"\n\s*name\s+(.+)",
        cfg1
    )

    if m:
        customer["name"] = (
            m.group(1)
            .strip()
        )

    m = re.search(
        r"profile\s+([^\r\n]+)",
        cfg1
    )

    if m:
        customer["package"] = (
            m.group(1)
            .strip()
        )

    m = re.search(
        r"user-vlan\s+(\d+)",
        cfg1
    )

    if m:
        customer["vlan"] = (
            m.group(1)
        )

    m = re.search(
        r"username\s+(\S+)",
        cfg2
    )

    if m:
        customer["pppoe_user"] = (
            m.group(1)
        )

tn.close()

with open(
    "data/customers.json",
    "w"
) as f:

    json.dump(
        all_onus,
        f,
        indent=4
    )

print(
    f"IMPORT SELESAI : {len(all_onus)} ONU"
)
