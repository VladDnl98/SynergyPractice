import requests
import logging

from mvd_monitoring_2_3.tg.telegram_config import TelegramConfig

logger = logging.getLogger(__name__)


class TelegramClient:
    def __init__(self):
        self.base_url = f"https://api.telegram.org/bot{TelegramConfig.TOKEN}"

    def send_message(self, chat_id: int, message_thread_id: int | None, text: str):
        endpoint = f"{self.base_url}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        if message_thread_id:
            data["message_thread_id"] = message_thread_id

        logger.info(f"Отправка сообщения в чат {chat_id} (thread: {message_thread_id})")
        try:
            response = requests.post(endpoint, data=data, timeout=10)
            if response.ok:
                logger.info("Сообщение успешно отправлено")
            else:
                logger.error(f"Ошибка отправки: {response.status_code} {response.text}")
        except requests.RequestException as e:
            logger.error(f"Исключение при отправке в Telegram: {e}")