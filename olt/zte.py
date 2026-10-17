import os
import telnetlib
import time

from settings import load_dotenv

load_dotenv()

HOST = os.getenv("OLT_HOST", "192.168.220.31")
PORT = int(os.getenv("OLT_PORT", "23"))
USER = os.getenv("OLT_USERNAME", "")
PASS = os.getenv("OLT_PASSWORD", "")


def open_olt_connection():
    if not USER or not PASS:
        raise RuntimeError(
            "OLT_USERNAME dan OLT_PASSWORD harus diatur di file .env."
        )
    return telnetlib.Telnet(HOST, PORT)


def get_uncfg_onu():

    tn = open_olt_connection()

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

    tn = open_olt_connection()

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

    tn = open_olt_connection()

    tn.read_until(b"Username:")
    tn.write(USER.encode() + b"\n")

    tn.read_until(b"Password:")
    tn.write(PASS.encode() + b"\n")

    time.sleep(2)

    tn.read_very_eager()
