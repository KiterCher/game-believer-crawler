"""配置管理模块"""

import os
from pathlib import Path
from typing import Optional

import yaml
from loguru import logger
from pydantic import BaseModel


class SiteConfig(BaseModel):
    """网站配置"""

    name: str
    base_url: str
    enabled: bool = True
    rate_limit: float = 1.0  # 请求间隔（秒）
    timeout: int = 30
    crawl_types: list[str] = ["characters", "lightcones", "relics"]  # 爬取类型


class ScheduleConfig(BaseModel):
    """定时任务配置"""

    interval_minutes: int = 5
    enabled: bool = True


class CrawlerConfig(BaseModel):
    """爬虫配置"""

    # 网站配置（支持多个网站）
    sites: dict[str, SiteConfig] = {}

    # 输出配置
    output_dir: str = "../GameBeliever-web/src/data"
    images_dir: str = "../GameBeliever-web/public/images"
    raw_dir: str = "./data/raw"
    processed_dir: str = "./data/processed"

    # 爬虫配置
    max_retries: int = 3
    concurrency: int = 5
    user_agent: str = "GameBeliever Crawler/0.1.0"

    # 缓存配置
    cache_enabled: bool = True
    cache_dir: str = "./data/cache"
    cache_ttl: int = 3600  # 1小时

    # 定时任务配置
    schedule: ScheduleConfig = ScheduleConfig()

    def get_enabled_sites(self) -> dict[str, SiteConfig]:
        """获取所有启用的网站"""
        return {name: site for name, site in self.sites.items() if site.enabled}

    def get_site_config(self, site_name: str) -> Optional[SiteConfig]:
        """获取指定网站配置"""
        return self.sites.get(site_name)


# 默认配置
DEFAULT_CONFIG = CrawlerConfig(
    sites={
        "prydwen": SiteConfig(
            name="prydwen",
            base_url="https://prydwen.gg/star-rail",
            rate_limit=1.0,
            crawl_types=["characters", "lightcones", "relics"],
        ),
    }
)


def load_config(config_path: Optional[str] = None) -> CrawlerConfig:
    """
    加载配置

    Args:
        config_path: 配置文件路径（可选）

    Returns:
        CrawlerConfig: 配置对象
    """
    # 默认配置文件路径
    if config_path is None:
        config_path = "config/settings.yaml"

    config_file = Path(config_path)

    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)

            # 转换 sites 配置
            if "sites" in config_data:
                sites = {}
                for name, site_data in config_data["sites"].items():
                    if isinstance(site_data, dict):
                        sites[name] = SiteConfig(**site_data)
                config_data["sites"] = sites

            # 转换 schedule 配置
            if "schedule" in config_data and isinstance(config_data["schedule"], dict):
                config_data["schedule"] = ScheduleConfig(**config_data["schedule"])

            logger.info(f"Config loaded from: {config_path}")
            return CrawlerConfig(**config_data)

        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {e}")
            logger.info("Using default config")

    # 检查环境变量
    output_dir = os.getenv("CRAWLER_OUTPUT_DIR")
    if output_dir:
        config = DEFAULT_CONFIG.copy()
        config.output_dir = output_dir
        return config

    return DEFAULT_CONFIG
