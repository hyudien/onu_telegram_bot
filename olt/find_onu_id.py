import re

def find_free_onu_id(config):

    used = []

    for line in config.splitlines():

        m = re.search(r"onu\s+(\d+)\s+type", line)

        if m:
            used.append(int(m.group(1)))

    if not used:
        return 1

    used = sorted(used)

    for i in range(1, max(used) + 1):

        if i not in used:
            return i

    return max(used) + 1
