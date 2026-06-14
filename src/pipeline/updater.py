"""自动更新模块 - 检查并更新数据"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from loguru import logger

from ..crawler.prydwen import PrydwenCrawler
from ..config import load_config, CrawlerConfig
from .sync import DataSync


class AutoUpdater:
    """自动更新器"""

    def __init__(self, config: CrawlerConfig):
        self.config = config
        self.crawler = None
        self.sync = None
        self.status_file = Path(config.cache_dir) / "update_status.json"

    async def start(self):
        """启动更新器"""
        # 获取第一个启用的网站配置
        enabled_sites = self.config.get_enabled_sites()
        if not enabled_sites:
            logger.error("No enabled sites configured")
            return

        site_name = list(enabled_sites.keys())[0]
        site_config = enabled_sites[site_name]

        self.crawler = PrydwenCrawler(self.config, site_config)
        self.sync = DataSync(
            crawler_data_dir=self.config.processed_dir,
            web_data_dir=self.config.output_dir,
            web_images_dir=self.config.images_dir,
        )

        await self.crawler.start()

    async def stop(self):
        """停止更新器"""
        if self.crawler:
            await self.crawler.stop()

    def check_updates_needed(self) -> dict[str, Any]:
        """检查是否需要更新"""
        logger.info("Checking for updates...")

        status = self.sync.get_sync_status()
        update_needed = {
            "characters": status["crawler"]["characters"] > status["web"]["characters"],
            "lightcones": status["crawler"]["lightcones"] > status["web"]["lightcones"],
            "full_sync": False,
        }

        # 检查是否有新数据
        if update_needed["characters"] or update_needed["lightcones"]:
            update_needed["full_sync"] = True

        logger.info(f"Update status: {status}")
        logger.info(f"Update needed: {update_needed}")

        return update_needed

    async def update_characters(self, force: bool = False) -> dict[str, Any]:
        """更新角色数据"""
        logger.info("Updating characters...")

        try:
            # 爬取角色列表
            characters = await self.crawler.crawl_characters()
            logger.info(f"Found {len(characters)} characters")

            # 爬取每个角色的详情
            updated = 0
            skipped = 0
            errors = 0

            for i, char in enumerate(characters):
                slug = char.get("slug", "")
                if not slug:
                    continue

                logger.info(f"[{i+1}/{len(characters)}] Processing {slug}...")

                try:
                    # 检查是否需要更新
                    if not force:
                        web_file = Path(self.config.output_dir) / "characters" / f"{slug}.json"
                        if web_file.exists():
                            # 检查文件是否在最近 24 小时内更新过
                            mtime = datetime.fromtimestamp(web_file.stat().st_mtime)
                            if (datetime.now() - mtime).total_seconds() < 86400:
                                skipped += 1
                                continue

                    # 爬取详情
                    detail = await self.crawler.crawl_single_character(slug)
                    if detail:
                        updated += 1
                    else:
                        errors += 1

                except Exception as e:
                    logger.error(f"Failed to update {slug}: {e}")
                    errors += 1

                # 限流
                await asyncio.sleep(1)

            result = {
                "total": len(characters),
                "updated": updated,
                "skipped": skipped,
                "errors": errors,
            }

            logger.info(f"Character update complete: {result}")
            return result

        except Exception as e:
            logger.error(f"Failed to update characters: {e}")
            return {"error": str(e)}

    async def update_lightcones(self, force: bool = False) -> dict[str, Any]:
        """更新光锥数据"""
        logger.info("Updating lightcones...")

        try:
            # 爬取光锥列表
            lightcones = await self.crawler.crawl_lightcones()
            logger.info(f"Found {len(lightcones)} lightcones")

            # 光锥详情暂时不需要爬取（列表数据已足够）
            return {
                "total": len(lightcones),
                "updated": len(lightcones),
                "skipped": 0,
                "errors": 0,
            }

        except Exception as e:
            logger.error(f"Failed to update lightcones: {e}")
            return {"error": str(e)}

    def sync_to_web(self) -> dict[str, Any]:
        """同步数据到网站"""
        logger.info("Syncing data to web...")

        try:
            # 同步角色数据
            char_stats = self.sync.sync_characters()

            # 同步光锥数据
            lc_stats = self.sync.sync_lightcones()

            result = {
                "characters": char_stats,
                "lightcones": lc_stats,
            }

            # 保存更新状态
            self._save_status(result)

            logger.info(f"Sync complete: {result}")
            return result

        except Exception as e:
            logger.error(f"Failed to sync data: {e}")
            return {"error": str(e)}

    async def run_update(self, force: bool = False) -> dict[str, Any]:
        """运行完整更新流程"""
        logger.info("Starting full update...")

        try:
            await self.start()

            # 1. 更新角色数据
            char_result = await self.update_characters(force)

            # 2. 更新光锥数据
            lc_result = await self.update_lightcones(force)

            # 3. 同步到网站
            sync_result = self.sync_to_web()

            result = {
                "timestamp": datetime.now().isoformat(),
                "characters": char_result,
                "lightcones": lc_result,
                "sync": sync_result,
            }

            # 保存状态
            self._save_status(result)

            logger.info(f"Full update complete: {result}")
            return result

        except Exception as e:
            logger.error(f"Failed to run update: {e}")
            return {"error": str(e)}

        finally:
            await self.stop()

    def _save_status(self, status: dict[str, Any]):
        """保存更新状态"""
        try:
            self.status_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.status_file, "w", encoding="utf-8") as f:
                json.dump(status, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save status: {e}")

    def get_last_update(self) -> Optional[dict[str, Any]]:
        """获取上次更新状态"""
        if not self.status_file.exists():
            return None

        try:
            with open(self.status_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read status: {e}")
            return None
