import asyncio
import os
import yt_dlp
from youtubesearchpython.__future__ import VideosSearch

COOKIES_FILE = "cookies.txt"

class YouTubeAPI:
    async def get_details(self, query: str):
        try:
            results = VideosSearch(query, limit=1)
            result = (await results.next())["result"][0]
            return {
                "title": result.get("title", "Unknown"),
                "duration": result.get("duration", "00:00"),
                "link": result.get("link", query)
            }
        except:
            return None

    async def download(self, link: str, audio_only=True) -> str:
        loop = asyncio.get_running_loop()
        def run_ytdlp():
            if audio_only:
                ydl_opts = {
                    "format": "bestaudio/best",
                    "outtmpl": "downloads/%(title)s.%(ext)s",
                    "postprocessors": [{"key": "FFmpegExtractAudio","preferredcodec": "mp3"}],
                    "quiet": True, "noplaylist": True
                }
                if os.path.exists(COOKIES_FILE): ydl_opts["cookiefile"] = COOKIES_FILE
            else:
                ydl_opts = {
                    "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
                    "outtmpl": "downloads/%(title)s.%(ext)s",
                    "quiet": True, "noplaylist": True
                }
                if os.path.exists(COOKIES_FILE): ydl_opts["cookiefile"] = COOKIES_FILE

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=True)
                filename = ydl.prepare_filename(info)
                if audio_only:
                    return f"{os.path.splitext(filename)[0]}.mp3"
                return filename

        try:
            return await loop.run_in_executor(None, run_ytdlp)
        except Exception as e:
            print(f"DL Error: {e}")
            return None

yt = YouTubeAPI()

def time_to_seconds(time_str):
    if not time_str: return 0
    parts = time_str.split(':')
    if len(parts) == 2: return int(parts[0]) * 60 + int(parts[1])
    return 0
              
