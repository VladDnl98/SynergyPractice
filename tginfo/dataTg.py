import os
from dotenv import load_dotenv

load_dotenv()  # Загружает .env в os.environ

class TelegramDataPROD:
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    ODIN_YEY_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))
    THREAD_CERTIFICATE_ID = int(os.getenv("TELEGRAM_THREAD_ID"))