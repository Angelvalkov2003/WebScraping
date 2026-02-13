"""Registry of scrapers - add new scrapers here for different sites."""
from typing import List, Optional

from .base import BaseScraper
from .nova_bg import NovaBgScraper
from .twelve_punto import TwelvePuntoScraper

# All available scrapers (add new ones here)
SCRAPERS: List[BaseScraper] = [
    TwelvePuntoScraper(),
    NovaBgScraper(),
]


def get_scraper_for_url(url: str) -> Optional[BaseScraper]:
    """Return the first scraper that can handle the URL."""
    for scraper in SCRAPERS:
        if scraper.can_handle(url):
            return scraper
    return None


def get_scraper_by_name(name: str) -> Optional[BaseScraper]:
    """Return scraper by display name."""
    for scraper in SCRAPERS:
        if scraper.name == name:
            return scraper
    return None


def get_available_sites() -> List[str]:
    """Return list of site names for the GUI dropdown."""
    return [s.name for s in SCRAPERS]
