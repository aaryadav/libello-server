import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("baljeet")
    logger.setLevel(logging.INFO)

    # File Handler - logs to a file
    file_handler = RotatingFileHandler("baljeet.log", maxBytes=1000000, backupCount=5)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
