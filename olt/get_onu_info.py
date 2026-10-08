import telnetlib
import time
import re

from olt.zte import HOST, USER, PASS


def get_onu_info(pon, onu_id):

    tn = telnetlib.Telnet(HOST, 23)

    tn.read_until(b"Username:")
    tn.write(USER.encode() + b"\n")

    tn.read_until(b"Password:")
    tn.write(PASS.encode() + b"\n")

    time.sleep(1)

    tn.write(b"conf t\n")
    time.sleep(1)

    cmd = (
        f"show pon power attenuation "
        f"gpon-onu_{pon}:{onu_id}\n"
    )

    tn.write(cmd.encode())

    time.sleep(2)

    output = tn.read_very_eager().decode(
        errors="ignore"
    )

    tn.close()

    up = re.search(
        r"up\s+Rx\s*:(-?\d+\.\d+).*?Tx\s*:(-?\d+\.\d+)",
        output,
        re.S
    )

    down = re.search(
        r"down\s+Tx\s*:(-?\d+\.\d+).*?Rx\s*:(-?\d+\.\d+)",
        output,
        re.S
    )

    loss = re.findall(
        r"(\d+\.\d+)\(dB\)",
        output
    )

    return {
        "olt_rx": up.group(1) if up else "-",
        "onu_tx": up.group(2) if up else "-",
        "olt_tx": down.group(1) if down else "-",
        "onu_rx": down.group(2) if down else "-",
        "loss_up": loss[0] if len(loss) > 0 else "-",
        "loss_down": loss[1] if len(loss) > 1 else "-"
    }
