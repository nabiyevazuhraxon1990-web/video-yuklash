import asyncio
import os
import re
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
import yt_dlp

import shutil

try:
    if shutil.which("ffmpeg"):
        FFMPEG_EXE = shutil.which("ffmpeg")
    else:
        import imageio_ffmpeg
        FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_EXE = None

from config import DOWNLOAD_DIR, MAX_FILE_SIZE_BYTES, MAX_FILE_SIZE_MB

URL_REGEX = re.compile(
    r'^(https?://)?(www\.)?'
    r'([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
    r'(/[\w\-.~:/?#\[\]@!$&\'()*+,;=]*)?$',
    re.IGNORECASE
)

def is_valid_url(text: str) -> bool:
    """Tekst URL ekanligini tekshiradi."""
    if not text:
        return False
    return bool(URL_REGEX.match(text.strip()))

def get_video_info(url: str) -> Optional[Dict[str, Any]]:
    """Video haqidagi ma'lumotlarni (title, duration, thumbnail) yuklab olmasdan oladi."""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'extract_flat': False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return info
        except Exception:
            return None

def _download_video_sync(url: str) -> Dict[str, Any]:
    """Sinxron tarzda videoni yuklab oladi (yt-dlp orqali)."""
    file_id = str(uuid.uuid4())[:8]
    outtmpl = str(DOWNLOAD_DIR / f"{file_id}_%(title).50s.%(ext)s")

    ydl_opts = {
        'outtmpl': outtmpl,
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        # 50MB dan kichik eng yaxshi video va audioni tanlash
        'format': 'best[ext=mp4][filesize<?50M]/best[filesize<?50M]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
        'max_filesize': MAX_FILE_SIZE_BYTES,
    }
    if FFMPEG_EXE:
        ydl_opts['ffmpeg_location'] = FFMPEG_EXE

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

        # Agar format o'zgargan bo'lsa (masalan mkv yoki mp4) mavjud faylni topish
        downloaded_path = Path(filename)
        if not downloaded_path.exists():
            # outtmpl bazasida qidirish
            parent = downloaded_path.parent
            base_pattern = f"{file_id}_*"
            matches = list(parent.glob(base_pattern))
            if matches:
                downloaded_path = matches[0]

        filesize = downloaded_path.stat().st_size if downloaded_path.exists() else 0

        return {
            'file_path': str(downloaded_path),
            'title': info.get('title', 'Video'),
            'duration': info.get('duration', 0),
            'width': info.get('width'),
            'height': info.get('height'),
            'thumbnail': info.get('thumbnail'),
            'filesize': filesize,
        }

def _download_audio_sync(url: str) -> Dict[str, Any]:
    """Sinxron tarzda audioni yuklab oladi."""
    file_id = str(uuid.uuid4())[:8]
    outtmpl = str(DOWNLOAD_DIR / f"{file_id}_audio_%(title).50s.%(ext)s")

    ydl_opts = {
        'outtmpl': outtmpl,
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'format': 'bestaudio[filesize<?50M]/best[filesize<?50M]/best',
        'max_filesize': MAX_FILE_SIZE_BYTES,
    }
    if FFMPEG_EXE:
        ydl_opts['ffmpeg_location'] = FFMPEG_EXE

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

        downloaded_path = Path(filename)
        if not downloaded_path.exists():
            parent = downloaded_path.parent
            base_pattern = f"{file_id}_audio_*"
            matches = list(parent.glob(base_pattern))
            if matches:
                downloaded_path = matches[0]

        filesize = downloaded_path.stat().st_size if downloaded_path.exists() else 0

        return {
            'file_path': str(downloaded_path),
            'title': info.get('title', 'Audio'),
            'duration': info.get('duration', 0),
            'filesize': filesize,
        }

async def download_video(url: str) -> Dict[str, Any]:
    """Asinxron video yuklovchi funksiya."""
    return await asyncio.to_thread(_download_video_sync, url)

async def download_audio(url: str) -> Dict[str, Any]:
    """Asinxron audio yuklovchi funksiya."""
    return await asyncio.to_thread(_download_audio_sync, url)

def remove_file(file_path: Optional[str]) -> None:
    """Yuklangan vaqtinchalik faylni diskdan xavfsiz o'chiradi."""
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError:
            pass
