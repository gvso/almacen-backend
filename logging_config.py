import logging
import logging.config
from typing import Any

from pythonjsonlogger import jsonlogger

from app_settings import settings
from environment import Environment

JSON_FORMAT = (
    "%(module)s %(asctime)s %(levelname)s %(thread)d %(processName)s %(task_name)s %(task_id)s %(name)s "
    "%(funcName)s %(filename)s %(lineno)d %(message)s"
)
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "jsonFormat": {
            "format": JSON_FORMAT,
            "class": "logging_config.CustomJsonFormatter",
        },
        "standardFormat": {
            "format": (
                "%(asctime)s %(levelname)s %(thread)d %(processName)s [%(name)s] [%(funcName)s] "
                "[%(filename)s:%(lineno)d] - %(message)s"
            )
        },
        "standardTaskFormat": {
            "format": (
                "%(asctime)s %(levelname)s %(thread)d %(processName)s %(task_name)s [%(task_id)s] [%(name)s] "
                "[%(funcName)s] [%(filename)s:%(lineno)d] - %(message)s"
            )
        },
    },
    "handlers": {
        "jsonStreamHandler": {
            "formatter": "jsonFormat",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # Default is stderr
        }
    },
    "loggers": {
        "": {
            "handlers": ["jsonStreamHandler"],
            "level": settings.logging.level,
            "propagate": False,
        },
    },
}
LOCAL_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "default": {
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # Default is stderr
        },
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": settings.logging.level,
            "propagate": False,
        },
        "werkzeug": {"handlers": ["default"], "propagate": False},
        "connectionpool": {
            "handlers": ["default"],
            "level": settings.logging.level,
            "propagate": False,
        },
        "requests_oauthlib": {
            "handlers": ["default"],
            "level": settings.logging.level,
            "propagate": False,
        },
        "faker": {
            "handlers": ["default"],
            "level": settings.logging.level,
            "propagate": False,
        },
        "urllib3": {
            "handlers": ["default"],
            "level": settings.logging.level,
            "propagate": False,
        },
        "PIL": {
            "handlers": ["default"],
            "level": settings.logging.level,
            "propagate": False,
        },
        "httpx": {
            "handlers": ["default"],
            "level": settings.logging.level,
            "propagate": False,
        },
    },
}


# Used because we add custom local formatting.
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._app_env = settings.environment
        self._pretty_format = settings.logging.use_pretty_json
        # For local development we want to make logs more clear
        if self._app_env == Environment.DEVELOPMENT and self._pretty_format:
            self.json_indent = 2

    def format(self, record: logging.LogRecord) -> str:
        result = super(CustomJsonFormatter, self).format(record)
        # For local development we want to make logs more clear.
        if self._app_env == Environment.DEVELOPMENT and self._pretty_format:
            result = result.replace("\\n", "\n\t\t")
        return result


def setup_logging() -> None:
    if (
        settings.environment == Environment.DEVELOPMENT
        or settings.environment == Environment.TEST
    ):
        logging.config.dictConfig(LOCAL_LOGGING_CONFIG)
        logging.captureWarnings(True)
        logging.disable(logging.NOTSET)
    if settings.logging.use_config is True:
        """Setup root logger using our logging config"""
        logging.config.dictConfig(LOGGING_CONFIG)
        logging.captureWarnings(True)
        logging.disable(logging.NOTSET)
