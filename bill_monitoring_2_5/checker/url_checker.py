import requests
import time
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

from bill_monitoring_2_5.config.config import Config
from bill_monitoring_2_5.models.page import Page
from bill_monitoring_2_5.tg.tg_client import TelegramClient
from bill_monitoring_2_5.utils.logger import get_logger
from certificate_cheker_2_1.tg.tg_config import TelegramDataPROD


class URLChecker:
    def __init__(self, session: requests.Session):
        self.session = session
        self.logger = get_logger(self.__class__.__name__)
        self.TelegramClient = TelegramClient()

    def _headers(self):
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    def check_urls(self, url_configs: List[Dict], prev_status: dict) -> List[Page]:
        pages = []
        self.logger.info(f"Проверка {len(url_configs)} страниц...")

        for config in url_configs:
            url = config["url"].strip()
            name = config["name"]
            threshold = config["slow_threshold"]
            if not url:
                continue

            prev = prev_status.get(url, {})
            page = Page(
                url=url,
                name=name,
                slow_threshold=threshold,
                was_slow=prev.get("slow", False),
                was_failed=not prev.get("success", True)  # если ранее не было success → была ошибка
            )
            pages.append(page)

        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_page = {
                executor.submit(self._check_single, page): page for page in pages
            }
            for future in as_completed(future_to_page):
                page = future_to_page[future]
                try:
                    future.result()  # обновляет page внутри
                except Exception as e:
                    page.error = str(e)
                    page.response_time = 0
                    self._handle_error(page, prev_status)

        return pages

    def _check_single(self, page: Page):
        start_time = time.time()
        try:
            resp = self.session.get(
                page.url,
                headers=self._headers(),
                timeout=Config.TIMEOUT,
                allow_redirects=True
            )
            page.response_time = time.time() - start_time
            page.status_code = resp.status_code

            if resp.status_code == 200:
                page.success = True
                self._handle_success(page)
            else:
                page.error = f"HTTP {resp.status_code}"
                self._handle_error(page)
        except requests.RequestException as e:
            page.response_time = time.time() - start_time
            page.error = str(e)
            self._handle_error(page)

    def _handle_success(self, page: Page):
        rt = page.response_time or 0
        is_slow = rt > page.slow_threshold

        if is_slow and not page.was_slow:
            msg_text = (
                f"*Проверка работы страниц биллинга*\n"
                f"*Медленная загрузка🟡*\n\n"
                f"*Наименование страницы*: **{page.name}**\n"
                f"*Ссылка*: {page.url}\n"
                f"*Время*: `{rt:.2f}с` > {page.slow_threshold}с"
            )
            self.logger.warning(f"ОТПРАВКА: Медленная загрузка (первое) — {page.name} ({rt:.2f}с)")
            self.TelegramClient.send_message(
                TelegramDataPROD.ODIN_YEY_CHAT_ID,
                TelegramDataPROD.TREAD_MONITORING_ID,
                msg_text
            )
            page.was_slow = True

        elif not is_slow and page.was_slow:
            msg_text = (
                f"*Проверка работы страниц биллинга*\n"
                f"*Скорость восстановлена*🟢\n"
                f"*Наименование страницы*: **{page.name}**\n"
                f"*Ссылка*: {page.url}\n"
                f"*Время*: `{rt:.2f}с`"
            )
            self.logger.info(f"ОТПРАВКА: Восстановление скорости — {page.name} ({rt:.2f}с)")
            self.TelegramClient.send_message(
                TelegramDataPROD.ODIN_YEY_CHAT_ID,
                TelegramDataPROD.TREAD_MONITORING_ID,
                msg_text
            )
            page.was_slow = False

        if page.was_failed:
            msg_text = (
                f"*Проверка работы страниц биллинга*\n"
                f"*Работа страницы восстановлена*🟢\n"
                f"*Наименование страницы*: **{page.name}**\n"
                f"*Ссылка*: {page.url}\n"
                f"*Время ответа*: `{rt:.2f}с`"
            )
            self.logger.info(f"ОТПРАВКА: Восстановление после ошибки — {page.name}")
            self.TelegramClient.send_message(
                TelegramDataPROD.ODIN_YEY_CHAT_ID,
                TelegramDataPROD.TREAD_MONITORING_ID,
                msg_text
            )
            page.was_failed = False

        else:
            self.logger.info(f"OK: {page.name} — {rt:.2f}с")

    def _handle_error(self, page: Page):
        rt = page.response_time or 0

        if not page.was_failed:
            msg_text = (
                f"*Проверка работы страниц биллинга*\n"
                f"*Ошибка при открытии страницы*🔴\n"
                f"*Наименование страницы*: **{page.name}**\n"
                f"*Ссылка*: {page.url}\n"
                f"*Ошибка*: `{page.error}`\n"
                f"*Время*: `{rt:.2f}с`"
            )
            self.logger.warning(f"ОТПРАВКА: Новая ошибка — {page.name} ({page.error})")
            self.TelegramClient.send_message(
                TelegramDataPROD.ODIN_YEY_CHAT_ID,
                TelegramDataPROD.TREAD_MONITORING_ID,
                msg_text
            )
            page.was_failed = True
        else:
            self.logger.error(f"ПОВТОРНАЯ ОШИБКА: {page.name} — {page.error} (уведомление не отправлено)")

    def send_hourly_ok_report(self, prev_status: dict) -> float:
        last_report = prev_status.get("last_ok_report", 0)
        current_time = time.time()

        if current_time - last_report >= 3600:
            msg_text = (
                f"*Проверка работы страниц биллинга*\n"
                f"*Ресурс работает корректно*🟢\n"
            )
            self.logger.info("ОТПРАВКА: Почасовой отчёт — всё ОК")
            self.TelegramClient.send_message(
                TelegramDataPROD.ODIN_YEY_CHAT_ID,
                TelegramDataPROD.TREAD_MONITORING_ID,
                msg_text
            )
            return current_time
        return last_report