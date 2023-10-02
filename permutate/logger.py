import logging
import os

import colorlog
from dotenv import load_dotenv

from permutate.singleton import Singleton

load_dotenv()
ENVIRONMENT = os.environ.get("ENVIRONMENT")


class Logger(metaclass=Singleton):
    """
    Outputs logs to app.log
    """

    def __init__(self):
        self.logger = logging.getLogger("LOGGER")
        self.logger.setLevel(logging.INFO)
        # File handler
        current_dir = os.path.dirname(os.path.abspath(__file__))
        log_file_path = os.path.join(current_dir, "workspace/app.log")
        file_handler = logging.FileHandler(log_file_path, mode="w")
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        # Add the file handler to the logger
        self.logger.addHandler(file_handler)

        if ENVIRONMENT == "development":
            # Stream handler (stdout)
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(
                colorlog.ColoredFormatter(
                    "%(log_color)s%(levelname)s:\t %(reset)s %(message)s",
                    log_colors={
                        "DEBUG": "blue",
                        "INFO": "green",
                        "WARNING": "yellow",
                        "ERROR": "red",
                        "CRITICAL": "bold_red",
                    },
                    secondary_log_colors={},
                    style="%",  # to avoid an error with recent colorlog versions
                )
            )
            # Add the stream handler to the logger
            self.logger.addHandler(stream_handler)

    def _log(self, message, level=logging.INFO):
        self.logger.log(level, message)

    def set_level(self, level):
        self.logger.setLevel(level)

    def debug(self, message):
        self._log(message, logging.DEBUG)

    def info(self, title, message):
        self._log(f"({title}) {message}", logging.INFO)

    def error(self, message):
        self._log(message, logging.ERROR)

    def warn(self, message):
        self._log(message, logging.WARN)


logger = Logger()
