from utils.urls import CHECK_BEELINE_MVD_LOG_URL
import datetime

def format_base_message() -> str:
    today_str = datetime.date.today().strftime('%Y-%m-%d')
    return f"*Отчет по проверке работы МВД* - [{today_str}]({CHECK_BEELINE_MVD_LOG_URL})\n"