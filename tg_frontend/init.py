import os
from aiogram import Bot
from dotenv import load_dotenv

load_dotenv(dotenv_path="token.env")
BOT_TOKEN: str = os.getenv("TG_KEY") or ""
CREDENTIALS: str = os.getenv("GIGA_KEY") or ""
API_HOST = "127.0.0.1:8000"

if not BOT_TOKEN or not CREDENTIALS:
    raise ValueError("Missing one of the secret keys")

bot = Bot(token=BOT_TOKEN)

statuses = ("todo", "done")
