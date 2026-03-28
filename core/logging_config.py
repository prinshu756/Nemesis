"""
Logging configuration for Nemesis SOC
"""

import logging
import os
from pathlib import Path

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/nemesis.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('nemesis')
