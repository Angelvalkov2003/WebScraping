"""Регистър на скрейпери – добавяне на нови сайтове тук."""
from typing import List, Optional

from .base import BaseScraper
from .nova_bg import NovaBgScraper
from .twelve_punto import TwelvePuntoScraper

SCRAPERS: List[BaseScraper] = [
    TwelvePuntoScraper(),
    NovaBgScraper(),
]


def get_scraper_for_url(url: str) -> Optional[BaseScraper]:
    for scraper in SCRAPERS:
        if scraper.can_handle(url):
            return scraper
    return None


def get_scraper_by_name(name: str) -> Optional[BaseScraper]:
    for scraper in SCRAPERS:
        if scraper.name == name:
            return scraper
    return None


def get_available_sites() -> List[str]:
    return [s.name for s in SCRAPERS]
