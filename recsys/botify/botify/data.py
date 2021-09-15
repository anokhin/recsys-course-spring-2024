import logging
from dataclasses import dataclass, asdict
from logging.handlers import RotatingFileHandler

from pythonjsonlogger import jsonlogger


@dataclass
class Datum:
    timestamp: int
    user: int
    track: int
    time: float
    recommendation: int = None


class DataLogger:
    def __init__(self, app):
        self.logger = logging.getLogger("data")

        handler = RotatingFileHandler(
            app.config["DATA_LOG_FILE"],
            maxBytes=app.config["DATA_LOG_FILE_MAX_BYTES"],
            backupCount=app.config["DATA_LOG_FILE_BACKUP_COPIES"],
        )
        formatter = jsonlogger.JsonFormatter()
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    def log(self, location, datum: Datum):
        self.logger.info(location, extra=asdict(datum))
