VLANS = {
    "150": {
        "name": "KWL",
        "profile": "vlan-KWL(150)"
    },
    "151": {
        "name": "TJS",
        "profile": "vlan-TJS(151)"
    },
    "152": {
        "name": "SS",
        "profile": "vlan-SS(152)"
    },
    "153": {
        "name": "EG",
        "profile": "vlan-EG(153)"
    },
    "154": {
        "name": "MDR",
        "profile": "vlan-MDR(154)"
    },
    "155": {
        "name": "KSB",
        "profile": "vlan-KSB(155)"
    },
    "177": {
        "name": "PPP",
        "profile": "TEST_177"
    }
}

def detect_mode(vlan):

    vlan = str(vlan)

    if vlan in ["30", "44"]:
        return "BRIDGE"

    return "PPPOE"
