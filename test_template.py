from olt.register_onu import preview_register

data = {
    "pon": "1/1/4",
    "sn": "ZTEGC456342B",
    "onu_type": "ALL-ONT",
    "customer": "TTT",
    "package": "UPto-50M",
    "vlan": "177"
}

print(
    preview_register(
        data,
        61
    )
)
