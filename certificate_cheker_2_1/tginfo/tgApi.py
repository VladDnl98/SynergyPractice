import requests
from certificate_cheker_2_1.other.loger.logger_config import LoggerManager
from certificate_cheker_2_1.tginfo import dataTg
logger = LoggerManager.get_logger(__name__)

class TegApi:
    """
    Класс для взаимодействия с Telegram API.
    """

    def __init__(self):
        self.url = "https://api.telegram.org/bot"

    def send_message(self, channel_id, message_thread_id, text):
        """
        Отправляет текстовое сообщение в Telegram.
        :param channel_id: ID канала.
        :param message_thread_id: ID темы сообщения.
        :param text: Текст сообщения.
        :return: Ответ от API.
        """
        token = dataTg.TelegramDataPROD.TOKEN
        endpoint = f"{self.url}{token}/sendMessage"

        r = requests.post(endpoint, data={
            "chat_id": channel_id,
            "message_thread_id": message_thread_id,
            "text": text,
            "parse_mode": "Markdown"
        })
        if r.status_code == 200:
            logger.info(f"Сообщение отправлено: {text}")
        else:
            logger.error(f"Ошибка отправки сообщения: {r.text}")
        return r
