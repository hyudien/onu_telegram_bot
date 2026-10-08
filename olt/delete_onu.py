import telnetlib
import time

from olt.zte import HOST, USER, PASS


def delete_onu(pon, onu_id):

    tn = telnetlib.Telnet(HOST, 23)

    tn.read_until(b"Username:")
    tn.write(USER.encode() + b"\n")

    tn.read_until(b"Password:")
    tn.write(PASS.encode() + b"\n")

    time.sleep(1)

    tn.write(b"conf t\n")
    time.sleep(1)

    tn.write(
        f"interface gpon-olt_{pon}\n".encode()
    )
    time.sleep(1)

    cmd = f"no onu {onu_id}\n"

    print("KIRIM =", cmd)

    tn.write(cmd.encode())

    output = ""

    for _ in range(5):
       time.sleep(1)
       output += tn.read_very_eager().decode(
           errors="ignore"
       )

    tn.write(b"exit\n")
    time.sleep(0.5)

    tn.write(b"exit\n")
    time.sleep(0.5)

    output += tn.read_very_eager().decode(
        errors="ignore"
    )

    print("OUTPUT=")
    print(output)

    tn.close()


    return "Success" in output
