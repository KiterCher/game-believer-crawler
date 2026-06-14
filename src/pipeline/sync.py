"""数据同步模块 - 将爬取的数据同步到 GameBeliever-web"""

import json
import shutil
from pathlib import Path
from typing import Any, Optional

from loguru import logger


class DataSync:
    """数据同步器"""

    def __init__(self, crawler_data_dir: str, web_data_dir: str, web_images_dir: str):
        """
        初始化数据同步器

        Args:
            crawler_data_dir: 爬虫数据目录 (GameBeliever-crawler/data/processed)
            web_data_dir: 网站数据目录 (GameBeliever-web/src/data)
            web_images_dir: 网站图片目录 (GameBeliever-web/public/images)
        """
        self.crawler_data_dir = Path(crawler_data_dir)
        self.web_data_dir = Path(web_data_dir)
        self.web_images_dir = Path(web_images_dir)

        # 确保目录存在
        self.web_data_dir.mkdir(parents=True, exist_ok=True)
        self.web_images_dir.mkdir(parents=True, exist_ok=True)

    def sync_characters(self) -> dict[str, Any]:
        """同步角色数据"""
        logger.info("Syncing character data...")

        crawler_chars_dir = self.crawler_data_dir / "characters"
        web_chars_dir = self.web_data_dir / "characters"

        if not crawler_chars_dir.exists():
            logger.warning(f"Crawler characters directory not found: {crawler_chars_dir}")
            return {"synced": 0, "skipped": 0, "errors": 0}

        web_chars_dir.mkdir(parents=True, exist_ok=True)

        stats = {"synced": 0, "skipped": 0, "errors": 0}

        for json_file in crawler_chars_dir.glob("*.json"):
            if json_file.name.startswith("_"):
                continue  # 跳过列表文件

            slug = json_file.stem
            web_file = web_chars_dir / f"{slug}.json"

            try:
                # 检查是否需要更新
                if web_file.exists():
                    # 比较修改时间
                    crawler_mtime = json_file.stat().st_mtime
                    web_mtime = web_file.stat().st_mtime

                    if crawler_mtime <= web_mtime:
                        logger.debug(f"Skipping {slug} (already up to date)")
                        stats["skipped"] += 1
                        continue

                # 读取并转换数据
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # 转换为网站格式
                web_data = self._convert_character_data(data)

                # 保存到网站目录
                with open(web_file, "w", encoding="utf-8") as f:
                    json.dump(web_data, f, indent=2, ensure_ascii=False)

                logger.info(f"Synced character: {slug}")
                stats["synced"] += 1

            except Exception as e:
                logger.error(f"Failed to sync {slug}: {e}")
                stats["errors"] += 1

        logger.info(f"Character sync complete: {stats}")
        return stats

    def sync_lightcones(self) -> dict[str, Any]:
        """同步光锥数据"""
        logger.info("Syncing lightcone data...")

        crawler_lc_dir = self.crawler_data_dir / "lightcones"
        web_lc_dir = self.web_data_dir / "lightcones"

        if not crawler_lc_dir.exists():
            logger.warning(f"Crawler lightcones directory not found: {crawler_lc_dir}")
            return {"synced": 0, "skipped": 0, "errors": 0}

        web_lc_dir.mkdir(parents=True, exist_ok=True)

        stats = {"synced": 0, "skipped": 0, "errors": 0}

        for json_file in crawler_lc_dir.glob("*.json"):
            if json_file.name.startswith("_"):
                continue

            slug = json_file.stem
            web_file = web_lc_dir / f"{slug}.json"

            try:
                if web_file.exists():
                    crawler_mtime = json_file.stat().st_mtime
                    web_mtime = web_file.stat().st_mtime

                    if crawler_mtime <= web_mtime:
                        stats["skipped"] += 1
                        continue

                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                web_data = self._convert_lightcone_data(data)

                with open(web_file, "w", encoding="utf-8") as f:
                    json.dump(web_data, f, indent=2, ensure_ascii=False)

                logger.info(f"Synced lightcone: {slug}")
                stats["synced"] += 1

            except Exception as e:
                logger.error(f"Failed to sync lightcone {slug}: {e}")
                stats["errors"] += 1

        logger.info(f"Lightcone sync complete: {stats}")
        return stats

    def sync_images(self, image_type: str) -> dict[str, Any]:
        """同步图片"""
        logger.info(f"Syncing {image_type} images...")

        crawler_images_dir = self.crawler_data_dir / "images" / image_type
        web_images_type_dir = self.web_images_dir / image_type

        if not crawler_images_dir.exists():
            logger.warning(f"Crawler images directory not found: {crawler_images_dir}")
            return {"synced": 0, "skipped": 0, "errors": 0}

        web_images_type_dir.mkdir(parents=True, exist_ok=True)

        stats = {"synced": 0, "skipped": 0, "errors": 0}

        for item_dir in crawler_images_dir.iterdir():
            if not item_dir.is_dir():
                continue

            slug = item_dir.name
            web_item_dir = web_images_type_dir / slug

            try:
                if web_item_dir.exists():
                    # 检查文件数量
                    crawler_files = list(item_dir.glob("*"))
                    web_files = list(web_item_dir.glob("*"))

                    if len(crawler_files) == len(web_files):
                        stats["skipped"] += 1
                        continue

                # 复制图片
                shutil.copytree(item_dir, web_item_dir, dirs_exist_ok=True)

                logger.info(f"Synced images for: {slug}")
                stats["synced"] += 1

            except Exception as e:
                logger.error(f"Failed to sync images for {slug}: {e}")
                stats["errors"] += 1

        logger.info(f"Image sync complete: {stats}")
        return stats

    def _convert_character_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """转换角色数据为网站格式"""
        # 确保必要的字段存在
        return {
            "id": data.get("id", ""),
            "name": data.get("name", ""),
            "nameEn": data.get("nameEn", ""),
            "rarity": data.get("rarity", 5),
            "element": data.get("element", "Physical"),
            "path": data.get("path", "Destruction"),
            "faction": data.get("faction", ""),
            "releaseVersion": data.get("releaseVersion", ""),
            "description": data.get("description", ""),
            "role": data.get("role", ""),
            "tags": data.get("tags", []),
            "skills": data.get("skills", []),
            "traces": data.get("traces", []),
            "eidolons": data.get("eidolons", []),
            "stats": data.get("stats", {}),
            "images": data.get("images", {}),
        }

    def _convert_lightcone_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """转换光锥数据为网站格式"""
        return {
            "id": data.get("id", ""),
            "name": data.get("name", ""),
            "nameEn": data.get("nameEn", ""),
            "rarity": data.get("rarity", 4),
            "path": data.get("path", "Destruction"),
            "stats": data.get("stats", {}),
            "passive": data.get("passive", {}),
            "images": data.get("images", {}),
        }

    def get_sync_status(self) -> dict[str, Any]:
        """获取同步状态"""
        status = {
            "crawler": {
                "characters": 0,
                "lightcones": 0,
                "relics": 0,
            },
            "web": {
                "characters": 0,
                "lightcones": 0,
            },
        }

        # 统计爬虫数据
        crawler_chars_dir = self.crawler_data_dir / "characters"
        if crawler_chars_dir.exists():
            status["crawler"]["characters"] = len(list(crawler_chars_dir.glob("*.json"))) - 1  # 减去列表文件

        crawler_lc_dir = self.crawler_data_dir / "lightcones"
        if crawler_lc_dir.exists():
            status["crawler"]["lightcones"] = len(list(crawler_lc_dir.glob("*.json"))) - 1

        # 统计网站数据
        web_chars_dir = self.web_data_dir / "characters"
        if web_chars_dir.exists():
            status["web"]["characters"] = len(list(web_chars_dir.glob("*.json")))

        web_lc_dir = self.web_data_dir / "lightcones"
        if web_lc_dir.exists():
            status["web"]["lightcones"] = len(list(web_lc_dir.glob("*.json")))

        return status
