import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)
import telnetlib
import time

from olt.zte import HOST, USER, PASS

PON = "1/1/6"
ONU = "3"

tn = telnetlib.Telnet(HOST, 23)

tn.read_until(b"Username:")
tn.write(USER.encode() + b"\n")

tn.read_until(b"Password:")
tn.write(PASS.encode() + b"\n")

time.sleep(2)

tn.write(b"conf t\n")
time.sleep(1)

tn.read_very_eager()

cmd = f"pon-onu-mng gpon-onu_{PON}:{ONU}\n"

print("KIRIM =", cmd)

tn.write(cmd.encode())

time.sleep(2)

output = tn.read_very_eager().decode(
    errors="ignore"
)

print(output)

output = tn.read_very_eager().decode(
    errors="ignore"
)

print(output)

tn.write(b"show wan-ip 1\n")

time.sleep(2)

output = tn.read_very_eager().decode(
    errors="ignore"
)

print(output)
tn.write(b"exit\n")
tn.close()
