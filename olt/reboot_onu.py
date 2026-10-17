import telnetlib
import time

from olt.zte import open_olt_connection


def reboot_onu(pon, onu_id):

    tn = open_olt_connection()

    tn.read_until(b"Username:")
    tn.write(USER.encode() + b"\n")

    tn.read_until(b"Password:")
    tn.write(PASS.encode() + b"\n")

    time.sleep(2)

    tn.write(b"conf t\n")
    time.sleep(1)

    tn.write(
        f"pon-onu-mng gpon-onu_{pon}:{onu_id}\n".encode()
    )

    time.sleep(1)

    tn.write(b"reboot\n")

    time.sleep(1)

    tn.write(b"y\n")

    time.sleep(2)

    tn.write(b"exit\n")
    tn.close()

    return True
