import asyncio
import subprocess
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    Update
)
from telegram.error import BadRequest

from telegram.ext import ContextTypes

from olt.zte import get_uncfg_onu
from olt.zte import (
    get_olt_config
)
from olt.get_onu_info import get_onu_info
from olt.change_pppoe import change_pppoe
from olt.find_onu_id import find_free_onu_id
from olt.register_onu import (
    register_onu,
    send_command,
    enable_remote_access
)
from olt.parser import parse_uncfg
from olt.delete_onu import delete_onu
from olt.change_package import change_package
from olt.change_onu import change_onu
from olt.get_status import (
    get_summary,
    get_problem_onus,
    get_pon_summary_live,
    get_pon_problem_customers_live,
    get_onu_wan_config,
    get_pon_info,
    connect_olt
)

from data.onu_types import ONU_TYPES
from data.modes import ONU_MODES
from data.vlans import VLANS
from data.packages import PACKAGES
from data.customer_db import (
    save_customer,
    find_customers,
    delete_customer,
    load_customers
)
from data.pons import PON_NAMES
from data.mt_profiles import MT_PROFILES

from mikrotik.status import get_status
from mikrotik.users import (
    get_online_users,
    get_offline_users,
    get_user
)
from mikrotik.actions import (
    add_user,
    delete_user,
    set_password,
    enable_user,
    disable_user,
    set_profile,
    set_comment,
    find_users
)
from data.mikrotik_routers import ROUTERS
from data.mt_profiles import MT_PROFILES

from datetime import datetime

