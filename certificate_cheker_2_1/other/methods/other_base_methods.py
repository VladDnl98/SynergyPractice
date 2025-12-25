
from certificate_cheker_2_1.other.loger.logger_config import LoggerManager
from certificate_cheker_2_1.tginfo.tgApi import TegApi

logger = LoggerManager.get_logger(__name__)

class OtherBaseMethods:
    @staticmethod
    def tg_send_message(chat_id, mt_id, m):
        """
        Отправляет сообщение в Telegram-чат.
        :param chat_id: ID чата.
        :param mt_id: ID темы сообщения.
        :param m: Сообщение или кортеж сообщений для отправки.
        """
        tg = TegApi()
        if isinstance(m, tuple):
            for msg in m:
                if msg:
                    response = tg.send_message(chat_id, mt_id, msg)
                    if response.status_code == 200:
                        logger.info(f"Сообщение отправлено в чат {chat_id}, тема {mt_id}: {msg}")
                    else:
                        logger.error(f"Ошибка отправки сообщения: {response.text}")
        else:
            response = tg.send_message(chat_id, mt_id, m)
            if response.status_code == 200:
                logger.info(f"Сообщение отправлено в чат {chat_id}, тема {mt_id}: {m}")
            else:
                logger.error(f"Ошибка отправки сообщения: {response.text}")
