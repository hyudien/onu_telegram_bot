def get_onu_wan_config(pon, onu_id):

    tn = connect_olt()

    output = send_command(
        tn,
        f"show onu running config gpon-onu_{pon}:{onu_id}",
        2
    )

    tn.close()

    result = {
        "pppoe_user": "",
        "pppoe_pass": ""
    }

    for line in output.splitlines():

        line = line.strip()

        if "wan-ip" in line and "username" in line:

            try:

                user = line.split("username")[1]
                user = user.split("password")[0].strip()

                passwd = line.split("password")[1]
                passwd = passwd.split()[0].strip()

                result["pppoe_user"] = user
                result["pppoe_pass"] = passwd

                break

            except:
                pass

    return result
