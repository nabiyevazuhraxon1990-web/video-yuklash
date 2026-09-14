import os
from pathlib import Path
from dotenv import load_dotenv

# .env faylini yuklash
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# Bot sozlamalari
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Yuklab olinadigan fayllar papkasi
DOWNLOAD_DIR = BASE_DIR / os.getenv("DOWNLOAD_DIR", "downloads")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Maksimal fayl hajmi (Telegram Bot API limiti: 50MB)
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
