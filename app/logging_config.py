from logging.config import dictConfig
import os


def setup_logging():
    os.makedirs("logs", exist_ok=True)

    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(name)s: %(message)s"
            }
        },
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "filename": "logs/app.log",
                "formatter": "default",
                "level": "INFO",
            },
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": "DEBUG",
            }
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["file", "console"]
        },
        "loggers": {
            "sqlalchemy.engine": {
                "level": "INFO",
                "handlers": ["file", "console"],
                "propagate": False
            }
        }
    })