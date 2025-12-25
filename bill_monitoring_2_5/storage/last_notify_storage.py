import json
from pathlib import Path


from datetime import datetime

from bill_monitoring_2_5.config.config import Config
from bill_monitoring_2_5.utils.logger import get_logger


class LastNotifyStorage:
    _logger = get_logger("LastNotify")

    @staticmethod
    def load() -> float:
        path = Path(Config.LAST_SUCCESS_NOTIFY_FILE)
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("timestamp", 0)
            except Exception as e:
                LastNotifyStorage._logger.warning(f"Ошибка чтения времени уведомления: {e}")
        return 0

    @staticmethod
    def save():
        try:
            with open(Config.LAST_SUCCESS_NOTIFY_FILE, 'w', encoding='utf-8') as f:
                json.dump({"timestamp": datetime.now().timestamp()}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            LastNotifyStorage._logger.error(f"Ошибка сохранения времени уведомления: {e}")