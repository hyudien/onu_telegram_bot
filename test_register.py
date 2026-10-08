from olt.register_onu import register_onu

data = {
    "pon": "1/1/4",
    "sn": "ZTEGC456342B",
    "onu_type": "ALL-ONT",
    "customer": "TTT",
    "package": "UPto-50M",
    "vlan": "177",
    "pppoe_user": "ttt",
    "pppoe_pass": "ttt"
}

print(
    register_onu(
        data,
        61
    )
)
