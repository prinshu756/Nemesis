import logging
import logging.handlers
import os
from core.config import config

def setup_logging():
    """Setup comprehensive logging for the system"""
    log_config = config.get('logging', {})

    # Create logs directory
    os.makedirs(os.path.dirname(log_config.get('file', 'logs/nemesis.log')), exist_ok=True)

    # Create logger
    logger = logging.getLogger('nemesis')
    logger.setLevel(getattr(logging, log_config.get('level', 'INFO')))

    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_config.get('file', 'logs/nemesis.log'),
        maxBytes=log_config.get('max_size', 10485760),
        backupCount=log_config.get('backup_count', 5)
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

# Global logger instance
logger = setup_logging()