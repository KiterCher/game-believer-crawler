"""浏览器工具模块"""

from typing import Optional
from loguru import logger


class BrowserManager:
    """浏览器管理器，使用 Playwright 渲染 JavaScript"""

    def __init__(self, headless: bool = True):
        """
        初始化浏览器管理器

        Args:
            headless: 是否使用无头模式
        """
        self.headless = headless
        self.browser = None
        self.context = None

    async def start(self):
        """启动浏览器"""
        try:
            from playwright.async_api import async_playwright

            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=self.headless)
            self.context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            logger.info("Browser started")
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            raise

    async def stop(self):
        """停止浏览器"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        logger.info("Browser stopped")

    async def get_page_content(self, url: str, wait_for: str = "domcontentloaded", timeout: int = 30000) -> str:
        """
        获取页面内容（渲染 JavaScript）

        Args:
            url: 页面 URL
            wait_for: 等待条件 ('load', 'domcontentloaded', 'networkidle')
            timeout: 超时时间（毫秒）

        Returns:
            渲染后的 HTML 内容
        """
        page = await self.context.new_page()

        try:
            logger.debug(f"Navigating to {url}")
            await page.goto(url, wait_until=wait_for, timeout=timeout)

            # 等待页面加载完成
            await page.wait_for_load_state(wait_for)

            # 额外等待 JavaScript 渲染
            await page.wait_for_timeout(3000)

            # 获取渲染后的 HTML
            content = await page.content()

            logger.debug(f"Page content loaded: {len(content)} chars")
            return content

        except Exception as e:
            logger.error(f"Failed to get page content: {e}")
            raise
        finally:
            await page.close()

    async def get_element_text(self, url: str, selector: str) -> Optional[str]:
        """获取元素文本"""
        page = await self.context.new_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await page.wait_for_load_state("networkidle")

            element = await page.query_selector(selector)
            if element:
                text = await element.text_content()
                return text.strip() if text else None
            return None

        except Exception as e:
            logger.error(f"Failed to get element text: {e}")
            return None
        finally:
            await page.close()

    async def get_page_data(self, url: str) -> dict:
        """
        获取页面数据（包括 JavaScript 生成的数据）

        Args:
            url: 页面 URL

        Returns:
            页面数据字典
        """
        page = await self.context.new_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await page.wait_for_load_state("networkidle")

            # 尝试获取 __NEXT_DATA__
            next_data = await page.evaluate("() => window.__NEXT_DATA__")
            if next_data:
                return next_data

            # 尝试获取页面内容
            content = await page.content()
            return {"html": content}

        except Exception as e:
            logger.error(f"Failed to get page data: {e}")
            return {}
        finally:
            await page.close()

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
