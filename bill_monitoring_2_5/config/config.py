import os
from urllib.parse import urljoin
from typing import List, Dict

class Config:
    # Базовый URL биллинговой системы — рекомендуется задавать через переменную окружения
    BASE_URL = os.getenv("BILLING_BASE_URL", "https://bill.example.local")
    LOGIN_URL = urljoin(BASE_URL, "/site/login")

    # Учётные данные — ОБЯЗАТЕЛЬНО задаются через переменные окружения
    USERNAME = os.getenv("BILLING_USERNAME")
    PASSWORD = os.getenv("BILLING_PASSWORD")

    # Таймаут запросов
    TIMEOUT = int(os.getenv("BILLING_TIMEOUT", "30"))

    # Файлы для хранения состояния
    STATUS_FILE = os.getenv("BILLING_STATUS_FILE", "status.json")
    LAST_SUCCESS_NOTIFY_FILE = os.getenv("BILLING_LAST_NOTIFY_FILE", "last_success_notify.json")

    # Список страниц для мониторинга
    # Задаётся через JSON в переменной окружения или захардкожен (без реальных ссылок в репозитории)
    _URLS_JSON = os.getenv("BILLING_URLS_JSON", '[]')

    try:
        import json
        URLS: List[Dict[str, any]] = json.loads(_URLS_JSON)
    except json.JSONDecodeError:
        # Резервный список с примерами (без реальных URL)
        URLS: List[Dict[str, any]] = [
            {
                "url": "https://bill.example.local/trade/delayed-order/index",
                "name": "Бронированные номера (пример)",
                "slow_threshold": 5.0
            },
            {
                "url": "https://bill.example.local/phone/card/view/1234567890",
                "name": "Карточка номера (пример)",
                "slow_threshold": 5.0
            },
            {
                "url": "https://bill.example.local/admin/user",
                "name": "Админка (пример)",
                "slow_threshold": 5.0
            },
            {
                "url": "https://bill.example.local/report/activations-summary",
                "name": "Сводный отчёт по активациям (пример)",
                "slow_threshold": 5.0
            }
        ]

    # Настройки уведомлений
    SUCCESS_NOTIFY_INTERVAL = 3600  # 1 час