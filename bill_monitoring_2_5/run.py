from core.monitor import BillMonitor
from utils.logger import get_logger

if __name__ == "__main__":
    logger = get_logger("Main")
    try:
        monitor = BillMonitor()
        success = monitor.run()
        if success:
            logger.info("Мониторинг завершён успешно")
        else:
            logger.error("Мониторинг завершился с ошибкой")
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}", exc_info=True)