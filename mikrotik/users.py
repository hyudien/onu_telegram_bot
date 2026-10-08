from mikrotik.api import get_api

def get_active_users(router_id):

    api = get_api(router_id)

    users = []

    for row in api.path("ppp", "active"):
        users.append(row["name"])

    return users

def get_offline_users(router_id):

    api = get_api(router_id)

    secrets = list(
        api.path(
            "ppp",
            "secret"
        )
    )

    active = list(
        api.path(
            "ppp",
            "active"
        )
    )

    active_names = {
        a.get("name")
        for a in active
    }

    offline = []

    for user in secrets:

        name = user.get(
            "name",
            "-"
        )

        if name not in active_names:
            offline.append(name)

    return offline

def get_user(router_id, username):

    api = get_api(router_id)

    secrets = api.path(
        "ppp",
        "secret"
    )

    users = list(
        secrets.select()
    )

    for user in users:

        if user.get("name") == username:
            return user

    return None

def get_online_users(router_id):

    api = get_api(router_id)

    active = list(
        api.path(
            "ppp",
            "active"
        )
    )

    hasil = []

    for user in active:

        hasil.append(
            user.get(
                "name",
                "-"
            )
        )

    return hasil

