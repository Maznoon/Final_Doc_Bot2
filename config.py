# config.py
import os

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///./test.db")
