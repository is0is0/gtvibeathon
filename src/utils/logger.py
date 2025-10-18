"""
Centralized Logging System
--------------------------
Production-grade logging configuration for the entire VoxelWeaver system.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
from logging.handlers import RotatingFileHandler
import json


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output."""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }

    def format(self, record):
        """Format log record with colors."""
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}"
                f"{record.levelname}"
                f"{self.COLORS['RESET']}"
            )
        return super().format(record)


class JSONFormatter(logging.Formatter):
    """Formatter for structured JSON logging."""

    def format(self, record):
        """Format log record as JSON."""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class VoxelWeaverLogger:
    """
    Centralized logging system for VoxelWeaver.

    Provides consistent logging across all modules with support for:
    - Console output (colored)
    - File output (rotating)
    - JSON structured logging
    - Module-specific loggers
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize logger (only once)."""
        if not VoxelWeaverLogger._initialized:
            self.log_dir = Path("logs")
            self.log_dir.mkdir(exist_ok=True)
            self.loggers = {}
            VoxelWeaverLogger._initialized = True

    def setup(
        self,
        level: str = "INFO",
        console: bool = True,
        file: bool = True,
        json_log: bool = False,
        log_file: Optional[str] = None
    ):
        """
        Setup logging configuration.

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            console: Enable console logging
            file: Enable file logging
            json_log: Enable JSON structured logging
            log_file: Custom log file name
        """
        # Get root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, level.upper()))

        # Clear existing handlers
        root_logger.handlers.clear()

        # Console handler
        if console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, level.upper()))
            console_formatter = ColoredFormatter(
                '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)

        # File handler
        if file:
            if log_file is None:
                log_file = f"voxelweaver_{datetime.now().strftime('%Y%m%d')}.log"

            file_path = self.log_dir / log_file
            file_handler = RotatingFileHandler(
                file_path,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)  # File gets all messages
            file_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)-30s | %(funcName)-20s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)

        # JSON handler
        if json_log:
            json_file = self.log_dir / f"voxelweaver_{datetime.now().strftime('%Y%m%d')}.json"
            json_handler = RotatingFileHandler(
                json_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            json_handler.setLevel(logging.DEBUG)
            json_handler.setFormatter(JSONFormatter())
            root_logger.addHandler(json_handler)

        logging.info("VoxelWeaver logging system initialized")

    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger for a specific module.

        Args:
            name: Logger name (usually __name__)

        Returns:
            Configured logger instance
        """
        if name not in self.loggers:
            self.loggers[name] = logging.getLogger(name)
        return self.loggers[name]

    def set_level(self, level: str, module: Optional[str] = None):
        """
        Set log level for root or specific module.

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            module: Optional module name (None for root logger)
        """
        if module:
            logger = self.get_logger(module)
            logger.setLevel(getattr(logging, level.upper()))
        else:
            logging.getLogger().setLevel(getattr(logging, level.upper()))


# Global logger instance
_logger_instance = VoxelWeaverLogger()


def setup_logging(
    level: str = "INFO",
    console: bool = True,
    file: bool = True,
    json_log: bool = False
):
    """
    Setup global logging configuration.

    Args:
        level: Log level
        console: Enable console logging
        file: Enable file logging
        json_log: Enable JSON logging

    Example:
        >>> from utils.logger import setup_logging
        >>> setup_logging(level="DEBUG", console=True, file=True)
    """
    _logger_instance.setup(level, console, file, json_log)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a module.

    Args:
        name: Module name (use __name__)

    Returns:
        Logger instance

    Example:
        >>> from utils.logger import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Hello from module")
    """
    return _logger_instance.get_logger(name)


def set_log_level(level: str, module: Optional[str] = None):
    """
    Change log level dynamically.

    Args:
        level: New log level
        module: Optional module name

    Example:
        >>> from utils.logger import set_log_level
        >>> set_log_level("DEBUG")  # All modules
        >>> set_log_level("WARNING", "voxel_weaver")  # Specific module
    """
    _logger_instance.set_level(level, module)


# Example usage
if __name__ == "__main__":
    # Setup logging
    setup_logging(level="DEBUG", console=True, file=True, json_log=True)

    # Get logger
    logger = get_logger(__name__)

    # Test different log levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

    try:
        1 / 0
    except Exception as e:
        logger.exception("This is an exception with traceback")

    logger.info("Logging system test complete")
