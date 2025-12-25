import os


class TelegramDataPROD:
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    ODIN_YEY_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))
    TREAD_MONITORING_ID = int(os.getenv("TREAD_MONITORING_ID"))

