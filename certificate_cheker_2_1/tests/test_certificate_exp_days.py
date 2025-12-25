import pytest
from datetime import datetime
from certificate_cheker_2_1.other.loger.logger_config import LoggerManager
from certificate_cheker_2_1.other.methods.check_certificate_methods import CheckCertificateMethods
from certificate_cheker_2_1.other.utils.urls import OtherNormalUrls
from certificate_cheker_2_1.tginfo.dataTg import TelegramDataPROD

logger = LoggerManager.get_logger(__name__)

class TestNormalCertificate:
    """
    Класс для тестирования сертификатов рабочих сайтов.
    """

    @pytest.mark.parametrize("url", [
        OtherNormalUrls.RUS_IN_COM_URL,
        OtherNormalUrls.BEZLIMIT_RU,
        OtherNormalUrls.BRITE_TELE_RU_URL,
        OtherNormalUrls.TELECOM_ALFA_RU_URL
        # При необходимости раскомментируйте другие URL
    ])
    def test_check_url(self, url):
        """
        Проверяет сертификат для одного URL-адреса и выполняет все запланированные проверки.
        При проблемах с доступом или сертификатом — отправляет предупреждение в Telegram.
        """
        logger.info(f"Начинаем проверку сертификата для URL: {url}")

        d, on = CheckCertificateMethods.check_certificate_date(url)

        # Если не удалось получить данные сертификата — отправляем предупреждение
        if d is None or on is None:
            warning_msg = (
                f"⚠️ *Не удалось проверить SSL-сертификат* для сайта `{url}`\n\n"
                f"Возможные причины:\n"
                f"• Сайт недоступен по HTTPS\n"
                f"• Проблема с SSL-handshake\n"
                f"• Сертификат отсутствует или повреждён\n\n"
                f"Рекомендуется проверить доступность сайта вручную."
            )
            CheckCertificateMethods.tg_send_message(
                chat_id=TelegramDataPROD.ODIN_YEY_CHAT_ID,
                mt_id=TelegramDataPROD.THREAD_CERTIFICATE_ID,
                m=warning_msg
            )
            logger.warning(f"Проверка сертификата пропущена для {url} из-за ошибки получения данных.")
            return

        # Логируем текущее состояние сертификата
        current_date = datetime.now().date()
        end_date = datetime.strptime(d, "%Y-%m-%d").date()
        days_left = (end_date - current_date).days

        if days_left > 0:
            logger.info(f"Сертификат действителен до {d}, осталось {days_left} дней. Организация: {on or 'Не указана'}")
        elif days_left == 0:
            logger.warning(f"Сертификат истекает СЕГОДНЯ: {d}")
        else:
            logger.warning(f"Сертификат уже истёк ({-days_left} дней назад).")

        # Собираем все уведомления о приближающемся истечении или уже истёкшем сертификате
        messages = (
            CheckCertificateMethods.check_if_expired(d, url, on),
            CheckCertificateMethods.check_end_date_one_month(d, url, on),
            CheckCertificateMethods.check_end_date_two_weeks(d, url, on),
            CheckCertificateMethods.check_end_date_one_week(d, url, on),
            CheckCertificateMethods.check_end_date_three_days(d, url, on)
        )

        # Отправляем только непустые сообщения
        if any(messages):
            CheckCertificateMethods.tg_send_message(
                chat_id=TelegramDataPROD.ODIN_YEY_CHAT_ID,
                mt_id=TelegramDataPROD.THREAD_CERTIFICATE_ID,
                m=messages
            )
        else:
            # Опционально: можно отправить сообщение, что всё в порядке (если нужно)
            # logger.info(f"Нет предупреждений по сертификату для {url}")
            pass