async def menu_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    text = update.message.text
    step = context.user_data.get("step")
    print("TEXT =", text)
    print("STEP =", step)

    if text in [
        "📊 STATUS MT",
        "➕ TAMBAH USER",
        "🗑 HAPUS USER",
        "✏️ EDIT USER",
        "🔙 MIKROTIK MENU",
        "🏠 MENU UTAMA"
    ]:

        context.user_data["step"] = None
        step = None

    if text == "🔙 MIKROTIK MENU":

        context.user_data["step"] = None
        buttons = []

        for router in ROUTERS:
            buttons.append(
                [f"🌐 Router {router}"]
            )

        buttons.append(
            ["🏠 MENU UTAMA"]
        )

        await update.message.reply_text(
            "🌐 Pilih Router MikroTik",
            reply_markup=ReplyKeyboardMarkup(
                buttons,
                resize_keyboard=True
            )
        )

        return

    if step == "edit_comment_input":

        if step == "edit_profile_input":
            username = context.user_data["edit_user"]

        username = context.user_data[
            "edit_user"
        ]

        router = context.user_data.get(
            "router",
            "KWL"
        )

        hasil = set_comment(
            router,
            username,
            text
        )

        context.user_data["step"] = None

        if hasil:

            await update.message.reply_text(
                f"""
    ✅ COMMENT BERHASIL DIUBAH

    👤 User : {username}
    📝 Comment : {text}
    """
            )

        else:

            await update.message.reply_text(
                "❌ Gagal mengubah comment"
            )

        return

    if step == "edit_pass_input":

        username = context.user_data["edit_user"]

        router = context.user_data.get(
            "router",
            "KWL"
        )

        set_password(
            router,
            username,
            text
        )

        context.user_data["step"] = None

        await update.message.reply_text(
            "✅ Password berhasil diubah"
        )

        return

    if text == "✏️ EDIT USER":

        context.user_data["step"] = "mt_edit_user"

        await update.message.reply_text(
            "Masukkan Username PPPoE"
        )

        return

    if step == "mt_edit_user":

        router = context.user_data.get(
            "router",
            "KWL"
        )
        user = get_user(router, text)

        if not user:

            await update.message.reply_text(
                "❌ User tidak ditemukan"
            )
            return

        username = text

        context.user_data["edit_user"] = username

        disabled = user.get(
            "disabled",
            False
        )

        status = "YES" if disabled else "NO"

        buttons = [
            [
                InlineKeyboardButton(
                    "🔑 Password",
                    callback_data="edit_pass"
                )
            ],
            [
                InlineKeyboardButton(
                    "📦 Profile",
                    callback_data="edit_profile"
                )
            ],
            [
                InlineKeyboardButton(
                    "📝 Comment",
                    callback_data="edit_comment"
                )
            ],
            [
                InlineKeyboardButton(
                    "🚫 Disable",
                    callback_data="edit_disable"
                ),
                InlineKeyboardButton(
                    "✅ Enable",
                    callback_data="edit_enable"
                )
            ]
        ]

        context.user_data["step"] = None
        await update.message.reply_text(
            f"""
    👤 User : {user['name']}
    📦 Profile : {user.get('profile','-')}
    📝 Comment : {user.get('comment','-')}
    🚫 Disabled : {status}
    """,
            reply_markup=InlineKeyboardMarkup(
                buttons
            )
        )

        return

    if text == "🗑 HAPUS USER":

        context.user_data["step"] = None
        context.user_data["step"] = "mt_delete_user"

        await update.message.reply_text(
            "Masukkan Username PPPoE"
        )

        return

    if step == "mt_delete_user":

        hasil = find_users(
            context.user_data.get(
                "router",
                "KWL"
            ),
            text
        )

        if len(hasil) == 0:

            await update.message.reply_text(
                "❌ User tidak ditemukan"
            )

            return

        if len(hasil) > 1:

            context.user_data["delete_candidates"] = hasil
            context.user_data["step"] = "mt_delete_select"

            pesan = "🔍 Ditemukan beberapa user\n\n"

            for i, nama in enumerate(
                hasil,
                start=1
            ):
                pesan += f"{i}. {nama}\n"

            pesan += "\nBalas nomor user"

            await update.message.reply_text(
                pesan
            )

            return

        username = hasil[0]

        user = get_user(
            context.user_data.get(
                "router",
                "KWL"
            ),
            username
        )

        context.user_data["delete_user"] = username

        buttons = [
            [
                InlineKeyboardButton(
                    "✅ HAPUS",
                    callback_data="mt_delete_yes"
                )
            ],
            [
                InlineKeyboardButton(
                    "❌ BATAL",
                    callback_data="mt_delete_no"
                )
            ]
        ]

        context.user_data["step"] = None

        await update.message.reply_text(
            f"""
        🗑 KONFIRMASI HAPUS

        👤 User : {username}
        📦 Profile : {user.get('profile','-')}
        📝 Comment : {user.get('comment','-')}
        """,
            reply_markup=InlineKeyboardMarkup(
                buttons
            )
        )

        return

    if step == "mt_delete_select":

        router = context.user_data.get(
            "router",
            "KWL"
        )

        try:

            nomor = int(text)

            hasil = context.user_data[
                "delete_candidates"
            ]

            username = hasil[
                nomor - 1
            ]

        except:

            await update.message.reply_text(
                "Masukkan nomor yang benar"
            )

            return

        user = get_user(
            context.user_data.get(
                "router",
                "KWL"
            ),
            username
        )

        context.user_data["delete_user"] = username

        buttons = [
            [
                InlineKeyboardButton(
                    "✅ HAPUS",
                    callback_data="mt_delete_yes"
                )
            ],
            [
                InlineKeyboardButton(
                    "❌ BATAL",
                    callback_data="mt_delete_no"
                )
            ]
        ]

        context.user_data["step"] = None
        await update.message.reply_text(
            f"""
    🗑 KONFIRMASI HAPUS

    👤 User : {username}
    📦 Profile : {user.get('profile','-')}
    📝 Comment : {user.get('comment','-')}
    """,
            reply_markup=InlineKeyboardMarkup(
                buttons
            )
        )

        return

    if text == "➕ TAMBAH USER":

        context.user_data["step"] = None
        context.user_data["step"] = "mt_add_user"

        await update.message.reply_text(
            "Masukkan Username PPPoE"
        )

        return

    if step == "mt_add_user":

        context.user_data["mt_user"] = text
        context.user_data["step"] = "mt_add_pass"

        await update.message.reply_text(
            "Masukkan Password PPPoE"
        )
        return

    if step == "mt_add_pass":

        context.user_data["mt_pass"] = text

        buttons = []

        for p in MT_PROFILES:
            buttons.append([
                InlineKeyboardButton(
                    p,
                    callback_data=f"mt_profile_{p}"
                )
            ])

        await update.message.reply_text(
            "📦 Pilih Profile",
            reply_markup=InlineKeyboardMarkup(
                buttons
            )
        )

        return

    if step == "mt_add_comment":

        username = context.user_data["mt_user"]
        password = context.user_data["mt_pass"]
        profile = context.user_data["mt_profile"]
        comment = text

        router = context.user_data.get(
            "router",
            "KWL"
        )

        add_user(
            router,
            username,
            password,
            profile,
            comment
        )

        context.user_data["step"] = None

        await update.message.reply_text(
            f"""
    ✅ PPPoE BERHASIL DIBUAT

    👤 User : {username}
    🔑 Pass : {password}
    📦 Profile : {profile}
    📝 Comment : {comment}
    """
        )

        return

    if text == "📡 MANAGE OLT":

        context.user_data["step"] = None
        keyboard = ReplyKeyboardMarkup(
            [
                ["📊 STATUS", "🔍 CARI"],
                ["📝 REGISTRASI"],
                ["💾 SAVE CONFIG"],
                ["🔄 SYNC DB"],
                ["🏠 MENU UTAMA"]
            ],
            resize_keyboard=True
        )

        await update.message.reply_text(
            "📡 Menu OLT",
            reply_markup=keyboard
        )

        return

    if text == "🏠 MENU UTAMA":

        context.user_data["step"] = None
        keyboard = ReplyKeyboardMarkup(
            [
                ["📡 MANAGE OLT"],
                ["🌐 MANAGE MIKROTIK"]
            ],
            resize_keyboard=True
        )

        await update.message.reply_text(
            "Pilih Menu",
            reply_markup=keyboard
        )

        return

    if text == "🌐 MANAGE MIKROTIK":

        print("=== MASUK MENU MIKROTIK ===")

        context.user_data["step"] = None
        buttons = []

        for router in ROUTERS:
            buttons.append(
                [f"🌐 Router {router}"]
            )

        buttons.append(
            ["🏠 MENU UTAMA"]
        )

        await update.message.reply_text(
            "🌐 Pilih Router MikroTik",
            reply_markup=ReplyKeyboardMarkup(
                buttons,
                resize_keyboard=True
            )
        )

        return

    if text.startswith("🌐 Router "):

        context.user_data["step"] = None
        router = text.replace(
            "🌐 Router ",
            ""
        )

        context.user_data["router"] = router

        keyboard = ReplyKeyboardMarkup(
            [
                ["📊 STATUS MT"],
                ["➕ TAMBAH USER"],
                ["🗑 HAPUS USER"],
                ["✏️ EDIT USER"],
                ["🔙 MIKROTIK MENU"]
            ],
            resize_keyboard=True
        )

        await update.message.reply_text(
            f"🌐 Router {router}",
            reply_markup=keyboard
        )

        return

    if text == "📊 STATUS MT":

        context.user_data["step"] = None
        router = context.user_data.get(
            "router",
            "KWL"
        )

        data = get_status(router)

        pesan = f"""
    🌐 Router {router.upper()}

    👥 Total User : {data['total']}
    🟢 Online : {data['online']}
    🔴 Offline : {data['offline']}

    CPU : {data['cpu']}%
    RAM : {data['memory']} MB
    Uptime : {data['uptime']}
    """

        buttons = [
            [
                InlineKeyboardButton(
                    "🟢 USER ONLINE",
                    callback_data="mt_online"
                ),
                InlineKeyboardButton(
                    "🔴 USER OFFLINE",
                    callback_data="mt_offline"
                )
            ]
        ]

        await update.message.reply_text(
            pesan,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

        return

    if text in ["🔍 CARI", "📝 REGISTRASI", "📊 STATUS", "💾 SAVE CONFIG", "🔄 SYNC DB"]:
            context.user_data["step"] = None

    print("TEXT =", text)
    print("STEP =", context.user_data.get("step"))


    if step == "change_pppoe_user":

        context.user_data["new_pppoe_user"] = text
        context.user_data["step"] = "change_pppoe_pass"

        await update.message.reply_text(
            "Masukkan Password PPPoE baru"
        )

        return


    if step == "change_pppoe_pass":

        cust = context.user_data.get(
            "selected_customer"
        )

        user = context.user_data[
            "new_pppoe_user"
        ]

        passwd = text

        await update.message.reply_text(
            "⏳ Mengubah PPPoE..."
        )

        ok = change_pppoe(
            cust["pon"],
            cust["onu_id"],
            user,
            passwd,
            cust["vlan"]
        )

        if ok:

            cust["pppoe_user"] = user

            save_customer(cust)

            await update.message.reply_text(
                "✅ PPPoE berhasil diubah"
            )

        else:

            await update.message.reply_text(
                "❌ Gagal mengubah PPPoE"
            )

        context.user_data["step"] = None

        return

    if step == "change_onu_pass":

        cust = context.user_data["selected_customer"]

        cust["pppoe_pass"] = text.strip()

        save_customer(cust)

        context.user_data["step"] = None

        new_onu = context.user_data["new_onu"]

        await update.message.reply_text(
            "⏳ Mengganti ONU..."
        )

        ok = change_onu(
            cust,
            new_onu["sn"]
        )

        if ok:

            wan = get_onu_wan_config(
               cust["pon"],
               cust["onu_id"]
            )

            cust["sn"] = new_onu["sn"]

            if wan["pppoe_user"]:
               cust["pppoe_user"] = wan["pppoe_user"]

            if wan["pppoe_pass"]:
               cust["pppoe_pass"] = wan["pppoe_pass"]

            save_customer(cust)

            await update.message.reply_text(
                "⏳ Menunggu ONU online..."
            )

            await asyncio.sleep(10)

        else:

            await update.message.reply_text(
                "❌ Gagal mengganti ONU"
            )

        return

    if text == "🔍 CARI":

        context.user_data["step"] = "search"

        await update.message.reply_text(
            "Masukkan Nama / SN / PPPoE User"
        )

        return

    if step == "search":

        customers = find_customers(text)

        context.user_data["step"] = None

        if not customers:

            await update.message.reply_text(
                "Data tidak ditemukan"
            )

            return

        buttons = []

        for i, c in enumerate(customers[:10]):

            buttons.append([
                InlineKeyboardButton(
                    c.get("name", c["sn"]),
                    callback_data=f"cust_{i}"
                )
            ])

        context.user_data["search_result"] = customers

        await update.message.reply_text(
            "Pilih pelanggan",
            reply_markup=InlineKeyboardMarkup(
                buttons
            )
        )

        return

    if text == "📝 REGISTRASI":

        output = get_uncfg_onu()

        onu_list = parse_uncfg(output)

        context.user_data["uncfg_onu"] = onu_list

        buttons = []

        for i, onu in enumerate(onu_list):

            buttons.append([
                InlineKeyboardButton(
                    f"{onu['sn']} ({onu['pon']})",
                    callback_data=f"sn_{i}"
                )
            ])

        await update.message.reply_text(
            "Pilih ONU UNCFG",
            reply_markup=InlineKeyboardMarkup(
                buttons
            )
        )

    if context.user_data.get("step") == "customer_name":

        context.user_data["customer"] = text

        mode = context.user_data.get("mode", "")
        print("MODE DEBUG =", repr(mode))
        if mode.upper() == "BRIDGE":
            buttons = []
            for p in PACKAGES:
                buttons.append([
                    InlineKeyboardButton(
                        p,
                        callback_data=f"pkg_{PACKAGES[p]}"
                    )
                ])
            await update.message.reply_text(
                "Pilih Paket",
                reply_markup=InlineKeyboardMarkup(
                    buttons
                )
            )
            context.user_data["step"] = None

            return

        else:

            context.user_data["step"] = "pppoe_user"

            await update.message.reply_text(
                "Masukkan Usename PPPoE"
            )

            return

    if context.user_data.get("step") == "pppoe_user":

        context.user_data["pppoe_user"] = text
        context.user_data["step"] = "pppoe_pass"

        await update.message.reply_text(
            "Masukkan Password PPPoE"
        )

        return

    if context.user_data.get("step") == "pppoe_pass":

        context.user_data["pppoe_pass"] = text

        buttons = [
            [
                InlineKeyboardButton(
                    "☑ REGISTRASI",
                    callback_data="register"
                )
            ],
            [
                InlineKeyboardButton(
                    "✘ BATAL",
                     callback_data="cancel"
                )
            ]
         ]

        if context.user_data.get("mode", "").upper() == "PPPOE+BRIDGE":

            msg = (
                f"KONFIRMASI REGISTRASI\n\n"
                f"Nama : {context.user_data['customer']}\n"
                f"SN : {context.user_data['sn']}\n"
                f"PON : {context.user_data['pon']}\n"
                f"TYPE : {context.user_data['onu_type']}\n"
                f"MODE : {context.user_data['mode']}\n"
                f"VLAN PPP : {context.user_data['vlan']}\n"
                f"VLAN BRG : {context.user_data['bridge_vlan']}\n"
                f"PAKET PPP : {context.user_data['pppoe_package']}\n"
                f"PAKET BRG : {context.user_data['bridge_package']}\n"
                f"USER : {context.user_data['pppoe_user']}"
            )

        else:

            msg = (
                f"KONFIRMASI REGISTRASI\n\n"
                f"Nama : {context.user_data['customer']}\n"
                f"SN : {context.user_data['sn']}\n"
                f"PON : {context.user_data['pon']}\n"
                f"TYPE : {context.user_data['onu_type']}\n"
                f"MODE : {context.user_data['mode']}\n"
                f"VLAN : {context.user_data['vlan']}\n"
                f"PAKET : {context.user_data.get('package','')}\n"
                f"USER : {context.user_data['pppoe_user']}"
            )

        await update.message.reply_text(
            msg,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        context.user_data["step"] = None

        return

    if text == "📊 STATUS":

        s = get_summary()

        buttons = [
            [
                InlineKeyboardButton(
                    "📍 PER PON",
                    callback_data="perpon"
                )
            ]
        ]

        await update.message.reply_text(
            f"📊 STATUS OLT\n\n"
            f"🟢 Online     : {s['online']}\n"
            f"🔴 Offline    : {s['offline']}\n"
            f"📡 LOS        : {s['los']}\n"
            f"⚡ DyingGasp  : {s['dyinggasp']}\n\n"
            f"📊 Total ONU  : {s['total']}",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    if text == "🔄 SYNC DB":

        await update.message.reply_text(
            "⏳ Sync database..."
        )

        result = subprocess.run(
            ["python3", "sync_discovery.py"],
        )

        await update.message.reply_text(
            "⏳ Sinkron konfigurasi..."
        )

        subprocess.run(
            ["python3", "sync_pppoe.py"]
        )

        await update.message.reply_text(
            "✅ Sync selesai"
        )

        return

    if text == "💾 SAVE CONFIG":

        await update.message.reply_text(
            "⏳ Menyimpan konfigurasi OLT..."
        )

        try:

            tn = connect_olt()

            output = send_command(
                tn,
                "write",
                5
            )

            tn.close()

            await update.message.reply_text(
                "💾 Running-config berhasil ditulis ke flash"
            )

        except Exception as e:

            await update.message.reply_text(
                f"❌ Save gagal\n\n{e}"
            )

        return

async def callback_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    data = query.data

    if query.data == "edit_comment":

        context.user_data[
            "step"
        ] = "edit_comment_input"

        await query.message.reply_text(
            "Masukkan Comment Baru"
        )

        return

    if query.data == "edit_profile":

        buttons = []

        for p in MT_PROFILES:

            buttons.append([
                InlineKeyboardButton(
                    p,
                    callback_data=f"set_profile_{p}"
                )
            ])

        await query.message.reply_text(
            "📦 Pilih Profile Baru",
            reply_markup=InlineKeyboardMarkup(
                buttons
            )
        )

        return

    if query.data.startswith(
        "set_profile_"
    ):

        profile = query.data.replace(
            "set_profile_",
            ""
        )

        username = context.user_data[
            "edit_user"
        ]

        router = context.user_data.get(
            "router",
            "KWL"
        )

        hasil = set_profile(
            router,
            username,
            profile
        )

        if hasil:

            await query.edit_message_text(
                f"""
    ✅ PROFILE BERHASIL DIUBAH

    👤 User : {username}
    📦 Profile : {profile}
    """
            )

        else:

            await query.edit_message_text(
                "❌ Gagal mengubah profile"
            )

        return

    if query.data == "edit_disable":

        username = context.user_data["edit_user"]

        router = context.user_data.get(
            "router",
            "KWL"
        )

        disable_user(
            router,
            username
        )

        await query.answer(
            "User Disabled"
        )

        await query.edit_message_text(
            f"🚫 {username} berhasil di-disable"
        )

        return

    if query.data == "edit_enable":

        username = context.user_data["edit_user"]

        router = context.user_data.get("router", "KWL")

        enable_user(
            router,
            username
        )

        await query.answer(
            "User Enabled"
        )

        await query.edit_message_text(
            f"✅ {username} berhasil di-enable"
        )

        return

    if query.data == "edit_pass":

        context.user_data["step"] = "edit_pass_input"

        await query.message.reply_text(
            "Masukkan Password Baru"
        )

        return

    if query.data == "mt_delete_yes":

        username = context.user_data.get(
            "delete_user"
        )

        router = context.user_data.get(
            "router",
            "KWL"
        )

        hasil = delete_user(
            router,
            username
        )

        if hasil:

            await query.edit_message_text(
                f"✅ User {username} berhasil dihapus"
            )

        else:

            await query.edit_message_text(
                "❌ Gagal menghapus user"
            )

        return

    if query.data == "mt_delete_no":

        await query.edit_message_text(
            "❌ Dibatalkan"
        )

        return

    if query.data.startswith("mt_profile_"):

        profile = query.data.replace(
            "mt_profile_",
            ""
        )

        context.user_data["mt_profile"] = profile
        context.user_data["step"] = "mt_add_comment"

        await query.edit_message_text(
            f"📦 Profile : {profile}"
        )

        await query.message.reply_text(
            "Masukkan Comment"
        )

        return

    if query.data == "mt_offline":

        router = context.user_data.get(
            "router",
            "KWL"
        )

        users = get_offline_users(router)

        text = (
            f"🔴 USER OFFLINE\n\n"
            f"Total : {len(users)}\n\n"
        )

        for i, user in enumerate(users[:100], start=1):
            text += f"{i}. {user}\n"

        text += (
            f"\n\n🕒 Refresh : "
            f"{datetime.now().strftime('%H:%M:%S')}"
        )

        buttons =[
            [
                InlineKeyboardButton(
                    "🔄 REFRESH",
                    callback_data="mt_offline_refresh"
                ),
                InlineKeyboardButton(
                    "🔙 KEMBALI",
                    callback_data="mt_back"
                )
            ]
        ]

        await query.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    if query.data == "mt_offline_refresh":

        router = context.user_data.get(
            "router",
            "KWL"
        )

        users = get_offline_users(router)

        text = (
            f"🔴 USER OFFLINE\n\n"
            f"Total : {len(users)}\n\n"
        )

        for i, user in enumerate(users[:100], start=1):
            text += f"{i}. {user}\n"

        text += (
            f"\n\n🕒 Refresh : "
            f"{datetime.now().strftime('%H:%M:%S')}"
        )

        buttons = [
            [
                InlineKeyboardButton(
                "🔄 REFRESH",
                callback_data="mt_offline_refresh"
                ),
                InlineKeyboardButton(
                    "🔙 KEMBALI",
                    callback_data="mt_back"
                )
            ]
        ]

        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

        return

    if query.data == "mt_back":

        keyboard = ReplyKeyboardMarkup(
            [
                ["📊 STATUS MT"],
                ["➕ TAMBAH PPPoE"],
                ["🗑 HAPUS PPPoE"],
                ["✏️ EDIT PPPoE"],
                ["🔙 MIKROTIK MENU"]
            ],
            resize_keyboard=True
        )

        await query.message.reply_text(
            "🌐 Router Menu",
            reply_markup=keyboard
        )

        return

    if query.data == "mt_online":

        router = context.user_data.get(
            "router",
            "KWL"
        )

        users = get_online_users(router)

        text = "🟢 USER ONLINE\n\n"

        for i, user in enumerate(users[:50], start=1):
            text += f"{i}. {user}\n"

        text += f"\nTotal : {len(users)}"

        await query.message.reply_text(
            text
        )

        return

    if data.startswith("sn_"):

        idx = int(
            data.split("_")[1]
        )

        onu_list = context.user_data.get(
            "uncfg_onu",
            []
        )

        if idx >= len(onu_list):

            await query.answer(
                "Data ONU tidak ditemukan",
                show_alert=True
            )
            return

        onu = onu_list[idx]

        context.user_data["sn"] = onu["sn"]
        context.user_data["pon"] = onu["pon"]

        buttons = []

        for t in ONU_TYPES:

            buttons.append([
                InlineKeyboardButton(
                    t,
                    callback_data=f"type_{t}"
                )
            ])

        await query.edit_message_text(
            f"SN : {onu['sn']}\n"
            f"PON : {onu['pon']}\n\n"
            f"Pilih ONU Type",
            reply_markup=InlineKeyboardMarkup(
                buttons
            )
        )

    elif data.startswith("type_"):

        onu_type = data.replace(
            "type_",
            ""
        )

        context.user_data["onu_type"] = onu_type

        buttons = []

        for mode in ONU_MODES:

            buttons.append([
               InlineKeyboardButton(
                   mode,
                   callback_data=f"mode_{mode}"
               )
            ])

        await query.edit_message_text(
            f"SN   : {context.user_data['sn']}\n"
            f"PON  : {context.user_data['pon']}\n"
            f"TYPE : {onu_type}"
            f"Pilih Mode",
            reply_markup=InlineKeyboardMarkup(
                buttons
            )
        )

    elif data.startswith("mode_"):

        mode = data.replace(
            "mode_",
            ""
        )

        context.user_data["mode"] = mode
        buttons = []

        if mode.upper() == "BRIDGE":

            buttons = [
                [
                    InlineKeyboardButton(
                        "BRG(30)",
                        callback_data="bridge_vlan_30"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "BRG(44)",
                        callback_data="bridge_vlan_44"
                    )
                ]
            ]

        else:

            for vlan_id, vlan_info in VLANS.items():

                buttons.append([
                    InlineKeyboardButton(
                        f"{vlan_info['name']}({vlan_id})",
                        callback_data=f"vlan_{vlan_id}"
                    )
                ])

        await query.edit_message_text(
            f"SN   : {context.user_data['sn']}\n"
            f"PON  : {context.user_data['pon']}\n"
            f"TYPE : {context.user_data['onu_type']}\n"
            f"MODE : {mode}"
            f"Pilih VLAN",
            reply_markup=InlineKeyboardMarkup(
                buttons
            )
        )

    elif data.startswith("vlan_"):

        vlan = data.replace(
            "vlan_",
            ""
        )

        context.user_data["vlan"] = vlan

        mode = context.user_data.get(
            "mode",
            ""
        )

        if mode.upper() == "PPPOE+BRIDGE":

            buttons = [
                [
                    InlineKeyboardButton(
                        "BRG(30)",
                        callback_data="bridge_vlan_30"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "BRG(44)",
                        callback_data="bridge_vlan_44"
                    )
                ]
            ]

            await query.edit_message_text(
                f"VLAN PPPoE : {vlan}\n\n"
                f"Pilih VLAN Bridge",
                reply_markup=InlineKeyboardMarkup(
                    buttons
                )
            )

            return
        buttons = []

        for name, profile in PACKAGES.items():
            buttons.append([
              InlineKeyboardButton(
                  name,
                  callback_data=f"pkg_{profile}"
               )
            ])

        await query.edit_message_text(
            f"SN   : {context.user_data['sn']}\n"
            f"PON  : {context.user_data['pon']}\n"
            f"TYPE : {context.user_data['onu_type']}\n"
            f"MODE : {context.user_data['mode']}\n"
            f"VLAN : {vlan}"
            f"Pilih Paket",
            reply_markup=InlineKeyboardMarkup(
                buttons
            )
        )

    elif data.startswith("bridge_vlan_"):

        bridge_vlan = data.replace(
            "bridge_vlan_",
            ""
        )

        context.user_data["bridge_vlan"] = bridge_vlan

        buttons = []

        for name, profile in PACKAGES.items():
            buttons.append([
                InlineKeyboardButton(
                    name,
                    callback_data=f"ppp_pkg_{profile}"
                )
            ])

        await query.edit_message_text(
            f"VLAN PPPoE : {context.user_data['vlan']}\n"
            f"VLAN Bridge: {bridge_vlan}\n\n"
            f"Pilih Paket",
            reply_markup=InlineKeyboardMarkup(
                buttons
            )
        )

        return

    elif data.startswith("ppp_pkg_"):

        package = data.replace(
            "ppp_pkg_",
            ""
        )

        context.user_data["pppoe_package"] = package

        buttons = []

        for name, profile in PACKAGES.items():
            buttons.append([
                InlineKeyboardButton(
                    name,
                    callback_data=f"brg_pkg_{profile}"
                )
            ])

        await query.edit_message_text(
            f"PAKET PPPoE : {package}\n\n"
            f"Pilih Paket Bridge",
            reply_markup=InlineKeyboardMarkup(
                buttons
            )
        )

        return

    elif data.startswith("brg_pkg_"):

        package = data.replace(
            "brg_pkg_",
            ""
        )

        context.user_data["bridge_package"] = package

        context.user_data["step"] = "customer_name"

        await query.edit_message_text(
            f"PAKET PPPoE  : {context.user_data['pppoe_package']}\n"
            f"PAKET BRIDGE : {package}\n\n"
            f"Masukkan nama customer:"
        )

        return

    elif data.startswith("pkg_"):

        package = data.replace(
            "pkg_",
            ""
        )

        context.user_data["package"] = package

        mode = context.user_data.get(
            "mode",
            ""
        )

        if mode.upper() == "BRIDGE":

            buttons = [
                [
                    InlineKeyboardButton(
                        "☑ REGISTRASI",
                        callback_data="register"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "✘ BATAL",
                        callback_data="cancel"
                    )
                ]
            ]

            await query.edit_message_text(
                f"KONFIRMASI REGISTRASI\n\n"
                f"Nama : {context.user_data['customer']}\n"
                f"SN : {context.user_data['sn']}\n"
                f"PON : {context.user_data['pon']}\n"
                f"TYPE : {context.user_data['onu_type']}\n"
                f"MODE : {context.user_data['mode']}\n"
                f"VLAN : {context.user_data['vlan']}\n"
                f"PAKET : {package}",
                reply_markup=InlineKeyboardMarkup(
                    buttons
                )
            )

            return

        await query.edit_message_text(
            f"SN     : {context.user_data['sn']}\n"
            f"PON    : {context.user_data['pon']}\n"
            f"TYPE   : {context.user_data['onu_type']}\n"
            f"MODE   : {context.user_data['mode']}\n"
            f"VLAN   : {context.user_data['vlan']}\n"
            f"PAKET  : {package}\n\n"
            f"Ketik Nama Pelanggan"
        )

        context.user_data["step"] = "customer_name"

    elif data == "cancel":

        context.user_data.clear()

        await query.edit_message_text(
            "Registrasi dibatalkan"
        )

    elif data == "register":

        await query.edit_message_text(
            "⌛ Sedang registrasi ONU..."
        )

        cfg = get_olt_config(
            context.user_data["pon"]
        )

        onu_id = find_free_onu_id(cfg)

        print("ONU ID =", onu_id)

        result = register_onu(
            context.user_data,
            onu_id
        )

        if result:

            save_customer({
                "name": context.user_data["customer"],
                "pon":context.user_data["pon"],
                "onu_id": str(onu_id),
                "sn": context.user_data["sn"],

                "vlan": str(context.user_data["vlan"]),
                "package": context.user_data.get(
                    "package",
                    context.user_data.get("pppoe_package", "")),

                "pppoe_package": context.user_data.get("pppoe_package", ""),
                "bridge_package": context.user_data.get("bridge_package", ""),

                "pppoe_user": context.user_data.get("pppoe_user", ""),
                "pppoe_pass": context.user_data.get("pppoe_pass", ""),

                "onu_type": context.user_data["onu_type"],
                "mode": context.user_data["mode"],

                "bridge_vlan": context.user_data.get(
                    "bridge_vlan",
                    ""
                ),
                "created_at": datetime.now().isoformat()
            })

            user = context.user_data.get(
                "pppoe_user",
                "-"
            )


            await query.message.reply_text(
                f"✅ Registrasi berhasil\n\n"
                f"ONU ID : {str(onu_id)}\n"
                f"SN     : {context.user_data['sn']}\n"
                f"PON    : {context.user_data['pon']}\n"
                f"NAMA   : {context.user_data['customer']}\n"
                f"PPP    : {context.user_data.get('pppoe_package','')}\n"
                f"BRG    : {context.user_data.get('bridge_package','')}\n"
                f"VLAN P : {context.user_data['vlan']}\n"
                f"VLAN B : {context.user_data.get('bridge','')}\n"
                f"USER   : {user}\n"
            )

        else:

            await query.message.reply_text(
                "❌ Registrasi gagal"
            )

        print(context.user_data)

    elif data.startswith("cust_"):
        print("DETAIL SENT")

        idx = int(
            data.replace("cust_", "")
        )

        cust = context.user_data[
            "search_result"
        ][idx]

        context.user_data[
            "selected_customer"
        ] = cust

        print("SHOW DETAIL")

        buttons = [
            [
                InlineKeyboardButton(
                    "🔄 REBOOT",
                    callback_data="reboot"
                ),
                 InlineKeyboardButton(
                    "🔑 PPPOE",
                    callback_data="pppoe"
                ),
            ],
            [
                 InlineKeyboardButton(
                    "📡 REDAMAN",
                    callback_data="info"
                ),
                InlineKeyboardButton(
                    "🔄 CHANGE ONU",
                    callback_data="change_onu"
                )
            ],
            [
                 InlineKeyboardButton(
                    "🗑 DELETE",
                    callback_data="delete_onu"
                 ),
                 InlineKeyboardButton(
                    "⬆️ UBAH PAKET",
                     callback_data="change_package"
                 )

            ],
            [
                 InlineKeyboardButton(
                     "🌐 Remote",
                     callback_data="enable_remote"
                 )
            ],
        ]

        if cust.get("mode", "").upper() == "PPPOE+BRIDGE":

            msg = (
                f"NAMA      : {cust.get('name','-')}\n"
                f"USER      : {cust.get('pppoe_user','-')}\n"
                f"SN        : {cust.get('sn','-')}\n"
                f"PON       : {cust.get('pon','-')}\n"
                f"ONU       : {cust.get('onu_id','-')}\n"
                f"MODE      : {cust.get('mode','-')}\n\n"

                f"VLAN PPP  : {cust.get('vlan','-')}\n"
                f"VLAN BRG  : {cust.get('bridge_vlan','-')}\n\n"

                f"PKG PPP   : {cust.get('pppoe_package','-')}\n"
                f"PKG BRG   : {cust.get('bridge_package','-')}"
            )

        else:

            msg = (
                f"NAMA  : {cust.get('name','-')}\n"
                f"USER  : {cust.get('pppoe_user','-')}\n"
                f"SN    : {cust.get('sn','-')}\n"
                f"PON   : {cust.get('pon','-')}\n"
                f"ONU   : {cust.get('onu_id','-')}\n"
                f"MODE  : {cust.get('mode','-')}\n"
                f"VLAN  : {cust.get('vlan','-')}\n"
                f"PAKET : {cust.get('package','-')}"
            )

        await query.edit_message_text(
            msg,
            reply_markup=InlineKeyboardMarkup(
                buttons
            )
        )
        print("DETAIL SENT")

    elif data == "enable_remote":

        cust = context.user_data.get(
            "selected_customer"
        )

        await query.edit_message_text(
            "⏳ Mengaktifkan Remote Access..."
        )

        try:

            tn = connect_olt()

            send_command(
                tn,
                "conf t"
            )

            send_command(
                tn,
                f"pon-onu-mng gpon-onu_{cust['pon']}:{cust['onu_id']}"
            )

            enable_remote_access(tn)

            send_command(tn, "end")

            tn.close()

            await query.message.reply_text(
                "✅ Remote Access berhasil diaktifkan"
            )

        except Exception as e:

            await query.message.reply_text(
                f"❌ Gagal\n\n{e}"
            )

    elif data == "reboot":

        cust = context.user_data.get(
            "selected_customer"
        )

        buttons = [
            [
                InlineKeyboardButton(
                    "✅ YA",
                    callback_data="reboot_yes"
                ),
                InlineKeyboardButton(
                    "❌ TIDAK",
                    callback_data="cancel"
                )
            ]
        ]

        await query.edit_message_text(
            f"Reboot ONU?\n\n"
            f"{cust.get('name','-')}",
            reply_markup=InlineKeyboardMarkup(
                buttons
            )
        )

    elif data == "reboot_yes":

        cust = context.user_data[
            "selected_customer"
        ]

        await query.edit_message_text(
            "⏳ Sedang reboot ONU..."
        )

        from olt.reboot_onu import reboot_onu

        reboot_onu(
            cust["pon"],
            cust["onu_id"]
        )

        await query.message.reply_text(
            f"✅ ONU berhasil direboot\n\n"
            f"{cust['name']}"
        )

    elif data == "cancel":

        await query.edit_message_text(
            "Dibatalkan"
        )

    elif data == "pppoe":

        context.user_data["step"] = "change_pppoe_user"

        await query.message.reply_text(
            "Masukkan Username PPPoE baru"
        )

    elif data == "info":

        cust = context.user_data.get(
            "selected_customer"
        )

        info = get_onu_info(
            cust["pon"],
            cust["onu_id"]
        )

        await query.message.reply_text(
            f"ℹ️ INFO ONU\n\n"
            f"📡 RX ONU : {info['onu_rx']} dBm\n"
            f"📡 TX ONU : {info['onu_tx']} dBm\n\n"
            f"📉 LOSS UP : {info['loss_up']} dB\n"
            f"📉 LOSS DOWN : {info['loss_down']} dB"
        )

    elif data == "change_package":

        cust = context.user_data.get(
            "selected_customer"
        )
        print("CUSTOMER DEBUG =", cust)

        buttons = []

        for name, profile in PACKAGES.items():

            buttons.append([
                InlineKeyboardButton(
                    name,
                    callback_data=f"pkgchg_{profile}"
                )
            ])

        await query.edit_message_text(
            "Pilih Paket Baru",
            reply_markup=InlineKeyboardMarkup(
                buttons
            )
        )

    elif data.startswith("pkgchg_"):

        package = data.replace(
            "pkgchg_",
            ""
        )

        cust = context.user_data.get(
            "selected_customer"
        )

        await query.edit_message_text(
            "⏳ Mengubah Paket..."
        )

        if cust.get("mode", "").upper() == "PPPOE+BRIDGE":

            ok = change_package(
                cust["pon"],
                cust["onu_id"],
                package,
                cust.get("bridge_package")
            )
            cust["pppoe_package"] = package
            cust["package"] = package

        else:
            ok = change_package(
                cust["pon"],
                cust["onu_id"],
                package
            )
            cust["package"] = package

        if ok:

            save_customer(cust)

            await query.message.reply_text(
            f"✅ Paket berhasil diubah\n\n"
            f"Paket Baru : {package}"
            )

        else:

            await query.message.reply_text(
                "❌ Gagal mengubah paket"
            )

    elif data == "delete_onu":

        cust = context.user_data.get(
            "selected_customer"
        )

        buttons = [
            [
                InlineKeyboardButton(
                    "✅ YA",
                    callback_data="delete_confirm"
                ),
                InlineKeyboardButton(
                    "❌ BATAL",
                    callback_data="cancel"
                )
            ]
        ]

        await query.message.reply_text(
            f"⚠️ Hapus ONU\n\n"
            f"Nama : {cust.get('name','-')}\n"
            f"PON  : {cust['pon']}\n"
            f"ONU  : {cust['onu_id']}\n\n"
            f"Yakin?",
            reply_markup=InlineKeyboardMarkup(
                 buttons
            )
        )

        return

    elif data == "delete_confirm":

        cust = context.user_data.get(
            "selected_customer"
        )
        await query.message.reply_text(
            "⏳ Menghapus ONU..."
        )

        ok = delete_onu(
            cust["pon"],
            cust["onu_id"]
        )

        if ok:

            delete_customer(
                cust["pon"],
                cust["onu_id"]
            )

            await query.message.reply_text(
                "✅ ONU berhasil dihapus"
            )

        else:

            await query.message.reply_text(
                "❌ Gagal menghapus ONU"
            )

        return

    elif data == "change_onu":

        onu_list = parse_uncfg(
            get_uncfg_onu()
        )

        context.user_data[
            "change_onu_list"
        ] = onu_list

        buttons = []

        for i, onu in enumerate(onu_list):

            buttons.append([
                InlineKeyboardButton(
                    f"{onu['sn']} ({onu['pon']})",
                    callback_data=f"newonu_{i}"
                )
            ])

        await query.edit_message_text(
            "Pilih ONU Baru",
            reply_markup=InlineKeyboardMarkup(
                buttons
            )
        )

    elif data.startswith("newonu_"):

        idx = int(
            data.replace(
                "newonu_",
                ""
            )
        )

        onu = context.user_data[
            "change_onu_list"
        ][idx]

        context.user_data[
            "new_onu"
        ] = onu

        cust = context.user_data[
            "selected_customer"
        ]

        buttons = [
            [
                InlineKeyboardButton(
                    "✅ LANJUTKAN",
                    callback_data="change_onu_yes"
                )
            ],
            [
                InlineKeyboardButton(
                    "❌ BATAL",
                    callback_data="cancel"
                )
            ]
        ]

        await query.edit_message_text(
            f"CHANGE ONU\n\n"
            f"Nama    : {cust['name']}\n"
            f"PON     : {cust['pon']}\n"
            f"ONU ID  : {cust['onu_id']}\n\n"
            f"SN Lama : {cust['sn']}\n"
            f"SN Baru : {onu['sn']}",
            reply_markup=InlineKeyboardMarkup(
                buttons
            )
        )

    elif data == "change_onu_yes":

        cust = context.user_data[
            "selected_customer"
        ]

        new_onu = context.user_data[
            "new_onu"
        ]

        if not cust.get("pppoe_pass"):

            context.user_data["step"] = "change_onu_pass"

            await query.message.reply_text(
                f"PPPoE User : {cust['pppoe_user']}\n\n"
                f"Masukkan PPPoE Password:"
            )

            return

        await query.edit_message_text(
            "⏳ Mengganti ONU..."
        )

        ok = change_onu(
            cust,
            new_onu["sn"]
        )

        if ok:

            cust["sn"] = new_onu["sn"]

            save_customer(cust)

            await query.message.reply_text(
                f"✅ ONU berhasil diganti\n\n"
                f"ONU ID : {cust['onu_id']}\n"
                f"SN Baru : {new_onu['sn']}"
            )

        else:

            await query.message.reply_text(
                "❌ Gagal mengganti ONU"
            )

        if not cust.get("onu_type"):

            context.user_data["step"] = "change_onu_type"

            await query.message.reply_text(
                "Masukkan ONU Type:\n\n"
                "Contoh:\n"
                "ALL-ONT\n"
                "ALL-ONU(5G)\n"
                "OPEN_HUAWEI"
            )

            return



    elif data == "perpon":

        buttons = []

        row = []

        for pon, nama in PON_NAMES.items():

            row.append(
                InlineKeyboardButton(
                    nama,
                    callback_data=f"pon_{pon}"
                )
            )

            if len(row) == 2:
                buttons.append(row)
                row = []

        if row:
            buttons.append(row)

        await query.edit_message_text(
            "📍 Pilih PON",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

        return

    elif (
         data.startswith("pon_")
         or data.startswith("refresh_")
    ):

        if data.startswith("refresh"):
            pon = data.replace(
                "refresh_",
                ""
            )

        else:
           pon = data.replace(
               "pon_",
               ""
           )

        data = get_pon_info(pon)

        summary = get_pon_summary_live(data)

        problems = get_pon_problem_customers_live(data, pon)

        nama_pon = PON_NAMES.get(pon, pon)

        msg = (
            f"📡 {nama_pon}\n"
            f"({pon})\n\n"
            f"🟢 Online : {summary['online']}\n"
            f"🔴 Offline : {summary['offline']}\n"
            f"📊 Total : {summary['total']}\n\n"
        )

        if problems:

            msg += "🔴 ONU BERMASALAH\n\n"

            for p in problems:

                msg += (
                    f"{p['onu_id']} - {p['name']}\n"
                    f"({p['status'].upper()})\n\n"
                )

        else:

            msg += "✅ Semua ONU Online"

        buttons = [
            [
                InlineKeyboardButton(
                    "🔄 REFRESH",
                    callback_data=f"refresh_{pon}"
                )
            ],
            [
                InlineKeyboardButton(
                    "◀️ KEMBALI",
                    callback_data="perpon"
                )
            ]
        ]

        try:
           await query.edit_message_text(
               msg,
               reply_markup=InlineKeyboardMarkup(buttons)
           )

        except BadRequest:
            pass

        return
