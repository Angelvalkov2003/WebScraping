"""Базов скрейпър – всички сайтове наследяват от тук."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ArticleData:
    title: str
    image_url: Optional[str]
    text: str
    source_url: str


class BaseScraper(ABC):
    name: str = "Base"
    domain: str = ""

    @abstractmethod
    def can_handle(self, url: str) -> bool:
        pass

    @abstractmethod
    def scrape(self, url: str) -> ArticleData:
        pass
