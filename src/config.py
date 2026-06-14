"""配置管理模块"""

import os
from pathlib import Path
from typing import Optional

import yaml
from loguru import logger
from pydantic import BaseModel


class DataSourceConfig(BaseModel):
    """数据源配置"""

    name: str
    base_url: str
    enabled: bool = True
    rate_limit: float = 1.0  # 请求间隔（秒）
    timeout: int = 30


class CrawlerConfig(BaseModel):
    """爬虫配置"""

    # 数据源
    sources: dict[str, DataSourceConfig] = {}

    # 输出配置
    output_dir: str = "../GameBeliever-web/src/data"
    raw_dir: str = "./data/raw"
    processed_dir: str = "./data/processed"
    images_dir: str = "./data/images"

    # 爬虫配置
    max_retries: int = 3
    concurrency: int = 5
    user_agent: str = "GameBeliever Crawler/0.1.0"

    # 缓存配置
    cache_enabled: bool = True
    cache_dir: str = "./data/cache"
    cache_ttl: int = 3600  # 1小时


# 默认配置
DEFAULT_CONFIG = CrawlerConfig(
    sources={
        "prydwen": DataSourceConfig(
            name="prydwen",
            base_url="https://prydwen.gg/star-rail",
            rate_limit=1.0,
        ),
        "game8": DataSourceConfig(
            name="game8",
            base_url="https://game8.co/games/Honkai-Star-Rail",
            rate_limit=2.0,
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
    if config_path and Path(config_path).exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)

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
