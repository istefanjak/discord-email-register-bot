"""
Module which contains the function for setting up the instance for logging then returning it
"""
import logging
from constants import LOG_FILE


def getLogger(name: str) -> logging.Logger:
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(name)

    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(LOG_FILE)
    c_handler.setLevel(logging.DEBUG)
    f_handler.setLevel(logging.DEBUG)

    c_format = logging.Formatter('[ %(name)s | %(levelname)s ]: %(message)s')
    f_format = logging.Formatter('[ %(asctime)s | %(name)s | %(levelname)s ]: %(message)s', "%d-%m-%Y %H:%M:%S")
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
    return logger

if __name__ == "__main__":
    getLogger("testlogger").error("Testni error")