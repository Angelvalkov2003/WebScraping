"""Base scraper interface - all site scrapers inherit from this."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ArticleData:
    """Extracted article data."""
    title: str
    image_url: Optional[str]
    text: str
    source_url: str


class BaseScraper(ABC):
    """Base class for news site scrapers."""

    name: str = "Base"
    domain: str = ""

    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """Return True if this scraper can handle the given URL."""
        pass

    @abstractmethod
    def scrape(self, url: str) -> ArticleData:
        """Fetch URL and return extracted article data."""
        pass
