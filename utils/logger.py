import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(service_name: str = "api") -> logging.Logger:
    # Create log directory if it doesn't exist
    if not os.path.exists('log'):
        os.makedirs('log')
    
    # Create a custom logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    # Create handlers (1MB max size, keep 1 backup)
    log_file_path = os.path.join('log', f'{service_name}.log')
    handler = RotatingFileHandler(
        log_file_path,
        maxBytes=1024*1024,  # 1MB
        backupCount=1,
        encoding='utf-8'
    )
    
    # Create formatters and add it to handlers
    formatter = logging.Formatter('%(asctime)s,%(levelname)s,%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    
    # Add handlers to the logger
    logger.addHandler(handler)
    
    # Also log to console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

