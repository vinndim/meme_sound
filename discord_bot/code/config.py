import yt_dlp
from dotenv import load_dotenv
import os

load_dotenv()
env_path = "../token.env"
load_dotenv(dotenv_path=env_path)

TOKEN = os.getenv("TOKEN")
