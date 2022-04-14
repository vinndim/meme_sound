from dotenv import load_dotenv
import os

env_path = os.path.abspath('..') + "/discord_bot/token.env"
load_dotenv(dotenv_path=env_path)
TOKEN = os.getenv("TOKEN")
