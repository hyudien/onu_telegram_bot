# ONU Telegram Bot

Bot Telegram untuk mengelola ONU/OLT ZTE dan router MikroTik.

## Persyaratan

- Python 3.10–3.12 (kode OLT menggunakan `telnetlib`, yang tidak tersedia di
  Python 3.13 dan lebih baru).
- Akses jaringan dari komputer bot ke OLT dan router MikroTik.
- Token bot Telegram dari BotFather.

## Instalasi

Linux/macOS:

```bash
cd /path/ke/onu_telegram_bot
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
```

Windows PowerShell:

```powershell
cd C:\path\ke\onu_telegram_bot
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

## Konfigurasi

Edit `.env`, lalu isi `BOT_TOKEN`, kredensial OLT, dan kredensial router yang
akan digunakan. Sesuaikan alamat dan port jika jaringan Anda berbeda.
`ADMIN_ID` adalah ID Telegram administrator yang menerima permintaan akses.
Jangan membagikan atau meng-commit `.env`.

Setelah token pernah dipublikasikan, cabut token lama melalui BotFather dan
gunakan token baru. Ganti juga kata sandi OLT/router yang pernah tersimpan di
source code.

## Menjalankan

Pastikan virtual environment aktif dan `.env` sudah diisi, lalu jalankan:

```bash
python bot.py
```

Bot berjalan dengan polling; hentikan dengan `Ctrl+C`. Perintah pada berkas
`test_*.py` dan beberapa skrip di `tools/` dapat terhubung ke perangkat nyata
atau mengubah konfigurasinya. Jangan jalankan sebagai tes instalasi.
