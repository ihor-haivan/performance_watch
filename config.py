# config.py

import os
from typing import List
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

class Config:
    """
    Holds configuration constants except for logging.
    Sensitive or deployment-specific settings come from .env file.
    """

    # Telegram bot settings (loaded from .env)
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    CHAT_IDS: List[str] = os.getenv("CHAT_IDS", "").split(",")

    # Colors to be ignored when checking for free seats
    IGNORED_COLORS: set = {"rgb(173, 173, 173)", "rgb(255, 255, 255)"}

    # Timing configurations
    SLEEP_INTERVAL: int = 10       # Seconds between monitoring cycles
    MIN_CHECK_INTERVAL: int = 5    # Minimal wait in seconds between full checks

    # Playwright page load timeouts (in milliseconds)
    NAVIGATION_TIMEOUT: int = 60000  # 60 seconds
    WAIT_TIMEOUT: int = 1000         # 1 second
