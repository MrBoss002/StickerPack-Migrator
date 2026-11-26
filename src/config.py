import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN is missing! Please check your .env file.")
