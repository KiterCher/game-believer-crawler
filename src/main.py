"""CLI 入口模块"""

import click
from loguru import logger

from . import __version__
from .config import load_config, CrawlerConfig
from .utils.logger import setup_logger


@click.group()
@click.version_option(version=__version__)
def cli():
    """GameBeliever Crawler - Honkai Star Rail Data Crawler"""
    pass


@cli.command()
@click.option(
    "--type",
    "data_type",
    required=True,
    type=click.Choice(["characters", "lightcones", "relics", "materials"]),
    help="Data type to crawl",
)
@click.option("--slug", default=None, help="Specific item slug to crawl")
@click.option("--site", default="prydwen", help="Site to crawl from")
@click.option("--output", default=None, help="Output directory")
@click.option("--cache/--no-cache", default=True, help="Enable/disable cache")
def crawl(data_type: str, slug: str, site: str, output: str, cache: bool):
    """爬取数据"""
    import asyncio
    from .crawler.prydwen import PrydwenCrawler

    setup_logger(level="INFO")
    config = load_config()

    logger.info(f"Crawling {data_type} from {site}...")

    async def run_crawl():
        # 获取网站配置
        site_config = config.get_site_config(site)
        if not site_config:
            logger.error(f"Unknown site: {site}")
            click.echo(f"[ERROR] Unknown site: {site}")
            click.echo(f"Available sites: {', '.join(config.sites.keys())}")
            return

        # 检查是否启用
        if not site_config.enabled:
            logger.warning(f"Site {site} is disabled")
            click.echo(f"[WARNING] Site {site} is disabled")
            return

        # 创建爬虫
        crawler = PrydwenCrawler(config, site_config)

        try:
            await crawler.start()

            if data_type == "characters":
                if slug:
                    # 爬取单个角色详情
                    result = await crawler.crawl_single_character(slug)
                    if result:
                        from .pipeline.export import DataExporter
                        exporter = DataExporter(config.processed_dir)
                        exporter.export_json_file(result, f"characters/{slug}.json")
                        click.echo(f"[OK] Crawled {slug}: {result.get('name', 'Unknown')}")
                    else:
                        click.echo(f"[ERROR] Failed to crawl {slug}")
                else:
                    # 爬取角色列表
                    click.echo("[INFO] Crawling character list...")
                    results = await crawler.crawl_characters()
                    click.echo(f"[OK] Found {len(results)} characters")

                    # 保存列表数据
                    if results:
                        from .pipeline.export import DataExporter
                        exporter = DataExporter(config.processed_dir)

                        # 保存列表
                        exporter.export_json_file({"characters": results}, "characters/_list.json")

                        # 爬取每个角色的详情
                        click.echo("[INFO] Crawling character details...")
                        details = []
                        for i, char in enumerate(results):
                            slug_name = char.get("slug", "")
                            if slug_name:
                                click.echo(f"  [{i+1}/{len(results)}] {slug_name}...", nl=False)
                                detail = await crawler.crawl_single_character(slug_name)
                                if detail:
                                    exporter.export_json_file(detail, f"characters/{slug_name}.json")
                                    details.append(detail)
                                    click.echo(f" OK")
                                else:
                                    click.echo(f" FAILED")

                        click.echo(f"[OK] Crawled {len(details)} character details")

            elif data_type == "lightcones":
                results = await crawler.crawl_lightcones()
                click.echo(f"[OK] Crawled {len(results)} lightcones")

            elif data_type == "relics":
                results = await crawler.crawl_relics()
                click.echo(f"[OK] Crawled {len(results)} relics")

        finally:
            await crawler.stop()

    asyncio.run(run_crawl())


@cli.command()
@click.option(
    "--format",
    "output_format",
    default="json",
    type=click.Choice(["json", "csv"]),
    help="Output format",
)
@click.option("--output", default="../GameBeliever-web/src/data", help="Output directory")
@click.option("--type", "data_type", default=None, help="Export specific data type")
def export(output_format: str, output: str, data_type: str):
    """导出数据到 GameBeliever-web"""
    setup_logger(level="INFO")
    config = load_config()

    logger.info(f"Exporting data to {output}...")

    # TODO: 实现导出逻辑
    click.echo(f"[OK] Export command: format={output_format}, output={output}")
    click.echo("[TODO] Not implemented yet")


