import logging, os
from .singleton import Singleton


class Logger(metaclass=Singleton):
    """
    Outputs logs to app.log
    """

    def __init__(self):
        self.logger = logging.getLogger("LOGGER")
        self.logger.setLevel(logging.INFO)
        # File handler
        current_dir = os.path.dirname(os.path.abspath(__file__))
        log_file_path = os.path.join(current_dir, 'workspace/app.log')
        file_handler = logging.FileHandler(log_file_path)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        # Add the file handler to the logger
        self.logger.addHandler(file_handler)

    def _log(self, message, level=logging.INFO):
        self.logger.log(level, message)

    def set_level(self, level):
        self.logger.setLevel(level)

    def debug(self, message):
        self._log(message, logging.DEBUG)

    def info(self, message):
        self._log(message, logging.INFO)

    def error(self, message):
        self._log(message, logging.ERROR)

    def warn(self, message):
        self._log(message, logging.WARN)


logger = Logger()
