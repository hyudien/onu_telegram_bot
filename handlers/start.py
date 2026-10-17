import os

from telegram import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Update
)

from telegram.ext import ContextTypes

from data.users import (
    load_users,
    add_user
)

ADMIN_ID = int(os.getenv("ADMIN_ID", "185653926"))

MENU = ReplyKeyboardMarkup(
    [
        ["📡 MANAGE OLT"],
        ["🌐 MANAGE MIKROTIK"]
    ],
    resize_keyboard=True
)

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

    await update.message.reply_text(
        "Selamat datang di Bot ONU",
        reply_markup=MENU
    )


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
