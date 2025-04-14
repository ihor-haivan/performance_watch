# logger_manager.py

import logging
from logging.handlers import RotatingFileHandler

class LoggerManager:
    """
    Encapsulates logging configuration.
    """
    def __init__(self, logger_name: str = "custom_script",
                 log_level: int = logging.INFO, log_file:  str = None,
                 max_bytes: int = 2_000_000, backup_count: int = 3):
        self.logger_name = logger_name
        self.log_level = log_level
        self.log_file = log_file or f"{logger_name}.log"
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.logger = logging.getLogger(self.logger_name)
        self._setup_logger()

    def _setup_logger(self) -> None:
        # Configure the basic format for logs.
        log_format = '%(asctime)s [%(levelname)s] [%(name)s] (%(module)s:%(lineno)d, %(funcName)s): %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        logging.basicConfig(
            format=log_format,
            level=self.log_level,
            datefmt=date_format
        )
        self.logger.setLevel(self.log_level)

        # Suppress unnecessary logging from external modules.
        logging.getLogger("py4j").setLevel(logging.ERROR)

        # Clear any existing handlers to avoid duplications.
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        formatter = logging.Formatter(log_format, datefmt=date_format)

        # Create and add a console (stream) handler.
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(self.log_level)
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

        # Create and add a rotating file handler.
        file_handler = RotatingFileHandler(
            filename=self.log_file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding="utf-8"
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Prevent log propagation to ancestor loggers.
        self.logger.propagate = False
