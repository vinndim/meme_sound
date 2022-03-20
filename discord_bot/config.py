import yt_dlp
from dotenv import load_dotenv
import os

load_dotenv()
env_path = "../discord_bot/token.env"
load_dotenv(dotenv_path=env_path)

TOKEN = os.getenv("TOKEN")

yt_dlp.utils.bug_reports_message = lambda: 'yt_dlp error'
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}
ytdl = yt_dlp.YoutubeDL(ytdl_format_options)
FFMPEG_OPTIONS = {
    'before_options': '-nostdin',
    'options': '-vn'
}
