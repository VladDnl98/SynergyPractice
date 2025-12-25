import requests
import urllib3
from dateutil import parser
import certifi
from datetime import datetime, timedelta
from other.loger.logger_config import LoggerManager
from other.methods.other_base_methods import OtherBaseMethods

logger = LoggerManager.get_logger(__name__)

class CheckCertificateMethods(OtherBaseMethods):
    @staticmethod
    def check_site_accessibility(url, timeout=10):
        full_url = url if url.startswith("http") else f"https://{url}"
        try:
            response = requests.head(full_url, timeout=timeout, allow_redirects=True, verify=True)
            logger.info(f"Сайт {url} доступен (статус {response.status_code})")
            return response.status_code in (200, 301, 302, 303, 307, 308, 403)
        except Exception as e:
            logger.error(f"Ошибка доступности {url}: {e}")
            return False

    @staticmethod
    def check_certificate_date(u):
        """
        Получает дату истечения и организацию из SSL-сертификата через requests.
        Более надёжный способ, чем socket + wrap_socket.
        """
        full_url = u if u.startswith("http") else f"https://{u}"

        # Сначала проверяем доступность
        if not CheckCertificateMethods.check_site_accessibility(u):
            logger.error(f"Сайт {u} недоступен по HTTPS. Пропуск проверки сертификата.")
            return None, None

        try:
            with requests.get(full_url, timeout=10, verify=True, stream=True) as response:
                conn = response.raw.connection.sock
                if hasattr(conn, 'getpeercert'):
                    cert = conn.getpeercert()
                else:
                    http = urllib3.PoolManager(ca_certs=certifi.where())
                    r = http.request('GET', full_url)
                    cert = r.connection.sock.getpeercert()

            if not cert:
                logger.warning(f"Сертификат не получен для {u}")
                return None, None

            not_after_str = cert.get('notAfter')
            on = None
            for item in cert.get('issuer', []):
                for key, value in item:
                    if key == 'organizationName':
                        on = value
                        break
                if on:
                    break

            if not not_after_str:
                logger.warning(f"Поле notAfter отсутствует для {u}")
                return None, on

            not_after_date = parser.parse(not_after_str)
            d = not_after_date.strftime("%Y-%m-%d")
            logger.info(f"Сертификат {u} действителен до {d}, организация: {on}")
            return d, on

        except Exception as e:
            logger.error(f"Ошибка при получении сертификата {u}: {e}")
            return None, None

    @staticmethod
    def check_if_expired(d, u, on):
        """
        Проверяет, истек ли сертификат.
        :param d: Дата истечения.
        :param u: URL.
        :param on: Организация.
        :return: Сообщение или None.
        """
        try:
            current_date = datetime.now().date()
            end_date = datetime.strptime(d, "%Y-%m-%d").date()
            if end_date < current_date:
                m = f"Внимание! На сайте: {u} \n" \
                    "Сертификат истек! Необходимо актуализировать информацию по сертификату.\n" \
                    f"Название организации: {on} \n" \
                    f"Истек: {d}"
                logger.warning(f"Сертификат истек для {u}: {d}")
                return m
            return None
        except ValueError as e:
            logger.error(f"Ошибка формата даты для {u}: {e}")
            return None

    @staticmethod
    def check_end_date_one_month(d, u, on):
        """
        Проверяет, истекает ли сертификат ровно через 30 дней.
        :param d: Дата истечения.
        :param u: URL.
        :param on: Организация.
        :return: Сообщение или None.
        """
        try:
            current_date = datetime.now().date()
            end_date = datetime.strptime(d, "%Y-%m-%d").date()
            one_month_from_now = current_date + timedelta(days=30)
            if end_date == one_month_from_now:
                m = f"Внимание! На сайте: {u} \n" \
                    "Заканчивается срок действия сертификата, осталось 30 дней!\n" \
                    f"Название организации: {on} \n" \
                    f"заканчивается: {d}"
                logger.info(f"Обнаружено истечение через 30 дней для {u}")
                return m
            return None
        except ValueError as e:
            logger.error(f"Ошибка формата даты для {u}: {e}")
            return None

    @staticmethod
    def check_end_date_two_weeks(d, u, on):
        """
        Проверяет, истекает ли сертификат ровно через 14 дней.
        :param d: Дата истечения.
        :param u: URL.
        :param on: Организация.
        :return: Сообщение или None.
        """
        try:
            current_date = datetime.now().date()
            end_date = datetime.strptime(d, "%Y-%m-%d").date()
            two_weeks_from_now = current_date + timedelta(days=14)
            if end_date == two_weeks_from_now:
                m = f"Внимание! На сайте: {u} \n" \
                    "Заканчивается срок действия сертификата, осталось 14 дней!\n" \
                    f"Название организации: {on} \n" \
                    f"заканчивается: {d}"
                logger.info(f"Обнаружено истечение через 14 дней для {u}")
                return m
            return None
        except ValueError as e:
            logger.error(f"Ошибка формата даты для {u}: {e}")
            return None

    @staticmethod
    def check_end_date_one_week(d, u, on):
        """
        Проверяет, истекает ли сертификат ровно через 7 дней.
        :param d: Дата истечения.
        :param u: URL.
        :param on: Организация.
        :return: Сообщение или None.
        """
        try:
            current_date = datetime.now().date()
            end_date = datetime.strptime(d, "%Y-%m-%d").date()
            one_week_from_now = current_date + timedelta(days=7)
            if end_date == one_week_from_now:
                m = f"Внимание! На сайте: {u} \n" \
                    "Заканчивается срок действия сертификата, осталось 7 дней!\n" \
                    f"Название организации: {on} \n" \
                    f"заканчивается: {d}"
                logger.info(f"Обнаружено истечение через 7 дней для {u}")
                return m
            return None
        except ValueError as e:
            logger.error(f"Ошибка формата даты для {u}: {e}")
            return None

    @staticmethod
    def check_end_date_three_days(d, u, on):
        """
        Проверяет, истекает ли сертификат ровно через 3 дня.
        :param d: Дата истечения.
        :param u: URL.
        :param on: Организация.
        :return: Сообщение или None.
        """
        try:
            current_date = datetime.now().date()
            end_date = datetime.strptime(d, "%Y-%m-%d").date()
            three_days_from_now = current_date + timedelta(days=3)
            if end_date == three_days_from_now:
                m = f"Внимание! На сайте: {u} \n" \
                    "Заканчивается срок действия сертификата, осталось 3 дня!\n" \
                    f"Название организации: {on} \n" \
                    f"заканчивается: {d}"
                logger.info(f"Обнаружено истечение через 3 дня для {u}")
                return m
            return None
        except ValueError as e:
            logger.error(f"Ошибка формата даты для {u}: {e}")
            return None
