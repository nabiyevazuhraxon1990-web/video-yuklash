import asyncio
import html
import logging
import re
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatAction
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
import yt_dlp

from config import BOT_TOKEN, MAX_FILE_SIZE_BYTES
from downloader import download_video, remove_file

# Logging sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# URL qidirish uchun regex (matn ichidan havolani ajratib olish)
EXTRACT_URL_REGEX = re.compile(
    r'https?://(?:www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_+.~#?&/=]*'
)

dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    """/start komandasi uchun javob."""
    user_name = html.escape(message.from_user.first_name or "Foydalanuvchi")
    welcome_text = (
        f"Assalomu alaykum, <b>{user_name}</b>! 👋\n\n"
        "Men internetdan video yuklab beruvchi botman.\n\n"
        "📥 <b>Qo'llab-quvvatlanadigan platformalar:</b>\n"
        "• YouTube (Shorts & Videos)\n"
        "• Instagram (Reels, Post, IGTV)\n"
        "• TikTok (suv belgisiz)\n"
        "• Pinterest\n"
        "• Facebook, Twitter (X) va boshqalar\n\n"
        "🎬 Menga shunchaki video havolasini (link) yuboring!"
    )
    await message.answer(welcome_text)

@dp.message(Command("help"))
async def help_handler(message: Message) -> None:
    """/help komandasi uchun javob."""
    help_text = (
        "📖 <b>Botdan foydalanish bo'yicha qo'llanma:</b>\n\n"
        "1. Qaysidir ijtimoiy tarmoqdan (YouTube, Instagram, TikTok va h.k.) video havolasini nusxalang (kopirovat qiling).\n"
        "2. Ushbu botga havolani yuboring.\n"
        "3. Bot videoni avtomatik yuklab olib, sizga yuboradi.\n\n"
        "⚠️ <i>Eslatma: Telegram qoidalari bo'yicha botlar orqali faqat 50 MB gacha bo'lgan fayllarni yuborish mumkin.</i>"
    )
    await message.answer(help_text)

@dp.message(F.text)
async def video_link_handler(message: Message, bot: Bot) -> None:
    """Matn ichidagi havolani aniqlab videoni yuklab berish handler'i."""
    text = message.text or ""
    urls = EXTRACT_URL_REGEX.findall(text)

    if not urls:
        await message.reply(
            "Iltimos, to'g'ri video havolasini (URL) yuboring.\n"
            "Masalan: <code>https://www.instagram.com/reel/...</code> yoki YouTube/TikTok linki."
        )
        return

    url = urls[0]
    status_msg = await message.reply("⏳ <b>Video yuklab olinmoqda...</b>\nIltimos, biroz kuting.")
    
    # Telegramga "video yuborilmoqda..." harakatini ko'rsatish
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_VIDEO)

    video_data = None
    try:
        video_data = await download_video(url)
        file_path = video_data.get('file_path')
        filesize = video_data.get('filesize', 0)

        if not file_path or filesize == 0:
            await status_msg.edit_text("❌ Videoni yuklab olishning imkoni bo'lmadi. Havola yopiq yoki noto'g'ri bo'lishi mumkin.")
            return

        if filesize > MAX_FILE_SIZE_BYTES:
            size_mb = round(filesize / (1024 * 1024), 1)
            await status_msg.edit_text(
                f"⚠️ <b>Video hajmi juda katta ({size_mb} MB).</b>\n"
                f"Telegram botlari maksimal 50 MB gacha fayl yuborishi mumkin."
            )
            return

        # Videoni foydalanuvchiga jo'natish
        video_file = FSInputFile(file_path)
        caption_title = html.escape(video_data.get('title', 'Video')[:100])
        caption = f"🎬 <b>{caption_title}</b>\n\n📥 <i>Yuklab beruvchi bot orqali</i>"

        await message.answer_video(
            video=video_file,
            caption=caption,
            duration=video_data.get('duration'),
            width=video_data.get('width'),
            height=video_data.get('height'),
            supports_streaming=True
        )

        # Holat xabarini o'chirish
        await status_msg.delete()

    except yt_dlp.utils.DownloadError as e:
        logger.error(f"DownloadError: {e}")
        await status_msg.edit_text(
            "❌ <b>Xatolik yuz berdi:</b>\n"
            "Ushbu video himoyalangan, o'chirilgan yoki havolada xatolik bor."
        )
    except Exception as e:
        logger.exception(f"Kutilmagan xatolik: {e}")
        await status_msg.edit_text(
            "❌ <b>Kutilmagan xatolik yuz berdi.</b>\n"
            "Iltimos, birozdan so'ng qayta urinib ko'ring yoki boshqa havola yuboring."
        )
    finally:
        # Xotirani tejash: yuklangan vaqtinchalik faylni o'chirish
        if video_data and video_data.get('file_path'):
            remove_file(video_data['file_path'])

async def main() -> None:
    """Botni ishga tushirish funksiyasi."""
    if not BOT_TOKEN or "your-telegram-bot-token" in BOT_TOKEN:
        logger.error(
            "XATOLIK: .env faylida BOT_TOKEN ko'rsatilmagan!\n"
            "Iltimos, @BotFather dan token oling va uni .env fayliga kiriting."
        )
        sys.exit(1)

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    logger.info("Bot muvaffaqiyatli ishga tushirildi...")
    
    # Eski update'larni o'tkazib yuborish va pollingni boshlash
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
