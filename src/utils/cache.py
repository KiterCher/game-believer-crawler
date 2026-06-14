"""缓存管理模块"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from loguru import logger


class CacheManager:
    """缓存管理器，支持文件缓存"""

    def __init__(self, cache_dir: str, ttl: int = 3600):
        """
        初始化缓存管理器

        Args:
            cache_dir: 缓存目录
            ttl: 缓存过期时间（秒），默认 1 小时
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(seconds=ttl)
        logger.info(f"CacheManager initialized: dir={cache_dir}, ttl={ttl}s")

    def _get_cache_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        # 将 key 转换为安全的文件名
        safe_key = key.replace("/", "_").replace("\\", "_").replace(":", "_")
        return self.cache_dir / f"{safe_key}.json"

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            logger.debug(f"Cache miss: {key}")
            return None

        # 检查是否过期
        mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
        if datetime.now() - mtime > self.ttl:
            logger.debug(f"Cache expired: {key}")
            cache_path.unlink()
            return None

        # 读取缓存
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.debug(f"Cache hit: {key}")
            return data
        except json.JSONDecodeError as e:
            logger.warning(f"Cache read error: {e}")
            cache_path.unlink()
            return None

    def set(self, key: str, value: Any) -> None:
        """设置缓存"""
        cache_path = self._get_cache_path(key)

        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(value, f, indent=2, ensure_ascii=False)
            logger.debug(f"Cache set: {key}")
        except Exception as e:
            logger.error(f"Cache write error: {e}")

    def delete(self, key: str) -> None:
        """删除缓存"""
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_path.unlink()
            logger.debug(f"Cache deleted: {key}")

    def clear(self) -> int:
        """清空缓存，返回删除的文件数"""
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            count += 1
        logger.info(f"Cache cleared: {count} files deleted")
        return count

    def has(self, key: str) -> bool:
        """检查缓存是否存在且有效"""
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return False

        # 检查是否过期
        mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
        if datetime.now() - mtime > self.ttl:
            cache_path.unlink()
            return False

        return True

    def get_stats(self) -> dict:
        """获取缓存统计信息"""
        files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in files)

        return {
            "count": len(files),
            "total_size": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
        }
