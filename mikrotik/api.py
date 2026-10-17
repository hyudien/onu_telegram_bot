from librouteros import connect
from data.mikrotik_routers import ROUTERS

def get_api(router_id):

    router = ROUTERS[router_id]
    if not router["username"] or not router["password"]:
        raise RuntimeError(
            f"Kredensial router {router_id} belum diatur di file .env."
        )

    api = connect(
        host=router["host"],
        port=router["port"],
        username=router["username"],
        password=router["password"]
    )

    return api
