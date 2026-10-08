from librouteros import connect
from data.mikrotik_routers import ROUTERS

def get_api(router_id):

    router = ROUTERS[router_id]

    api = connect(
        host=router["host"],
        port=router["port"],
        username=router["username"],
        password=router["password"]
    )

    return api
