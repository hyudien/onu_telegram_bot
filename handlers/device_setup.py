from telegram import Update
from telegram.ext import ContextTypes

from handlers.common import ADMIN_ID, MENU
from data.device_config import (
    has_complete_device_ips,
    save_device_ips,
    validate_ip
)
from data.mikrotik_routers import ROUTERS


async def start_device_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Hanya admin yang dapat mengatur IP perangkat.")
        return

    context.user_data["device_setup"] = {
        "stage": "olt",
        "router_ids": list(ROUTERS),
        "router_hosts": {}
    }
    await update.message.reply_text(
        "Setup alamat perangkat sebelum masuk menu.\n"
        "Masukkan IP OLT:"
    )


async def handle_device_setup_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    setup = context.user_data.get("device_setup")
    if not setup:
        return False

    try:
        host = validate_ip(update.message.text)
    except ValueError as exc:
        await update.message.reply_text(f"{exc} Coba lagi:")
        return True

    if setup["stage"] == "olt":
        setup["olt_host"] = host
        setup["stage"] = "mikrotik"
        setup["router_index"] = 0
        router_id = setup["router_ids"][0]
        await update.message.reply_text(
            f"IP OLT disimpan sementara.\nMasukkan IP MikroTik {router_id}:"
        )
        return True

    router_id = setup["router_ids"][setup["router_index"]]
    setup["router_hosts"][router_id] = host
    setup["router_index"] += 1

    if setup["router_index"] < len(setup["router_ids"]):
        next_router = setup["router_ids"][setup["router_index"]]
        await update.message.reply_text(
            f"Masukkan IP MikroTik {next_router}:"
        )
        return True

    config = save_device_ips(setup["olt_host"], setup["router_hosts"])
    for configured_router, configured_host in config["mikrotik_hosts"].items():
        ROUTERS[configured_router]["host"] = configured_host

    context.user_data.pop("device_setup", None)
    await update.message.reply_text(
        "✅ IP OLT dan MikroTik berhasil disimpan.\n"
        "Silakan pilih menu:",
        reply_markup=MENU
    )
    return True


def device_setup_is_complete():
    return has_complete_device_ips(ROUTERS)
