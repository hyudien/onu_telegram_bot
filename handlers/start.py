from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Update
)

from telegram.ext import ContextTypes

from data.users import (
    load_users,
    add_user
)
from handlers.common import ADMIN_ID, MENU
from handlers.device_setup import device_setup_is_complete, start_device_setup

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id
    fullname = update.effective_user.full_name

    print("USER_ID =", user_id)
    print("ALLOWED =", load_users())

    if user_id not in load_users():

        buttons = [
            [
                InlineKeyboardButton(
                    "✅ ACC",
                    callback_data=f"acc_{user_id}"
                ),
                InlineKeyboardButton(
                    "❌ TOLAK",
                    callback_data=f"reject_{user_id}"
                )
            ]
        ]

        await context.bot.send_message(
            ADMIN_ID,
            f"🔔 Permintaan akses bot\n\n"
            f"Nama : {fullname}\n"
            f"ID   : {user_id}",
            reply_markup=InlineKeyboardMarkup(
                buttons
            )
        )

        await update.message.reply_text(
            "📨 Permintaan akses telah dikirim ke admin.\n"
            "Silakan tunggu persetujuan."
        )

        return

    if user_id == ADMIN_ID and not device_setup_is_complete():
        await start_device_setup(update, context)
        return

    if not device_setup_is_complete():
        await update.message.reply_text(
            "Setup IP perangkat belum selesai. Hubungi admin terlebih dahulu."
        )
        return

    await update.message.reply_text(
        "Selamat datang di Bot ONU",
        reply_markup=MENU
    )


async def setup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in load_users():
        await update.message.reply_text("Akses belum disetujui.")
        return
    await start_device_setup(update, context)


async def access_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    data = query.data

    if data.startswith("acc_"):

        user_id = int(
            data.replace(
                "acc_",
                ""
            )
        )

        add_user(user_id)

        await query.edit_message_text(
            f"✅ User {user_id} disetujui"
        )

    elif data.startswith("reject_"):

        await query.edit_message_text(
            "❌ Ditolak"
        )
