# settings.py
# importing the load_dotenv from the python-dotenv module
import yt_dlp

from dotenv import load_dotenv

# using existing module to specify location of the .env file
from pathlib import Path
import os
import requests
from bs4 import BeautifulSoup

load_dotenv()
env_path = "../discord_bot/token.env"
print(env_path)
load_dotenv(dotenv_path=env_path)

# retrieving keys and adding them to the project
# from the .env file through their key names
TOKEN = os.getenv("TOKEN")
print(TOKEN)
yt_dlp.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}
FFMPEG_OPTIONS = {
    'before_options': '-nostdin',
    'options': '-vn'
}
ytdl = yt_dlp.YoutubeDL(ytdl_format_options)
