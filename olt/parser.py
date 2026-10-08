def parse_uncfg(output):

    onu_list = []

    for line in output.splitlines():

        if "gpon-onu_" not in line:
            continue

        parts = line.split()

        if len(parts) < 3:
            continue

        onuindex = parts[0]
        sn = parts[1]

        pon = onuindex.replace(
            "gpon-onu_",
            ""
        ).split(":")[0]

        onu_list.append({
            "sn": sn,
            "pon": pon
        })

    return onu_list
