import json
import os

USER_FILE = "data/allowed_users.json"


def load_users():

    if not os.path.exists(USER_FILE):

        with open(USER_FILE, "w") as f:
            json.dump(
                [185653926],
                f
            )

    with open(USER_FILE, "r") as f:
        return json.load(f)


def save_users(users):

    with open(USER_FILE, "w") as f:
        json.dump(
            users,
            f,
            indent=4
        )


ALLOWED_USERS = load_users()


def add_user(user_id):

    users = load_users()

    if user_id not in users:

        users.append(user_id)

        save_users(users)

    return True


def remove_user(user_id):

    users = load_users()

    users = [
        u for u in users
        if u != user_id
    ]

    save_users(users)
