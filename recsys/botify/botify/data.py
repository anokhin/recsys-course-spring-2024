import logging
from dataclasses import dataclass, asdict
from logging.handlers import RotatingFileHandler

from pythonjsonlogger import jsonlogger

from botify.experiment import Experiments


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
        self.experiment_context = Experiments()

    def log(self, location, datum: Datum):
        values = asdict(datum)
        values["experiments"] = {
            experiment.name: experiment.assign(datum.user).name
            for experiment in self.experiment_context.experiments
        }
        self.logger.info(location, extra=values)
