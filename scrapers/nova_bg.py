"""Scraper for nova.bg (Nova TV) news articles."""
import re
from typing import Optional

import requests
from bs4 import BeautifulSoup

from .base import ArticleData, BaseScraper


class NovaBgScraper(BaseScraper):


    name = "Nova TV"
    domain = "nova.bg"

    def can_handle(self, url: str) -> bool:
        return "nova.bg" in url

    def scrape(self, url: str) -> ArticleData:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "bg,en;q=0.9",
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        title = self._extract_title(soup)
        image_url = self._extract_image(soup, url)
        text = self._extract_text(soup)

        return ArticleData(
            title=title or "",
            image_url=image_url,
            text=text or "",
            source_url=url,
        )

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        meta = soup.find("meta", property="og:title")
        if meta and meta.get("content"):
            return meta["content"].strip()
        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)
        title_tag = soup.find("title")
        if title_tag:
            return title_tag.get_text(strip=True)
        return None

    def _extract_image(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        meta = soup.find("meta", property="og:image")
        if meta and meta.get("content"):
            url = meta["content"].strip()
            if url.startswith("//"):
                url = "https:" + url
            elif url.startswith("/"):
                url = "https://nova.bg" + url
            return url
        article = soup.find("article") or soup.find("div", class_=re.compile(r"article|content|post", re.I))
        if article:
            img = article.find("img", src=True)
            if img and img.get("src"):
                url = img["src"].strip()
                if url.startswith("//"):
                    url = "https:" + url
                elif url.startswith("/"):
                    url = "https://nova.bg" + url
                return url
        return None

    def _extract_text(self, soup: BeautifulSoup) -> Optional[str]:
        selectors = [
            "article .content",
            "article .article-body",
            "article .entry-content",
            ".article-content",
            ".post-content",
            ".news-content",
            ".news-article__content",
            ".article__body",
            "[itemprop='articleBody']",
            "article",
        ]
        for sel in selectors:
            el = soup.select_one(sel)
            if not el:
                continue
            clone = BeautifulSoup(str(el), "html.parser")
            for tag in clone.find_all(["script", "style", "nav", "aside", "iframe"]):
                tag.decompose()
            paragraphs = clone.find_all("p")
            if paragraphs:
                texts = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
                if texts:
                    return "\n\n".join(texts)
            text = clone.get_text(separator="\n", strip=True)
            if len(text) > 100:
                return text

        main = soup.find("main") or soup.find("div", id=re.compile(r"content|main", re.I))
        if main:
            paragraphs = main.find_all("p")
            texts = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
            if texts:
                return "\n\n".join(texts)
        return None
