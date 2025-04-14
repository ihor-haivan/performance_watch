# scraper.py

from typing import List, Dict, Any
import logging
from playwright.async_api import BrowserContext, Page
from config import Config


class PerformanceScraper:
    """
    Handles scraping data from performance pages using Playwright.
    """

    @staticmethod
    async def load_page(context: BrowserContext, url: str) -> Page:
        """
        Loads a page using Playwright with a predefined timeout and wait.

        :param context: A Playwright browser context.
        :param url: The URL to navigate to.
        :return: The loaded Page object.
        """
        page = await context.new_page()
        await page.goto(url, timeout=Config.NAVIGATION_TIMEOUT, wait_until="domcontentloaded")
        await page.wait_for_timeout(Config.WAIT_TIMEOUT)
        return page

    @staticmethod
    async def get_show_title(page: Page, logger: logging.Logger) -> str:
        """
        Extracts and returns the show title (from an H1 element) on the page.

        :param page: The loaded Page object.
        :param logger: Logger instance for logging any errors.
        :return: The show title or a fallback string if not found.
        """
        try:
            h1 = await page.query_selector("h1")
            return (await h1.inner_text()).strip() if h1 else "Вистава (назва не знайдена)"
        except Exception as e:
            logger.error(f"Error extracting show title: {e}")
            return "Вистава (назва не знайдена)"

    @staticmethod
    async def get_event_datetime(page: Page, logger: logging.Logger) -> str:
        """
        Tries various selectors to extract the event date and time from the page.

        :param page: The loaded Page object.
        :param logger: Logger instance for logging errors.
        :return: The event date/time string or a default message if not found.
        """
        selectors = [".event-date", ".event-datetime", "time", ".date", ".performance-date", ".event-info span"]
        for sel in selectors:
            try:
                el = await page.query_selector(sel)
                if el:
                    text = (await el.inner_text()).strip()
                    if text:
                        return text
            except Exception as e:
                logger.error(f"Error extracting event datetime using selector '{sel}': {e}")
        return "Дата та час не знайдені"

    @staticmethod
    async def extract_event_links(page: Page, logger: logging.Logger) -> List[str]:
        """
        Extracts event links from the current page by iterating over all anchor tags.

        :param page: The loaded Page object.
        :param logger: Logger instance for logging information.
        :return: A list of extracted event URLs.
        """
        anchors = await page.query_selector_all("a")
        logger.info(f"Found {len(anchors)} links on the page.")
        event_links = set()
        for a in anchors:
            href = await a.get_attribute("href")
            if href and "sales.ft.org.ua/events/" in href:
                full_url = href if href.startswith("http") else f"https://sales.ft.org.ua{href}"
                event_links.add(full_url)
        logger.info(f"Extracted {len(event_links)} event links.")
        return list(event_links)

    @staticmethod
    async def get_fallback_name(performance_url: str) -> str:
        """
        Uses the last segment of the performance URL as a fallback name.

        :param performance_url: The performance URL.
        :return: A fallback show title.
        """
        return performance_url.rstrip("/").split("/")[-1]

    @staticmethod
    async def get_rect_fill_colors(page: Page) -> List[Dict[str, Any]]:
        """
        Executes a script in the page context that extracts the 'fill' attribute
        of all <rect> elements (used to determine seat availability).

        :param page: The loaded Page object.
        :return: A list of dictionaries for each <rect> element found.
        """
        script = """
            () => {
                return Array.from(document.querySelectorAll('rect'))
                            .map((r, i) => ({index: i, color: getComputedStyle(r).fill}));
            }
        """
        return await page.evaluate(script)
