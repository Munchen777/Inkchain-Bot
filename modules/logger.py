import logging
import os.path

from abc import ABC
from colorama import init, Fore, Style
from typing import Literal

from generall_settings import LOGS_FILE_PATH, EXCEL_FILE_PATH, GLOBAL_NETWORK


init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA + Style.BRIGHT,
    }

    def format(self, record: logging.LogRecord) -> str:
        message: str = super().format(record)
        color = self.LEVEL_COLORS.get(record.levelno, Fore.WHITE)

        return f"{color}{message}{Style.RESET_ALL}"


class LevelFileHandler(logging.Handler):
    def __init__(self, base_name: str = "file"):
        """
        Handler for different levels of logging

        """
        super().__init__()

        self.name: str = base_name
        self.formatter: logging.Formatter = logging.Formatter(
            fmt="%(levelname)s | %(name)s | %(asctime)s | %(lineno)d | %(message)s",
            datefmt="%I:%M:%S"
        )

    def emit(self, record: logging.LogRecord):
        """
        Form a name of file due to its logging level and
        write down to the appropriate

        """
        levelname: str = record.levelname
        filename: str = f"{self.name}_{levelname.lower()}.log"
        filepath: str = os.path.join(LOGS_FILE_PATH, filename)

        self.handler: logging.FileHandler = logging.FileHandler(
            filename=filepath,
            mode="a",
        )
        self.handler.setFormatter(self.formatter)
        message: str = self.handler.format(record)

        with open(self.handler.baseFilename, self.handler.mode) as file:
            file.write(message + "\n")


class Logger(ABC):
    def __init__(self, name: str = "app", file_base_name: str = "log"):
        self.logger: logging.Logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:

            if not os.path.exists(LOGS_FILE_PATH):
                os.mkdir(LOGS_FILE_PATH)

            formatter: ColoredFormatter = ColoredFormatter(
                fmt="%(levelname)s | %(name)s | %(asctime)s | %(lineno)d | %(message)s",
                datefmt="%I:%M:%S"
            )

            stream_handler: logging.StreamHandler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            self.logger.addHandler(stream_handler)

            file_handler: LevelFileHandler = LevelFileHandler(base_name=file_base_name)
            self.logger.addHandler(file_handler)
    
    def logger_msg(self, account_name, address, msg, type_msg: Literal["info", "error", "success", "warning"] = 'info'):
        from data.config import CHAIN_NAMES

        software_chain: str = CHAIN_NAMES[GLOBAL_NETWORK]

        if account_name is None and address is None:
            info = f'[Inkochain] | {software_chain} | {self.__class__.__name__} |'
        elif account_name is not None and address is None:
            info = f'[{account_name}] | {software_chain} | {self.__class__.__name__} |'
        else:
            info = f'[{account_name}] | {address} | {software_chain} | {self.__class__.__name__} |'

        if type_msg == 'info':
            self.logger.info(f"{info} {msg}")
        elif type_msg == 'error':
            self.logger.error(f"{info} {msg}")
        elif type_msg == 'success':
            self.logger.info(f"{info} {msg}")
        elif type_msg == 'warning':
            self.logger.warning(f"{info} {msg}")

    def get_logger(self) -> logging.Logger:
        return self.logger
