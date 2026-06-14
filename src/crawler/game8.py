"""game8.co 爬虫"""

from typing import Any

from .base import BaseCrawler


class Game8Crawler(BaseCrawler):
    """game8.co 数据爬虫"""

    async def crawl_characters(self) -> list[dict[str, Any]]:
        # TODO: 实现角色爬取
        return []

    async def crawl_lightcones(self) -> list[dict[str, Any]]:
        # TODO: 实现光锥爬取
        return []

    async def crawl_relics(self) -> list[dict[str, Any]]:
        # TODO: 实现遗器爬取
        return []

    async def crawl_single_character(self, slug: str) -> dict[str, Any]:
        # TODO: 实现单个角色爬取
        return {}
