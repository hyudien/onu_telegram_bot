from olt.zte import open_olt_connection
import telnetlib
import time

def change_package(
    pon,
    onu_id,
    pppoe_package,
    bridge_package=None
):

    tn = open_olt_connection()

    tn.read_until(b"Username:")
    tn.write(USER.encode() + b"\n")

    tn.read_until(b"Password:")
    tn.write(PASS.encode() + b"\n")
    time.sleep(1)

    tn.write(b"conf t\n")
    time.sleep(1)

    cmd = (
        f"interface gpon-onu_{pon}:{onu_id}\n"
        f"tcont 1 name PPP profile {pppoe_package}\n"
        f"gemport 1 traffic-limit upstream {pppoe_package} downstream {pppoe_package}\n"
    )

    if bridge_package:

        cmd += (
            f"tcont 2 name BRG profile {bridge_package}\n"
            f"gemport 2 traffic-limit upstream {bridge_package} downstream {bridge_package}\n"
        )

    print("KIRIM =", cmd)

    tn.write(cmd.encode())

    time.sleep(2)

    output = tn.read_very_eager().decode(
        errors="ignore"
    )

    print(output)

    tn.write(b"end\n")
    tn.close()

    return "[Successful]" in output or "ZXAN" in output