@cli.command()
@click.option("--type", "data_type", default=None, help="Validate specific data type")
def validate(data_type: str):
    """校验数据完整性"""
    setup_logger(level="INFO")

    logger.info("Validating data...")

    # TODO: 实现校验逻辑
    click.echo(f"[OK] Validate command: type={data_type}")
    click.echo("[TODO] Not implemented yet")


@cli.command()
@click.option("--type", "image_type", required=True, type=click.Choice(["characters", "lightcones", "relics"]), help="Image type to download")
@click.option("--slug", default=None, help="Specific item slug")
@click.option("--all", "download_all", is_flag=True, help="Download all images")
def download(image_type: str, slug: str, download_all: bool):
    """下载图片"""
    import asyncio
    from .crawler.prydwen import PrydwenCrawler
    from .utils.http import HttpClient

    setup_logger(level="INFO")
    config = load_config()

    async def run_download():
        source_config = config.sources.get("prydwen")
        if not source_config:
            logger.error("Prydwen source not configured")
            return

        crawler = PrydwenCrawler(config, source_config)
        await crawler.start()

        try:
            images_dir = config.images_dir

            if image_type == "characters":
                if slug:
                    # 下载单个角色图片
                    click.echo(f"[INFO] Downloading images for {slug}...")
                    result = crawler.download_character_images(slug, images_dir)
                    click.echo(f"[OK] Downloaded {len(result)} images for {slug}")
                elif download_all:
                    # 下载所有角色图片
                    characters = await crawler.crawl_characters()
                    click.echo(f"[INFO] Downloading images for {len(characters)} characters...")

                    success = 0
                    failed = 0
                    for i, char in enumerate(characters):
                        char_slug = char.get("slug", "")
                        if char_slug:
                            click.echo(f"  [{i+1}/{len(characters)}] {char_slug}...", nl=False)
                            try:
                                result = crawler.download_character_images(char_slug, images_dir)
                                if result:
                                    click.echo(f" OK ({len(result)} images)")
                                    success += 1
                                else:
                                    click.echo(f" NO IMAGES")
                                    failed += 1
                            except Exception as e:
                                click.echo(f" FAILED: {e}")
                                failed += 1

                    click.echo(f"[OK] Download complete: {success} success, {failed} failed")
                else:
                    click.echo("[ERROR] Please specify --slug or --all")

            elif image_type == "lightcones":
                click.echo("[TODO] Lightcone image download not implemented yet")

            elif image_type == "relics":
                click.echo("[TODO] Relic image download not implemented yet")

        finally:
            await crawler.stop()

    asyncio.run(run_download())


@cli.command()
@click.option("--clear", is_flag=True, help="Clear cache")
@click.option("--stats", is_flag=True, help="Show cache statistics")
def cache(clear: bool, stats: bool):
    """缓存管理"""
    setup_logger(level="INFO")
    config = load_config()

    if clear:
        from .utils.cache import CacheManager
        cache_manager = CacheManager(config.cache_dir, config.cache_ttl)
        count = cache_manager.clear()
        click.echo(f"[OK] Cache cleared: {count} files deleted")
    elif stats:
        from .utils.cache import CacheManager
        cache_manager = CacheManager(config.cache_dir, config.cache_ttl)
        stats = cache_manager.get_stats()
        click.echo(f"[STATS] Cache Statistics:")
        click.echo(f"   Files: {stats['count']}")
        click.echo(f"   Size: {stats['total_size_mb']} MB")
    else:
        click.echo("Use --clear to clear cache or --stats to show statistics")


