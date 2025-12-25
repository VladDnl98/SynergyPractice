import re
import datetime
import requests
import logging

from bill_monitoring_2_5.tg.tg_client import TelegramClient
from mvd_monitoring_2_3.state.state_manager import StateManager
from mvd_monitoring_2_3.tg.telegram_config import TelegramConfig
from mvd_monitoring_2_3.utils.message_formatter import format_base_message
from mvd_monitoring_2_3.utils.urls import CHECK_BEELINE_MVD_LOG_URL

logger = logging.getLogger(__name__)


class MvdMonitorService:
    def __init__(self):
        self.state = StateManager.load()
        self.tg_client = TelegramClient()
        self.headers = {
            "Authorization": "Basic YXV0b3Rlc3Q6OVRxNHdIUk9sQmcy",
            "Authority": "cmd.bezlimit.ru",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    def _fetch_log(self) -> str | None:
        try:
            r = requests.get(CHECK_BEELINE_MVD_LOG_URL, headers=self.headers, timeout=15)
            logger.info(f"Запрос лога МВД: HTTP {r.status_code}")

            if r.status_code != 200:
                logger.error(f"Ошибка HTTP при загрузке лога: {r.status_code} {r.reason}")
                return None

            r.encoding = 'utf-8'  # Это заставит r.text вернуть правильный текст
            log_text = r.text
            logger.info(f"Лог успешно получен, размер: {len(log_text)} символов")
            logger.debug(f"Первые 300 символов лога:\n{log_text[:300]}")  # Для отладки

            return log_text

        except requests.RequestException as e:
            logger.error(f"Сетевая ошибка при загрузке лога МВД: {e}")
            return None
        except Exception as e:
            logger.error(f"Неизвестная ошибка при обработке лога: {e}")
            return None

    def _extract_last_status(self, content: str):
        logger.info("Начинаем поиск последней записи о статусе DOL в полном логе МВД")

        lines = content.split('\n')
        status_lines = []

        for line in lines:
            # Ищем строки с timestamp в начале: YYYY-MM-DD HH:MM:SS
            timestamp_match = re.match(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+(.*)', line)
            if not timestamp_match:
                continue

            timestamp_str, text = timestamp_match.groups()
            try:
                timestamp = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue

            cleaned = text.strip()
            logger.debug(f"Анализ строки: {timestamp_str} | {cleaned}")

            # Обработка [UP]DOL работает
            if '[UP]DOL работает' in cleaned:
                time_match = re.search(r'\(([0-9.]+)\s+sec\)', cleaned)
                resp_time = None
                response_sec = None

                if time_match:
                    response_sec = float(time_match.group(1))
                    resp_time = f"{int(response_sec)}с" if response_sec >= 1 else f"{response_sec:.2f}с"

                # Ключевое правило из ТЗ: >5 сек → DOWN, даже при [UP]
                if response_sec is not None and response_sec > 5.0:
                    logger.warning(f"🔴 Время ответа {response_sec:.2f}с > 5 сек → принудительно считаем DOWN")
                    status_lines.append((timestamp, 1, "DOL не работает (медленный ответ)", resp_time))
                else:
                    logger.info(
                        f"🟢 Найдена запись: DOL работает | Время: {resp_time or 'не указано'} | {timestamp_str}")
                    status_lines.append((timestamp, 0, "DOL работает", resp_time))

            # Обработка [DOWN]DOL не работает
            elif '[DOWN]DOL не работает' in cleaned:
                logger.warning(f"🔴 Найдена запись: DOL не работает | {timestamp_str}")
                status_lines.append((timestamp, 1, "DOL не работает", None))

        # Если прямых записей [UP]/[DOWN] нет — ищем косвенные признаки ошибки
        if not status_lines:
            logger.warning("⚠️ Записи с [UP]/[DOWN]DOL не найдены")

            recent_lines = '\n'.join(lines[-50:])  # последние 50 строк

            if 'Error Fetching http headers' in recent_lines:
                logger.warning("🔴 Обнаружена ошибка: 'Error Fetching http headers'")
                return 1, "DOL не работает (ошибка заголовков)", None
            if 'Прошлый процесс еще не закончен' in recent_lines:
                logger.warning("🔴 Обнаружен зависший процесс")
                return 1, "DOL не работает (процесс завис)", None

            logger.warning("⚠️ Статус DOL не определён")
            return None, "Статус DOL не найден", None

        # Берём самую последнюю валидную запись
        latest = max(status_lines, key=lambda x: x[0])
        timestamp, status, text, resp_time = latest

        if status == 0:
            logger.info(f"✅ Последний статус DOL: {text} 🟢")
        else:
            logger.warning(f"✅ Последний статус DOL: {text} 🔴")

        logger.info(f"   Время записи: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        if resp_time:
            logger.info(f"   Время ответа: {resp_time}")

        return status, text, resp_time

    def check_and_notify(self) -> None:
        logger.info("=== ЗАПУСК ПРОВЕРКИ СЕРВИСА МВД ===")

        base_message = format_base_message()
        current_time = datetime.datetime.now()
        prev_status = self.state.get("dol_work_status")
        logger.info(f"Предыдущий статус DOL: {prev_status} "
                    f"(0=работает, 1=не работает, None=первый запуск)")

        log_content = self._fetch_log()
        if log_content is None:
            error_msg = base_message + "Ошибка при получении лога сервера 🔴\n"
            logger.error("Критическая ошибка загрузки лога — отправляем уведомление")
            self._send_to_all(error_msg)
            return

        status, status_text, response_time = self._extract_last_status(log_content)

        if status is None:
            error_msg = base_message + f"Не удалось определить статус DOL 🔴\nПричина: {status_text}\n"
            logger.error("Статус не определён — отправляем уведомление об ошибке")
            self._send_to_all(error_msg)
            self.state["dol_work_status"] = 1
            StateManager.save(self.state)
            return

        logger.info(f"Текущий статус DOL: {status} → {status_text}")
        if response_time:
            logger.info(f"Время ответа: {response_time}")

        should_send = False
        message = base_message

        # Логика кейсов с подробным логированием
        if status == 0 and prev_status == 1:
            logger.info("🟢 КЕЙС 4: DOL восстановился после сбоя → отправляем уведомление")
            message += "Работа DOL восстановлена 🟢\n"
            if response_time:
                message += f"Время ответа МВД: {response_time}\n"
            should_send = True

        elif status == 1 and prev_status == 0:
            logger.warning("🔴 КЕЙС 2: DOL перестал работать → отправляем уведомление об ошибке")
            message += f"Выявлена ошибка в работе МВД 🔴\nРезультат проверки: {status_text}\n"
            if response_time:
                message += f"Время ответа МВД: {response_time}\n"
            should_send = True

        elif status == 0:
            last_msg_time = self.state.get("last_message_time")
            if last_msg_time is None or (current_time - last_msg_time).total_seconds() >= 3600:
                logger.info("🟢 КЕЙС 1: DOL работает → отправляем регулярное сообщение (раз в час)")
                message += f"Результат проверки: {status_text} 🟢\n"
                if response_time:
                    message += f"Время ответа МВД: {response_time}\n"
                should_send = True
            else:
                logger.info(f"🟢 DOL работает, но сообщение уже было отправлено недавно "
                            f"({(current_time - last_msg_time).total_seconds() // 60} мин назад)")

        elif status == 1:
            if prev_status == 1:
                logger.info("🔴 КЕЙС 3: DOL продолжает не работать → уведомление НЕ отправляем")
            elif prev_status is None:
                logger.warning("🔴 Первый запуск и DOL не работает → отправляем начальное уведомление")
                message += f"Выявлена ошибка в работе МВД 🔴\nРезультат проверки: {status_text}\n"
                if response_time:
                    message += f"Время ответа МВД: {response_time}\n"
                should_send = True

        if should_send:
            logger.info("📤 Отправка сообщения в Telegram-чаты")
            logger.debug(f"Содержимое сообщения:\n{message}")
            self._send_to_all(message)
        else:
            logger.info("ℹ️  Отправка сообщения не требуется")

        # Обновляем состояние
        if should_send and status == 0:
            self.state["last_message_time"] = current_time
        if should_send and status == 1:
            self.state["last_error_sent_time"] = current_time
        self.state["dol_work_status"] = status

        StateManager.save(self.state)
        logger.info("Состояние сохранено. Проверка завершена.\n")

    def _send_to_all(self, message: str):

        self.tg_client.send_message(TelegramConfig.ODIN_YEY_CHAT_ID, TelegramConfig.THREAD_MVD_ID, message)
        self.tg_client.send_message(TelegramConfig.MVD_CHAT_ID, None, message)
        self.tg_client.send_message(TelegramConfig.OPPERACIONIST_PD_CHAT_ID, None, message)