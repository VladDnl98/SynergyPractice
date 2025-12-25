import requests

from bill_monitoring_2_5.utils.logger import get_logger
from certificate_cheker_2_1.tg.tg_config import TelegramDataPROD


class TelegramClient:
    def __init__(self):
        self.url = "https://api.telegram.org/bot"
        self.logger = get_logger(self.__class__.__name__)

    def send_message(self, channel_id, message_thread_id, text):
        """
        Отправляет сообщение в Telegram с подробным логированием результата.
        """
        token = TelegramDataPROD.TOKEN
        endpoint = f"{self.url}{token}/sendMessage"

        self.logger.info(
            f"Отправка уведомления в Telegram → chat_id: {channel_id}, "
            f"thread_id: {message_thread_id}, длина текста: {len(text)} символов"
        )

        try:
            r = requests.post(
                endpoint,
                data={
                    "chat_id": channel_id,
                    "message_thread_id": message_thread_id,
                    "text": text,
                    "parse_mode": "Markdown"
                },
                timeout=10
            )

            if r.status_code == 200:
                response_json = r.json()
                if response_json.get("ok"):
                    self.logger.info("Уведомление успешно отправлено в Telegram")
                    return r
                else:
                    error_desc = response_json.get("description", "Неизвестная ошибка")
                    self.logger.error(f"Telegram API вернул ошибку: {error_desc}")
                    return r
            else:
                self.logger.error(
                    f"Ошибка HTTP при отправке в Telegram: {r.status_code} {r.text}"
                )
                return r

        except requests.RequestException as e:
            self.logger.error(f"Сетевая ошибка при отправке в Telegram: {e}")
            return None