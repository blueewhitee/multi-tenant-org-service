import logging
import sys
from app.core.config import settings

def setup_logging():
    """
    Setup the logging configuration.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.
    """
    return logging.getLogger(name)
