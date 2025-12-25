import json
from pathlib import Path
from typing import Dict, Any

from bill_monitoring_2_5.config.config import Config
from bill_monitoring_2_5.utils.logger import get_logger


class StatusStorage:
    @staticmethod
    def load() -> Dict[str, Any]:
        path = Path(Config.STATUS_FILE)
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "last_ok_report" not in data:
                        data["last_ok_report"] = 0
                    return data
            except Exception as e:
                get_logger("StatusStorage").warning(f"Ошибка чтения статуса: {e}")
        return {"last_ok_report": 0}

    @staticmethod
    def save(status: Dict[str, Any]):
        try:
            with open(Config.STATUS_FILE, 'w', encoding='utf-8') as f:
                json.dump(status, f, ensure_ascii=False, indent=2)
        except Exception as e:
            get_logger("StatusStorage").error(f"Ошибка сохранения статуса: {e}")