"""
src/utils.py
------------
Shared utilities: logging, domain extraction, config loading, rate limiting.
"""

import os
import logging
import yaml
import time
from logging.handlers import RotatingFileHandler
from ratelimit import limits, sleep_and_retry
import requests

# Logs setup
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOGS_DIR, "pipeline.log")

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s | %(message)s')
    # Console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    # File (rotating)
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=10*1024*1024, backupCount=5)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    return logger

def get_domain(url: str) -> str:
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return parsed.netloc or parsed.path.split('/')[0]

def load_websites(config_path: str) -> list:
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config.get('websites', [])

@sleep_and_retry
@limits(calls=60, period=60)  # 60 req/min
def rate_limited_request(url: str, **kwargs) -> requests.Response:
    return requests.get(url, **kwargs)