import os


class TelegramConfig:
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    ODIN_YEY_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))
    THREAD_MVD_ID = int(os.getenv("THREAD_MVD_ID"))
    STORE_CHAT_ID = int(os.getenv("STORE_CHAT_ID"))
    ATC_BEZLIMIT_CHAT_ID = int(os.getenv("ATC_BEZLIMIT_CHAT_ID"))
    OPPERACIONIST_PD_CHAT_ID = int(os.getenv("OPPERACIONIST_PD_CHAT_ID"))
