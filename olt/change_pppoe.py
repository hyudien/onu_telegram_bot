import telnetlib
import time

from olt.zte import HOST, USER, PASS
from data.vlans import VLANS


def change_pppoe(
    pon,
    onu_id,
    username,
    password,
    vlan
):

    profile = VLANS[str(vlan)]["profile"]

    tn = telnetlib.Telnet(HOST, 23)

    tn.read_until(b"Username:")
    tn.write(USER.encode() + b"\n")

    tn.read_until(b"Password:")
    tn.write(PASS.encode() + b"\n")

    time.sleep(2)

    tn.write(b"conf t\n")
    time.sleep(1)

    cmd = (
        f"pon-onu-mng "
        f"gpon-onu_{pon}:{onu_id}\n"
    )

    tn.write(cmd.encode())

    time.sleep(2)

    cmd = (
        f"wan-ip 1 mode pppoe "
        f"username {username} "
        f"password {password} "
        f"vlan-profile {profile}\n"
    )

    print("KIRIM =", cmd)

    tn.write(cmd.encode())

    time.sleep(3)

    output = tn.read_very_eager().decode(
        errors="ignore"
    )

    print(output)

    tn.write(b"end\n")
    tn.write(b"exit\n")

    tn.close()

    if "profile does not exist" in output:
        return False

    return True
