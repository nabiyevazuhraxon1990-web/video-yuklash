# 📥 Telegram Video Yuklovchi Bot (Python)

Ushbu bot Telegram orqali yuborilgan har qanday ommaviy video havolasini (Instagram Reels, TikTok, YouTube Shorts/Video, Pinterest, Twitter/X, Facebook va boshqalar) qabul qilib, videoni eng yaxshi sifatda yuklab oladi va foydalanuvchiga jo'natadi.

---

## 🚀 Texnologiyalar

- **Python 3.10+**
- **[Aiogram 3](https://docs.aiogram.dev/)** — Asinxron va zamonaviy Telegram bot kutubxonasi
- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** — 1000 dan ortiq platformalardan video va audio yuklab oluvchi eng mukammal vosita
- **python-dotenv** — Xavfsiz muhit o'zgaruvchilari boshqaruvi

---

## 🛠 O'rnatish va Ishga tushirish

### 1. Virtual muhit (Virtual Environment) yaratish va faollashtirish:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Kerakli kutubxonalarni o'rnatish:
```bash
pip install -r requirements.txt
```

### 3. Telegram Bot Tokenini olish:
1. Telegramda [@BotFather](https://t.me/BotFather) botiga kiring.
2. `/newbot` buyrug'ini yuboring va botingizga nom hamda username bering.
3. BotFather sizga bergan `API TOKEN`ni nusxalang.

### 4. Sozlamalarni kiritish (.env):
`.env` faylini oching (yoki `.env.example` dan nusxa oling) va tokeningizni joylashtiring:
```bash
BOT_TOKEN=1234567890:ABCDEF-sizning-bot-tokeningiz
```

### 5. Botni ishga tushirish:
```bash
python3 bot.py
```

---

## 💡 Qo'shimcha tavsiyalar (FFmpeg)

Videolarning eng yuqori sifatli tasvir va audio oqimlarini qorishtirish uchun kompyuteringizda yoki serveringizda **ffmpeg** o'rnatilgan bo'lishi tavsiya etiladi:

- **macOS (Homebrew orqali):**
  ```bash
  brew install ffmpeg
  ```
- **Ubuntu / Debian Linux:**
  ```bash
  sudo apt update && sudo apt install -y ffmpeg
  ```
- **Windows:**
  [ffmpeg.org](https://ffmpeg.org/download.html) saytidan yuklab olinadi va PATH ga qo'shiladi.

---

## ⚠️ Telegram Cheklovlari

- Telegram Bot API cheklovi sababli botlar orqali jo'natiladigan bitta faylning hajmi maksimum **50 MB** bo'lishi mumkin. Agar video hajmi 50 MB dan oshsa, bot bu haqda foydalanuvchini ogohlantiradi.
- Server xotirasi (disk) to'lib qolmasligi uchun video foydalanuvchiga yuborilgach, yuklangan vaqtinchalik fayl avtomatik tarzda o'chirib yuboriladi.
