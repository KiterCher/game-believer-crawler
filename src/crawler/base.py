"""爬虫基类"""

from abc import ABC, abstractmethod
from typing import Any

from ..config import CrawlerConfig, DataSourceConfig


class BaseCrawler(ABC):
    """爬虫基类，所有爬虫必须继承此类"""

    def __init__(self, config: CrawlerConfig, source_config: DataSourceConfig):
        self.config = config
        self.source_config = source_config
        self.session = None

    @abstractmethod
    async def crawl_characters(self) -> list[dict[str, Any]]:
        """爬取角色数据"""
        pass

    @abstractmethod
    async def crawl_lightcones(self) -> list[dict[str, Any]]:
        """爬取光锥数据"""
        pass

    @abstractmethod
    async def crawl_relics(self) -> list[dict[str, Any]]:
        """爬取遗器数据"""
        pass

    @abstractmethod
    async def crawl_single_character(self, slug: str) -> dict[str, Any]:
        """爬取单个角色数据"""
        pass

    async def start(self):
        """启动爬虫"""
        # TODO: 初始化 HTTP 会话
        pass

    async def stop(self):
        """停止爬虫"""
        # TODO: 关闭 HTTP 会话
        pass
