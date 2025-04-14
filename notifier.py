# notifier.py

import logging
import requests
from abc import ABC, abstractmethod
from typing import List


class Notifier(ABC):
    """
    Abstract notifier interface.
    Subclasses must implement the send_message method.
    """

    @abstractmethod
    def send_message(self, message: str) -> None:
        """
        Sends a notification message.

        :param message: The message text.
        """
        raise NotImplementedError("This is an interface method.")


class TelegramNotifier(Notifier):
    """
    Concrete notifier that sends Telegram messages.
    """

    def __init__(self, bot_token: str, chat_ids: List[str], logger: logging.Logger) -> None:
        """
        :param bot_token: The Telegram Bot API token.
        :param chat_ids: A list of Telegram chat IDs.
        :param logger: A logger instance for logging errors.
        """
        self.bot_token = bot_token
        self.chat_ids = chat_ids
        self.logger = logger

    def send_message(self, message: str) -> None:
        """
        Sends a Telegram message to all configured chat IDs.

        :param message: The message text.
        """
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        for chat_id in self.chat_ids:
            try:
                requests.post(url, data={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"})
            except Exception as e:
                self.logger.error(f"Error sending message to {chat_id}: {e}")
