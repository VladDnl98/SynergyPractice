import logging
import sys


def get_logger(name: str = "monitoring"):
    logger = logging.getLogger(name)

    # Избегаем добавления хендлеров несколько раз
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')

    # Консоль
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    logger.addHandler(ch)


    return logger