@cli.command()
def info():
    """显示配置信息"""
    config = load_config()

    click.echo("[INFO] Configuration Info:")
    click.echo(f"   Output Dir: {config.output_dir}")
    click.echo(f"   Images Dir: {config.images_dir}")
    click.echo(f"   Cache Dir: {config.cache_dir}")
    click.echo(f"   Cache TTL: {config.cache_ttl}s")
    click.echo(f"   Max Retries: {config.max_retries}")
    click.echo(f"   Concurrency: {config.concurrency}")
    click.echo(f"\n[INFO] Schedule:")
    click.echo(f"   Interval: {config.schedule.interval_minutes} minutes")
    click.echo(f"   Enabled: {config.schedule.enabled}")
    click.echo(f"\n[INFO] Sites:")
    for name, site in config.sites.items():
        status = "[OK]" if site.enabled else "[OFF]"
        crawl_types = ", ".join(site.crawl_types)
        click.echo(f"   {status} {name}: {site.base_url}")
        click.echo(f"      Crawl types: {crawl_types}")


@cli.command()
@click.option("--force", is_flag=True, help="Force update all data")
@click.option("--characters-only", is_flag=True, help="Update characters only")
@click.option("--lightcones-only", is_flag=True, help="Update lightcones only")
def update(force: bool, characters_only: bool, lightcones_only: bool):
    """更新数据（爬取 + 同步到网站）"""
    import asyncio
    from .pipeline.updater import AutoUpdater

    setup_logger(level="INFO")
    config = load_config()

    async def run_update():
        updater = AutoUpdater(config)

        if characters_only:
            await updater.start()
            result = await updater.update_characters(force)
            await updater.stop()
        elif lightcones_only:
            await updater.start()
            result = await updater.update_lightcones(force)
            await updater.stop()
        else:
            result = await updater.run_update(force)

        click.echo(f"[OK] Update complete:")
        click.echo(f"   Characters: {result.get('characters', {})}")
        click.echo(f"   Lightcones: {result.get('lightcones', {})}")

    asyncio.run(run_update())


@cli.command()
@click.option("--characters", is_flag=True, help="Sync characters only")
@click.option("--lightcones", is_flag=True, help="Sync lightcones only")
@click.option("--images", is_flag=True, help="Sync images only")
def sync(characters: bool, lightcones: bool, images: bool):
    """同步数据到网站"""
    from .pipeline.sync import DataSync

    setup_logger(level="INFO")
    config = load_config()

    syncer = DataSync(
        crawler_data_dir=config.processed_dir,
        web_data_dir=config.output_dir,
        web_images_dir=config.images_dir,
    )

    if characters:
        result = syncer.sync_characters()
        click.echo(f"[OK] Characters synced: {result}")
    elif lightcones:
        result = syncer.sync_lightcones()
        click.echo(f"[OK] Lightcones synced: {result}")
    elif images:
        for img_type in ["characters", "lightcones", "relics"]:
            result = syncer.sync_images(img_type)
            click.echo(f"[OK] {img_type} images synced: {result}")
    else:
        # 同步所有
        char_result = syncer.sync_characters()
        lc_result = syncer.sync_lightcones()
        click.echo(f"[OK] Sync complete:")
        click.echo(f"   Characters: {char_result}")
        click.echo(f"   Lightcones: {lc_result}")


@cli.command()
def status():
    """显示同步状态"""
    from .pipeline.sync import DataSync

    setup_logger(level="INFO")
    config = load_config()

    syncer = DataSync(
        crawler_data_dir=config.processed_dir,
        web_data_dir=config.output_dir,
        web_images_dir=config.images_dir,
    )

    status = syncer.get_sync_status()

    click.echo("[STATUS] Data Sync Status:")
    click.echo(f"\n   Crawler Data:")
    click.echo(f"      Characters: {status['crawler']['characters']}")
    click.echo(f"      Lightcones: {status['crawler']['lightcones']}")
    click.echo(f"\n   Web Data:")
    click.echo(f"      Characters: {status['web']['characters']}")
    click.echo(f"      Lightcones: {status['web']['lightcones']}")

    # 检查是否需要更新
    if status['crawler']['characters'] > status['web']['characters']:
        click.echo(f"\n   [UPDATE NEEDED] Characters: {status['crawler']['characters'] - status['web']['characters']} new")
    if status['crawler']['lightcones'] > status['web']['lightcones']:
        click.echo(f"\n   [UPDATE NEEDED] Lightcones: {status['crawler']['lightcones'] - status['web']['lightcones']} new")


if __name__ == "__main__":
    cli()
