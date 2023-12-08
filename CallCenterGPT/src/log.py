import logging
from os import environ

log = logging.getLogger("app")


def setup_logger():
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - [%(name)s] - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    log.addHandler(ch)
    log.setLevel(environ.get("LOG_LEVEL", "INFO").upper())
