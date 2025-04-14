# tests/test_monitor.py

import asyncio
import logging
import pytest

from monitor import PerformanceMonitor
from config import Config
from notifier import Notifier

# Create a dummy notifier that simply records any messages sent.
class DummyNotifier(Notifier):
    def __init__(self):
        self.messages = []

    def send_message(self, message: str) -> None:
        self.messages.append(message)

@pytest.mark.asyncio
async def test_get_all_event_links(monkeypatch):
    """
    Test that get_all_event_links correctly aggregates event links.
    """

    cfg = Config()
    logger = logging.getLogger("test_monitor")
    dummy_notifier = DummyNotifier()
    performance_urls = ["http://example.com/performance1"]

    monitor = PerformanceMonitor(
        notifier=dummy_notifier,
        config=cfg,
        logger=logger,
        performance_urls=performance_urls,
        send_notification=False
    )

    # Monkey-patch get_event_links_for_perf to return a dummy link.
    async def dummy_get_event_links_for_perf(context, perf_url, logger):
        return [("http://example.com/event1", perf_url)]
    monkeypatch.setattr(monitor, "get_event_links_for_perf", dummy_get_event_links_for_perf)

    event_links = await monitor.get_all_event_links(context=None)
    assert len(event_links) == 1
    assert event_links[0][0] == "http://example.com/event1"
    assert event_links[0][1] == "http://example.com/performance1"

@pytest.mark.asyncio
async def test_check_event(monkeypatch):
    """
    Test check_event by replacing the scraper methods with dummy implementations.
    """

    cfg = Config()
    logger = logging.getLogger("test_monitor")
    dummy_notifier = DummyNotifier()
    performance_urls = ["http://example.com/performance1"]
    monitor = PerformanceMonitor(
        notifier=dummy_notifier,
        config=cfg,
        logger=logger,
        performance_urls=performance_urls,
        send_notification=False
    )

    # Create a dummy page object that simulates a minimal Playwright Page.
    class DummyPage:
        async def goto(self, url, timeout, wait_until):
            pass
        async def wait_for_timeout(self, timeout):
            pass
        async def evaluate(self, script):
            # Simulate two rect elements:
            # One with a free seat color (not ignored) and one with an ignored color.
            return [
                {"index": 0, "color": "rgb(0, 0, 0)"},   # Free seat (assumed free)
                {"index": 1, "color": "rgb(255, 255, 255)"}  # Ignored seat (per Config.IGNORED_COLORS)
            ]
        async def close(self):
            pass

    # Dummy implementation for the scraper functions:
    async def dummy_load_page(context, url):
        return DummyPage()
    async def dummy_get_show_title(page, logger):
        return "Test Show"
    async def dummy_get_event_datetime(page, logger):
        return "2025-01-01 20:00"
    async def dummy_extract_event_links(page, logger):
        return []
    async def dummy_get_fallback_name(performance_url):
        return "Fallback Show"
    async def dummy_get_rect_fill_colors(page):
        return await page.evaluate(None)

    # Monkey-patch the PerformanceScraper methods used by check_event.
    from scraper import PerformanceScraper
    monkeypatch.setattr(PerformanceScraper, "load_page", dummy_load_page)
    monkeypatch.setattr(PerformanceScraper, "get_show_title", dummy_get_show_title)
    monkeypatch.setattr(PerformanceScraper, "get_event_datetime", dummy_get_event_datetime)
    monkeypatch.setattr(PerformanceScraper, "extract_event_links", dummy_extract_event_links)
    monkeypatch.setattr(PerformanceScraper, "get_fallback_name", dummy_get_fallback_name)
    monkeypatch.setattr(PerformanceScraper, "get_rect_fill_colors", dummy_get_rect_fill_colors)

    # Call check_event on a dummy event URL.
    await monitor.check_event(context=None, event_url="http://example.com/event1", performance_url="http://example.com/performance1")

    # Since send_notification is disabled (send_notification=False), no message should be sent.
    # Even though a free seat is detected ("rgb(0, 0, 0)" is not in IGNORED_COLORS).
    assert len(dummy_notifier.messages) == 0
