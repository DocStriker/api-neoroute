import logging
import os

class SafeExtraFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, "url_full"):
            record.url_full = ""
        return True

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return

    console_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s %(url_full)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    #console_handler.addFilter(SafeExtraFilter())

    os.makedirs("app/logs", exist_ok=True)
    file_handler = logging.FileHandler("app/logs/app.log", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)
    file_handler.addFilter(SafeExtraFilter())

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)