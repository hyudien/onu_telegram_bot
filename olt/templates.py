def build_pppoe(data, onu_id):

    return f"""
interface gpon-onu_{data['pon']}:{onu_id}

name {data['customer']}

tcont 1 name PPP profile {data['package']}

gemport 1 name PPP tcont 1

gemport 1 traffic-limit upstream {data['package']} downstream {data['package']}

service-port 1 vport 1 user-vlan {data['vlan']} vlan {data['vlan']}

service-port 1 description PPP
"""
