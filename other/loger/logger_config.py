import logging

class LoggerManager:
    """
    Менеджер для централизованного логирования.
    Гарантирует единственный экземпляр логгера с одним хендлером.
    """

    @staticmethod
    def get_logger(name: str = __name__) -> logging.Logger:
        """
        Возвращает настроенный логгер с именем модуля.
        Каждый раз очищает старые хендлеры, чтобы избежать дублирования.
        """
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        if logger.handlers:
            logger.handlers.clear()

        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        logger.propagate = False

        return logger