import json
import os
import datetime
import logging

logger = logging.getLogger(__name__)

STATE_FILE = "mvd_activity_state.json"


class StateManager:
    @staticmethod
    def load() -> dict:
        if not os.path.exists(STATE_FILE):
            return StateManager._default_state()

        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Восстановление datetime
                for key in ["last_message_time", "last_error_sent_time"]:
                    if data.get(key):
                        data[key] = datetime.datetime.fromisoformat(data[key])
                return data
        except Exception as e:
            logger.error(f"Ошибка чтения состояния: {e}")
            return StateManager._default_state()

    @staticmethod
    def save(state: dict):
        # Конвертируем datetime в строки
        save_state = state.copy()
        for key in ["last_message_time", "last_error_sent_time"]:
            if save_state.get(key):
                save_state[key] = save_state[key].isoformat()

        try:
            with open(STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(save_state, f, indent=2, ensure_ascii=False)
            logger.info(f"Состояние сохранено: dol_work_status={state.get('dol_work_status')}")
        except Exception as e:
            logger.error(f"Ошибка сохранения состояния: {e}")

    @staticmethod
    def _default_state():
        return {
            "last_response": None,
            "last_message_time": None,
            "last_error_sent_time": None,
            "dol_work_status": None  # 0 = работает, 1 = не работает
        }