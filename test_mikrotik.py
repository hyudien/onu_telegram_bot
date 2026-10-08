from mikrotik.actions import (
    set_profile,
    set_comment,
    enable_user
)

print(
    set_profile(
        "KWL",
        "ujicoba",
        "OLT-KWL"
    )
)

print(
    set_comment(
        "KWL",
        "ujicoba",
        "BOT TEST"
    )
)

print(
    enable_user(
        "KWL",
        "ujicoba"
    )
)
