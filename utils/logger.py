import logging
import os
from datetime import datetime
from logging import Logger

def setup_logger() -> Logger:   
    LOG_NAME = 'AtlasScout'
    LOG_DIRECTORY = 'data/logs'

    # Ensure log directory exists
    os.makedirs(LOG_DIRECTORY, exist_ok=True)

    # Generate log filename with timestamp
    date_str = datetime.now().strftime('%Y%m%d')
    log_filename = os.path.join(LOG_DIRECTORY, f"{LOG_NAME}_{date_str}.log")

    # Configure logging
    logger = logging.getLogger(LOG_NAME)
    logger.setLevel(logging.DEBUG)

    # Avoid duplicate handlers (important for repeated calls)
    if logger.hasHandlers():
        return logger

     # File Handler (captures all logs)
    file_handler = logging.FileHandler(log_filename, mode='a')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    # Console Handler (INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info(f"Logger initialized - log file: {log_filename}")
    return logger

# Create and configure the logger
logger = setup_logger()