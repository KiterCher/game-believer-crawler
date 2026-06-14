"""prydwen.gg 爬虫"""

import re
from typing import Any, Optional

from bs4 import BeautifulSoup
from loguru import logger

from .base import BaseCrawler
from ..models.character import Character, Element, Path, Skill, Trace, Eidolon, CharacterStats
from ..utils.http import HttpClient
from ..utils.cache import CacheManager
from ..utils.browser import BrowserManager


class PrydwenCrawler(BaseCrawler):
    """prydwen.gg 数据爬虫"""

    def __init__(self, config, source_config):
        super().__init__(config, source_config)
        self.http = HttpClient(
            base_url=source_config.base_url,
            rate_limit=source_config.rate_limit,
            max_retries=config.max_retries,
        )
        self.cache = CacheManager(config.cache_dir, config.cache_ttl)
        self.browser = BrowserManager(headless=True)

    async def start(self):
        """启动爬虫"""
        logger.info("Starting PrydwenCrawler...")
        await self.browser.start()

    async def stop(self):
        """停止爬虫"""
        await self.browser.stop()
        self.http.close()
        logger.info("PrydwenCrawler stopped")

    async def crawl_characters(self) -> list[dict[str, Any]]:
        """爬取角色列表"""
        logger.info("Crawling character list...")

        # 检查缓存
        cache_key = "prydwen_characters_list"
        cached = self.cache.get(cache_key)
        if cached:
            logger.info("Using cached character list")
            return cached

        # 使用 Playwright 获取页面内容
        try:
            url = f"{self.source_config.base_url}/characters"
            html = await self.browser.get_page_content(url)
            soup = BeautifulSoup(html, "lxml")

            # 解析角色列表
            characters = []

            # 查找所有角色链接
            links = soup.find_all("a", href=re.compile(r"/star-rail/characters/"))
            seen_slugs = set()

            for link in links:
                href = link.get("href", "")
                # 提取 slug
                match = re.search(r"/characters/([^/]+)", href)
                if match:
                    slug = match.group(1)
                    if slug and slug not in seen_slugs and slug != "characters":
                        seen_slugs.add(slug)
                        characters.append({
                            "slug": slug,
                            "name": link.get_text(strip=True) or slug.replace("-", " ").title(),
                            "url": f"/characters/{slug}",
                        })

            logger.info(f"Found {len(characters)} characters")

            # 缓存结果
            self.cache.set(cache_key, characters)

            return characters

        except Exception as e:
            logger.error(f"Failed to crawl character list: {e}")
            return []

    async def crawl_single_character(self, slug: str) -> dict[str, Any]:
        """爬取单个角色详情"""
        logger.info(f"Crawling character: {slug}")

        # 检查缓存
        cache_key = f"prydwen_character_{slug}"
        cached = self.cache.get(cache_key)
        if cached:
            logger.info(f"Using cached data for {slug}")
            return cached

        try:
            # 使用 Playwright 获取页面内容
            url = f"{self.source_config.base_url}/characters/{slug}"
            html = await self.browser.get_page_content(url)
            soup = BeautifulSoup(html, "lxml")

            # 解析角色数据
            character_data = self._parse_character_page(soup, slug)

            # 缓存结果
            self.cache.set(cache_key, character_data)

            return character_data

        except Exception as e:
            logger.error(f"Failed to crawl character {slug}: {e}")
            return {}

    def _parse_character_page(self, soup: BeautifulSoup, slug: str) -> dict[str, Any]:
        """解析角色页面"""
        page_text = soup.get_text()

        data = {
            "id": slug,
            "name": "",
            "nameEn": slug.replace("-", " ").title(),
            "rarity": 5,
            "element": "Physical",
            "path": "Destruction",
            "faction": "",
            "releaseVersion": "",
            "description": "",
            "role": "",
            "tags": [],
            "skills": [],
            "traces": [],
            "eidolons": [],
            "stats": {},
        }

        # 提取角色名称（从标题）
        title = soup.find("title")
        if title:
            title_text = title.get_text()
            # 从标题中提取名称
            name_match = re.match(r"^([^-|]+)", title_text)
            if name_match:
                name = name_match.group(1).strip()
                # 移除 "Best Build Guide" 等后缀
                name = re.sub(r'\s*(Best Build Guide|Character Guide|Build Guide).*$', '', name, flags=re.I)
                data["name"] = name.strip()

        # 提取稀有度（从星级符号）
        rarity_match = re.search(r'(\d)★', page_text)
        if rarity_match:
            data["rarity"] = int(rarity_match.group(1))

        # 提取属性
        element_map = {
            "Physical": ["Physical"],
            "Fire": ["Fire"],
            "Ice": ["Ice"],
            "Lightning": ["Lightning"],
            "Wind": ["Wind"],
            "Quantum": ["Quantum"],
            "Imaginary": ["Imaginary"],
        }

        # 优先从角色简介中查找属性
        intro_elem = soup.find("div", class_="character-intro")
        intro_text = intro_elem.get_text() if intro_elem else ""

        for element, keywords in element_map.items():
            for keyword in keywords:
                if keyword in intro_text:
                    data["element"] = element
                    break

        # 提取命途
        path_map = {
            "Destruction": ["Destruction"],
            "Hunt": ["The Hunt", "Hunt"],
            "Erudition": ["Erudition"],
            "Harmony": ["Harmony"],
            "Nihility": ["Nihility"],
            "Preservation": ["Preservation"],
            "Abundance": ["Abundance"],
        }

        for path, keywords in path_map.items():
            for keyword in keywords:
                if keyword in page_text:
                    data["path"] = path
                    break

        # 提取描述
        intro_elem = soup.find("div", class_="character-intro")
        if intro_elem:
            data["description"] = intro_elem.get_text(strip=True)[:500]

        # 提取技能
        skill_elems = soup.find_all("p", class_="skill-name")
        skill_types = ["Basic", "Skill", "Ultimate", "Talent", "Technique"]

        for i, skill_elem in enumerate(skill_elems[:5]):
            skill_name = skill_elem.get_text(strip=True)
            skill_type = skill_types[i] if i < len(skill_types) else f"Skill {i+1}"

            # 查找技能描述
            desc_elem = skill_elem.find_next_sibling("p")
            description = desc_elem.get_text(strip=True) if desc_elem else ""

            data["skills"].append({
                "name": skill_name,
                "type": skill_type,
                "description": description,
            })

        # 提取行迹（Traces）
        trace_names = ["Plunder", "Thorns", "Da Capo"]
        trace_descriptions = {
            "Plunder": "Unlock at A2",
            "Thorns": "Unlock at A4",
            "Da Capo": "Unlock at A6",
        }

        for trace_name in trace_names:
            trace_elem = soup.find(string=re.compile(re.escape(trace_name), re.I))
            if trace_elem:
                parent = trace_elem.parent
                desc_elem = parent.find_next("p") if parent else None
                data["traces"].append({
                    "id": f"trace_{len(data['traces'])}",
                    "name": trace_name,
                    "description": desc_elem.get_text(strip=True) if desc_elem else "",
                    "unlock_level": trace_descriptions.get(trace_name, f"A{2 + len(data['traces']) * 2}"),
                })

        # 提取星魂（Eidolons）
        eidolon_names = ["Fortississimo", "Capriccio", "Recitativo", "Doloroso", "Leggiero"]
        for i, eidolon_name in enumerate(eidolon_names[:6]):
            eidolon_elem = soup.find(string=re.compile(re.escape(eidolon_name), re.I))
            if eidolon_elem:
                parent = eidolon_elem.parent
                desc_elem = parent.find_next("p") if parent else None
                data["eidolons"].append({
                    "level": i + 1,
                    "name": eidolon_name,
                    "description": desc_elem.get_text(strip=True) if desc_elem else "",
                })

        # 提取属性数据
        hp_match = re.search(r'HP[:\s]*(\d+[\d,]*)', page_text)
        atk_match = re.search(r'ATK[:\s]*(\d+[\d,]*)', page_text)
        def_match = re.search(r'DEF[:\s]*(\d+[\d,]*)', page_text)
        spd_match = re.search(r'SPD[:\s]*(\d+)', page_text)

        if hp_match or atk_match:
            data["stats"] = {
                "hp": [int(hp_match.group(1).replace(",", ""))] if hp_match else [1000],
                "atk": [int(atk_match.group(1).replace(",", ""))] if atk_match else [500],
                "def": [int(def_match.group(1).replace(",", ""))] if def_match else [300],
                "spd": int(spd_match.group(1)) if spd_match else 100,
            }

        logger.info(f"Parsed character: {data['name']}")
        return data

    async def crawl_lightcones(self) -> list[dict[str, Any]]:
        """爬取光锥列表"""
        logger.info("Crawling lightcone list...")

        # 检查缓存
        cache_key = "prydwen_lightcones_list"
        cached = self.cache.get(cache_key)
        if cached:
            logger.info("Using cached lightcone list")
            return cached

        try:
            url = f"{self.source_config.base_url}/light-cones"
            html = await self.browser.get_page_content(url)
            soup = BeautifulSoup(html, "lxml")

            # 解析光锥列表
            lightcones = []
            seen_names = set()

            # 从文本中提取光锥数据
            page_text = soup.get_text()

            # 匹配格式: "Name Rarity: X★"（名称后面有 Rarity:）
            pattern = r'([A-Z][a-zA-Z\s\'-]{2,50}?)\s*Rarity:\s*(\d)★'
            matches = re.findall(pattern, page_text)

            for name, rarity in matches:
                name = name.strip()
                # 清理名称
                name = re.sub(r'HP\+\d+ATK\+\d+DEF\+\d+', '', name).strip()
                name = re.sub(r'\s+', ' ', name)

                # 跳过无效名称
                if not name or len(name) < 3 or name in seen_names:
                    continue
                if 'Source' in name or 'Reset' in name or 'Cone' in name:
                    continue

                seen_names.add(name)
                slug = name.lower().replace("'", "").replace("'", "").replace(" ", "-")
                slug = re.sub(r'[^a-z0-9-]', '', slug)
                slug = re.sub(r'-+', '-', slug).strip('-')

                lightcones.append({
                    "slug": slug,
                    "name": name,
                    "rarity": int(rarity),
                    "url": f"/light-cones/{slug}",
                })

            logger.info(f"Found {len(lightcones)} lightcones")

            # 缓存结果
            self.cache.set(cache_key, lightcones)

            return lightcones

        except Exception as e:
            logger.error(f"Failed to crawl lightcone list: {e}")
            return []

    async def crawl_relics(self) -> list[dict[str, Any]]:
        """爬取遗器列表"""
        logger.info("Crawling relic list...")

        # 检查缓存
        cache_key = "prydwen_relics_list"
        cached = self.cache.get(cache_key)
        if cached:
            logger.info("Using cached relic list")
            return cached

        try:
            # 遗器数据在 /guides/relic-sets 页面
            url = f"{self.source_config.base_url}/guides/relic-sets"
            html = await self.browser.get_page_content(url)
            soup = BeautifulSoup(html, "lxml")

            # 解析遗器列表
            relics = []
            seen_names = set()

            # 从文本中提取遗器数据
            page_text = soup.get_text()

            # 匹配遗器套装名称（格式：名称后跟 Type:）
            pattern = r'([A-Z][a-zA-Z\s\'-,]{3,50}?)\s*Type:'
            matches = re.findall(pattern, page_text)

            for name in matches:
                name = name.strip()
                # 清理名称
                name = re.sub(r'\s+', ' ', name)
                name = re.sub(r'[^a-zA-Z\s\'-]', '', name).strip()

                # 跳过无效名称
                if not name or len(name) < 3 or name in seen_names:
                    continue
                if any(skip in name.lower() for skip in ['source', 'reset', 'relic', 'cavern', 'showing']):
                    continue

                seen_names.add(name)
                slug = name.lower().replace("'", "").replace("'", "").replace(" ", "-")
                slug = re.sub(r'[^a-z0-9-]', '', slug)
                slug = re.sub(r'-+', '-', slug).strip('-')

                relics.append({
                    "slug": slug,
                    "name": name,
                    "url": f"/relics/{slug}",
                })

            logger.info(f"Found {len(relics)} relics")

            # 缓存结果
            self.cache.set(cache_key, relics)

            return relics

        except Exception as e:
            logger.error(f"Failed to crawl relic list: {e}")
            return []

    def download_character_images(self, slug: str, images_dir: str) -> dict[str, str]:
        """下载角色图片"""
        from pathlib import Path

        logger.info(f"Downloading images for {slug}")

        # 创建目录
        char_dir = Path(images_dir) / "characters" / slug
        char_dir.mkdir(parents=True, exist_ok=True)

        # prydwen.gg 图片 URL 格式
        image_urls = {
            "card": f"https://cdn.prydwen.gg/images/honkai-star-rail/characters/{slug}_card.webp",
            "full": f"https://cdn.prydwen.gg/images/honkai-star-rail/characters/{slug}_full.webp",
        }

        image_paths = {}
        for img_type, url in image_urls.items():
            save_path = char_dir / f"{img_type}.webp"
            if self.http.download_image(url, str(save_path)):
                image_paths[img_type] = f"/images/characters/{slug}/{img_type}.webp"

        return image_paths
