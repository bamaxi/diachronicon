from typing import Dict

import logging
from logging.config import dictConfig
from pathlib import Path


def init_logger(logging_file: str, loggingConfig: Dict[str, str]):
    # create logging dir if needed
    path = Path(logging_file)
    path.parent.mkdir(parents=True, exist_ok=True)

    dictConfig(loggingConfig)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    return logger
