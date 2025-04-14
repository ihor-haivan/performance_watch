# monitor.py

import asyncio
import time
import logging
from typing import Dict, List, Tuple

from playwright.async_api import async_playwright, BrowserContext

from config import Config
from notifier import Notifier
from scraper import PerformanceScraper

class PerformanceMonitor:
    """
    Orchestrates monitoring for performance pages:
      - Collects event links concurrently.
      - Checks event pages for free seats.
      - Optionally sends notifications when free seats are detected.
    """
    def __init__(self, notifier: Notifier, config: Config, logger: logging.Logger,
                 performance_urls: List[str], send_notification: bool = False) -> None:
        """
        :param notifier: An instance of Notifier for sending alerts.
        :param config: An instance of Config for general configurations.
        :param logger: A configured logger.
        :param performance_urls: List of performance page URLs to monitor.
        :param send_notification: If True, notifications are sent when free seats are detected.
        """
        self.notifier = notifier
        self.config = config
        self.logger = logger
        self.performance_urls = performance_urls
        self.send_notification = send_notification
        self.previous_free_rects_by_url: Dict[str, set] = {}
        self._last_check_time: float = 0.0

    @staticmethod
    async def get_event_links_for_perf(context: BrowserContext, perf_url: str, logger: logging.Logger) -> List[Tuple[str, str]]:
        try:
            page = await PerformanceScraper.load_page(context, perf_url)
            links = await PerformanceScraper.extract_event_links(page, logger)
            await page.close()
            return [(link, perf_url) for link in links]
        except Exception as e:
            logger.error(f"Error extracting event links for {perf_url}: {e}")
            return []

    async def get_all_event_links(self, context: BrowserContext) -> List[Tuple[str, str]]:
        tasks = [
            self.get_event_links_for_perf(context, perf_url, self.logger)
            for perf_url in self.performance_urls
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        event_links: List[Tuple[str, str]] = []
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Error in concurrent event link extraction: {result}")
            else:
                event_links.extend(result)
        return event_links

    async def check_event(self, context: BrowserContext, event_url: str, performance_url: str) -> None:
        page = await context.new_page()
        try:
            await page.goto(event_url, timeout=self.config.NAVIGATION_TIMEOUT, wait_until="domcontentloaded")
            await page.wait_for_timeout(self.config.WAIT_TIMEOUT)

            # Retrieve the show title and use fallback if necessary.
            show_title = await PerformanceScraper.get_show_title(page, self.logger)
            if show_title == "Вистава (назва не знайдена)":
                show_title = await PerformanceScraper.get_fallback_name(performance_url)

            event_datetime = await PerformanceScraper.get_event_datetime(page, self.logger)
            rect_fill_colors = await PerformanceScraper.get_rect_fill_colors(page)
            self.logger.info(f"Event: {event_url} — found {len(rect_fill_colors)} rect elements.")

            # Identify free seat elements based on their color.
            free_rects = {f"rect_{item['index']}_{item['color'].lower()}"
                          for item in rect_fill_colors
                          if item["color"] and item["color"].lower() not in self.config.IGNORED_COLORS}

            previous = self.previous_free_rects_by_url.get(event_url, set())
            new_seats = free_rects - previous

            if new_seats:
                msg = (
                    f"\n🎭 *{show_title}*"
                    f"\n🕒 {event_datetime}"
                    f"\n🎟 Нові вільні місця: {len(new_seats)}"
                    f"\n🔗 [Перейти до події]({event_url})"
                )
                self.logger.info(f"New seats found for {show_title}: {len(new_seats)}")
                self.logger.info(msg)
                if self.send_notification:
                    self.notifier.send_message(msg)

            self.previous_free_rects_by_url[event_url] = free_rects

        except Exception as e:
            self.logger.error(f"Error checking event {event_url}: {e}")
        finally:
            await page.close()

    async def run_monitoring(self) -> None:
        self.logger.info("🎭 Monitoring started.")
        if self.send_notification:
            self.notifier.send_message("🎭 Monitoring multiple performances started.")
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context()

            while True:
                elapsed = time.time() - self._last_check_time
                if elapsed < self.config.MIN_CHECK_INTERVAL:
                    await asyncio.sleep(self.config.MIN_CHECK_INTERVAL - elapsed)
                self._last_check_time = time.time()

                try:
                    event_links = await self.get_all_event_links(context)
                    if event_links:
                        tasks = [
                            self.check_event(context, link, perf_url)
                            for (link, perf_url) in event_links
                        ]
                        await asyncio.gather(*tasks, return_exceptions=True)
                except Exception as e:
                    self.logger.error(f"Error in main monitoring loop: {e}")

                await asyncio.sleep(self.config.SLEEP_INTERVAL)
