
import logging
from pathlib import Path

from rich.logging import RichHandler

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "axion.log"


class AxionLogger:

    _logger: logging.Logger | None = None

    @classmethod
    def get_logger(cls, name: str = "axion") -> logging.Logger:
        if cls._logger is not None:
            return cls._logger

        LOG_DIR.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False  

        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)

        console_handler = RichHandler(
            show_time=False,
            show_path=False,
            markup=True,
        )
        console_handler.setLevel(logging.INFO)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        cls._logger = logger
        return logger


if __name__ == "__main__":
    log = AxionLogger.get_logger()
    log.debug("This is a debug message (file only).")
    log.info("This is an info message.")
    log.warning("This is a warning message.")
    log.error("This is an error message.")
