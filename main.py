# main.py

import os
import asyncio
import logging

from config import Config
from logger_manager import LoggerManager
from notifier import TelegramNotifier
from monitor import PerformanceMonitor

# Define the performance URLs to monitor in main
PERFORMANCE_URLS = [
    "https://ft.org.ua/performances/sluga-dvox-paniv",
    "https://ft.org.ua/performances/vesillia-figaro"
]


async def start_monitoring(logger_name: str) -> None:
    # Load configuration settings (excluding performance URLs)
    cfg = Config()

    # Setup logger using LoggerManager with the provided logger name.
    logger_manager = LoggerManager(
        logger_name=logger_name,
        log_level=logging.INFO,
        log_file='monitor.log',
        max_bytes=2_000_000,
        backup_count=3
    )
    logger_instance = logger_manager.logger

    # Initialize the notifier with Telegram-specific settings.
    notifier = TelegramNotifier(
        bot_token=cfg.BOT_TOKEN,
        chat_ids=cfg.CHAT_IDS,
        logger=logger_instance
    )

    # Create the performance monitor instance.
    monitor = PerformanceMonitor(
        notifier=notifier,
        config=cfg,
        logger=logger_instance,
        performance_urls=PERFORMANCE_URLS,
        send_notification=False
    )

    # Start the monitoring process.
    await monitor.run_monitoring()

def main() -> None:
    project_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    logger_name = f"{project_name}Logger"

    try:
        asyncio.run(start_monitoring(logger_name))
    except KeyboardInterrupt:
        logger = logging.getLogger(logger_name)
        logger.warning("Monitoring stopped by user.")
    except Exception as e:
        logger = logging.getLogger(logger_name)
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
