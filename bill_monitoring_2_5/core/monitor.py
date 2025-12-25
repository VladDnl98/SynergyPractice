import requests

from bill_monitoring_2_5.auth.authenticator import Authenticator
from bill_monitoring_2_5.checker.url_checker import URLChecker
from bill_monitoring_2_5.storage.status_storage import StatusStorage
from bill_monitoring_2_5.utils.logger import get_logger


class BillMonitor:
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.session = requests.Session()
        self.auth = Authenticator(self.session)
        self.checker = URLChecker(self.session)
        self.status_storage = StatusStorage()

    def run(self):
        self.logger.info("=== Запуск цикла мониторинга биллинга ===")

        if not self.auth.login():
            self.logger.error("Авторизация не удалась — мониторинг прерван")
            return False

        self.logger.info("Авторизация прошла успешно, начало проверки страниц")

        prev_status = self.status_storage.load()
        pages = self.checker.check_urls(Config.URLS, prev_status)

        current_status = self._build_current_status(pages, prev_status)

        # Обновляем и отправляем почасовой отчёт "всё ОК", если пришло время
        new_report_time = self.checker.send_hourly_ok_report(current_status)
        if new_report_time != current_status.get("last_ok_report"):
            current_status["last_ok_report"] = new_report_time
            self.logger.info("Время почасового отчёта обновлено и сохранено")

        self.status_storage.save(current_status)

        self.logger.info("Статус успешно сохранён в status.json")
        self.logger.info("=== Цикл мониторинга завершён успешно ===\n")

        return True

    def _build_current_status(self, pages, prev_status):
        status = {}
        for page in pages:
            status[page.url] = {
                "success": page.success,
                "slow": page.was_slow,
                "failed": page.was_failed,
                "response_time": page.response_time,
                "status_code": page.status_code,
                "error": page.error
            }
        status["last_ok_report"] = prev_status.get("last_ok_report", 0)

        return status