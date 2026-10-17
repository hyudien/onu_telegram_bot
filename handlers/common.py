import os

from telegram import ReplyKeyboardMarkup


ADMIN_ID = int(os.getenv("ADMIN_ID", "185653926"))

MENU = ReplyKeyboardMarkup(
    [
        ["📡 MANAGE OLT"],
        ["🌐 MANAGE MIKROTIK"]
    ],
    resize_keyboard=True
)
