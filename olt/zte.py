import telnetlib
import time

HOST = "192.168.220.31"
USER = "admin"
PASS = "admin99"


def get_uncfg_onu():

    tn = telnetlib.Telnet(HOST, 23)

    tn.read_until(b"Username:")
    tn.write(USER.encode() + b"\n")

    tn.read_until(b"Password:")
    tn.write(PASS.encode() + b"\n")

    time.sleep(2)

    tn.read_very_eager()

    tn.write(b"show gpon onu uncfg\n")

    time.sleep(3)

    output = tn.read_very_eager().decode(errors="ignore")

    tn.write(b"exit\n")

    tn.close()

    return output

def get_olt_config(pon):

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

    print(
        tn.read_very_eager().decode(
            errors="ignore"
        )
    )

    cmd = (
        f"show running-config interface "
        f"gpon-olt_{pon}\n"
    )

    tn.write(cmd.encode())

    time.sleep(3)

    output = tn.read_very_eager().decode(
        errors="ignore"
    )

    tn.write(b"exit\n")

    tn.close()

    return output

def connect_olt():

    tn = telnetlib.Telnet(HOST, 23)

    tn.read_until(b"Username:")
    tn.write(USER.encode() + b"\n")

    tn.read_until(b"Password:")
    tn.write(PASS.encode() + b"\n")

    time.sleep(2)

    tn.read_very_eager()
