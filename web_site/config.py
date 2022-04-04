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
env_path = "../config.env"
load_dotenv(dotenv_path=env_path)

# retrieving keys and adding them to the project
# from the .env file through their key names
TOKEN = os.getenv("TOKEN")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

