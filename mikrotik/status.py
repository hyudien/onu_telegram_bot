from mikrotik.api import get_api

def get_status(router_id):

    api = get_api(router_id)

    total = len(list(api.path("ppp", "secret")))
    online = len(list(api.path("ppp", "active")))
    offline = total - online

    resource = list(
        api.path("system", "resource")
    )[0]

    return {
        "total": total,
        "online": online,
        "offline": offline,
        "cpu": resource["cpu-load"],
        "memory": round(
            int(resource["free-memory"]) /
            1024 / 1024
        ),
        "uptime": resource["uptime"]
    }
