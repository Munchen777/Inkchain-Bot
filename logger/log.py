import logging
import sys

from colorama import Fore, Style, init
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme
from typing import Literal

init(autoreset=True)


class CustomFormatter(logging.Formatter):
    """
    Formatter with colored output, icons, and timestamps.
    
    Customizes log messages with colors, emojis, and precise timestamps.
    """

    COLORS = {
        'DEBUG': Fore.BLUE,
        'INFO': Fore.WHITE,
        'SUCCESS': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT
    }

    ICONS = {
        'DEBUG': '🔍',
        'INFO': '🌐',
        'SUCCESS': '✅',
        'WARNING': '⚠️ ',
        'ERROR': '❌',
        'CRITICAL': '💀'
    }

    def __init__(self,
                 with_colors: bool = True,
                 fmt: str | None = None,
                 ) -> None:
        """
        Initialize formatter with color options.
        
        Args:
            with_colors: Enable colored output
            fmt: Custom format string
        """

        super().__init__(fmt or "%(asctime)s | %(levelname)-8s | %(message)s")
        self.with_colors: bool = with_colors
        self._start_time: datetime = datetime.now()

    def _get_timestamp(self) -> str:
        """ Get current time formatted as HH:MM:SS. """
        return datetime.now().strftime("%H:%M:%S")

    def _get_elapsed_time(self) -> str:
        elapsed: datetime = datetime.now() - self._start_time
        return f"{elapsed:.3f}s"

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record with colors, icons and timestamps.

        Args:
            record: Log record to format

        Returns:
            Formatted log message
        """
        level_name: str = record.levelname
        color: str = self.COLORS.get(level_name, '')
        icon: str = self.ICONS.get(level_name, '')

        if not record.msg:
            return ''

        timestamp = self._get_timestamp()
        elapsed = self._get_elapsed_time()

        if self.with_colors:
            header = f"{color}{timestamp}{Style.RESET_ALL}"
            level = f"{color}{level_name:8}{Style.RESET_ALL}"
        else:
            header = timestamp
            level = f"{level_name:8}"

        thread_info = ""
        if record.threadName != "MainThread":
            thread_info = f"[Thread: {record.threadName}] "

        message = (
            f"{header} | "
            f"{level} | "
            f"{icon} | "
            f"{thread_info}"
            f"{record.getMessage()}"
        )

        if record.exc_info:
            message += f"\n{self.formatException(record.exc_info)}"

        return message


class Logger:
    def __init__(self,
                 name: str = "Custom Logger",
                 level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO",
                 log_file: Path | None = None,
                 with_colors: bool = True,
                 rich_logging: bool = True,
                 ) -> None:

        self.logger: logging.Logger = logging.getLogger()
        self.logger.setLevel(level)

        # Add SUCCESS level
        logging.SUCCESS = 25  # Between INFO and WARNING
        logging.addLevelName(logging.SUCCESS, 'SUCCESS')

        self.logger.handlers.clear()

        if rich_logging:
            console_handler = RichHandler(
                console=Console(theme=Theme({
                    "info": "cyan",
                    "warning": "yellow",
                    "error": "red",
                    "critical": "red bold",
                    "success": "green",
                })),
                show_time=True,
                show_path=True,
            )
        else:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(CustomFormatter(with_colors=with_colors))

        self.logger.addHandler(console_handler)

        if log_file:
            self._setup_file_handler(log_file)

        setattr(self.logger, 'success', self._log_success)
    
    def _setup_file_handler(self, log_file: Path) -> None:
        """Setup file handler for logging to disk."""
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(CustomFormatter(with_colors=False))
        self.logger.addHandler(file_handler)

    def _log_success(self, message: str, *args, **kwargs) -> None:
        """Log message with SUCCESS level."""
        self.logger.log(logging.SUCCESS, message, *args, **kwargs)

    def remove(self) -> None:
        """Remove all handlers from the logger."""
        self.logger.handlers.clear()

    def add(self, sink, *, colorize: bool = False, format: str = None, rotation: str = None, retention: str = None) -> None:
        """
        Add a handler to the logger with custom options.
        
        Args:
            sink: Output destination (stdout or file path)
            colorize: Enable colored output
            format: Custom format string
            rotation: Log rotation settings
            retention: Log retention period
        """
        handler = None
        
        if sink is sys.stdout:
            handler = logging.StreamHandler(sink)
            handler.setFormatter(CustomFormatter(with_colors=colorize, fmt=format))
        
        elif isinstance(sink, (str, Path)):
            if rotation:
                handler = RotatingFileHandler(
                    sink,
                    maxBytes=1024 * 1024 * 1000,
                    backupCount=7 if retention == "7 days" else 1,
                    encoding='utf-8'
                )
            else:
                handler = logging.FileHandler(sink, encoding='utf-8')
            handler.setFormatter(CustomFormatter(with_colors=False, fmt=format))
        
        if handler:
            self.logger.addHandler(handler)

    @property
    def debug(self):
        """Log message at DEBUG level."""
        return self.logger.debug

    @property
    def info(self):
        """Log message at INFO level."""
        return self.logger.info

    @property
    def success(self):
        """Log message at SUCCESS level."""
        return self.logger.success

    @property
    def warning(self):
        """Log message at WARNING level."""
        return self.logger.warning

    @property
    def error(self):
        """Log message at ERROR level."""
        return self.logger.error

    @property
    def critical(self):
        """Log message at CRITICAL level."""
        return self.logger.critical

    def exception(self, msg: str, *args, **kwargs) -> None:
        """Log exception with traceback at ERROR level."""
        self.logger.exception(msg, *args, **kwargs)


log: Logger = Logger(
    name="App Logger",
    level="INFO",
    with_colors=True,
    rich_logging=True,
)
