import re
import requests

from bill_monitoring_2_5.config.config import Config
from bill_monitoring_2_5.utils.logger import get_logger


class Authenticator:
    def __init__(self, session: requests.Session):
        self.session = session
        self.logger = get_logger(self.__class__.__name__)
        self.csrf_token: str | None = None

    def _get_csrf_token(self):
        """Извлекает CSRF из формы логина"""
        try:
            self.logger.info("Получение CSRF токена...")
            resp = self.session.get(Config.LOGIN_URL, headers=self._headers(), timeout=Config.TIMEOUT)

            if resp.status_code != 200:
                self.logger.error(f"Страница логина недоступна: HTTP {resp.status_code}")
                return None

            match = re.search(r'name=["\']_csrf["\'][^>]+value=["\']([^"\']+)["\']', resp.text)
            if not match:
                self.logger.error("CSRF токен не найден в HTML")
                return None

            token = match.group(1)
            self.logger.info(f"CSRF токен получен: {token[:20]}...")
            return token

        except requests.RequestException as e:
            self.logger.error(f"Сетевая ошибка при получении CSRF: {e}")
            return None

    def _headers(self):
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    def login(self) -> bool:
        if not Config.USERNAME or not Config.PASSWORD:
            self.logger.critical(
                "Логин или пароль не заданы в переменных окружения! "
                "Установите BILLING_USERNAME и BILLING_PASSWORD."
            )
            return False


        self.logger.info("Начало процесса авторизации...")

        self.csrf_token = self._get_csrf_token()
        if not self.csrf_token:
            self.logger.error("Не удалось получить CSRF-токен. Авторизация прервана.")
            return False

        data = {
            "_csrf": self.csrf_token,
            "LoginForm[username]": Config.USERNAME,
            "LoginForm[password]": Config.PASSWORD,
            "LoginForm[rememberMe]": "1"
        }

        headers = {
            **self._headers(),
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": Config.BASE_URL,
            "Referer": Config.LOGIN_URL,
        }

        try:
            self.logger.info("Отправка POST-запроса для авторизации...")
            resp = self.session.post(
                Config.LOGIN_URL,
                headers=headers,
                data=data,
                allow_redirects=True,
                timeout=Config.TIMEOUT
            )

            self.logger.info(
                f"Ответ на авторизацию: HTTP {resp.status_code}, конечный URL: {resp.url}"
            )

            if resp.status_code in [200, 302] and "site/login" not in resp.url:
                self.logger.info(f"Авторизация успешна → перенаправление на {resp.url}")
                return True
            else:
                self.logger.error(
                    f"Авторизация не удалась: остались на странице логина "
                    f"(статус {resp.status_code}, URL: {resp.url})"
                )
                return False

        except requests.RequestException as e:
            self.logger.error(f"Сетевая ошибка при попытке авторизации: {e}")
            return False