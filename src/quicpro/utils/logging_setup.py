"""
Logging setup module.
Configures root logging for the application.
"""

import logging
import sys


def setup_logging(level=logging.DEBUG):
    """
    Configure logging with the given level.
    """
    logger = logging.getLogger()
    logger.setLevel(level)
    if logger.hasHandlers():
        logger.handlers.clear()
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logging.info("Logging is configured with level %s",
                 logging.getLevelName(level))
