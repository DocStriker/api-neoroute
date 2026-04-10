import logging
import os

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    os.makedirs("app/logs", exist_ok=True)
    file_handler = logging.FileHandler("app/logs/app.log", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)