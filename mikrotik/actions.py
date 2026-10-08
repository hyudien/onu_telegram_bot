from mikrotik.api import get_api

def add_user(
    router_id,
    username,
    password,
    profile,
    comment
):

    api = get_api(router_id)

    api.path("ppp", "secret").add(
        name=username,
        password=password,
        profile=profile,
        comment=comment,
        service="pppoe"
    )

    return True

def disable_user(router_id, username):

    api = get_api(router_id)

    secrets = api.path("ppp", "secret")

    for row in secrets:

        if row["name"] == username:

            secrets.update(
                **{
                    ".id": row[".id"],
                    "disabled": "true"
                }
            )

            return True

    return False

def enable_user(
    router_id,
    username
):

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

            secrets.update(
                **{
                    ".id": user[".id"],
                    "disabled": "no"
                }
            )

            return True

    return False

def delete_user(router_id, username):

    api = get_api(router_id)

    secrets = api.path("ppp", "secret")

    users = list(
        secrets.select()
    )

    for user in users:

        if user.get("name") == username:

            secrets.remove(
                user[".id"]
            )

            return True

    return False

def set_password(
    router_id,
    username,
    password
):

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

            secrets.update(
                **{
                    ".id": user[".id"],
                    "password": password
                }
            )

            return True

    return False

def set_profile(
    router_id,
    username,
    profile
):

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

            secrets.update(
                **{
                    ".id": user[".id"],
                    "profile": profile
                }
            )

            return True

    return False

def set_comment(
    router_id,
    username,
    comment
):

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

            secrets.update(
                **{
                    ".id": user[".id"],
                    "comment": comment
                }
            )

            return True

    return False

def find_users(router_id, keyword):

    api = get_api(router_id)

    secrets = api.path(
        "ppp",
        "secret"
    )

    users = list(
        secrets.select()
    )

    hasil = []

    keyword = keyword.lower()

    for user in users:

        nama = user.get(
            "name",
            ""
        ).lower()

        if keyword in nama:
            hasil.append(
                user["name"]
            )

    return hasil
