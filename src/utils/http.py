"""HTTP 工具模块"""

import time
from typing import Any, Optional

import requests
from loguru import logger
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class HttpClient:
    """HTTP 客户端，支持限流、重试、缓存"""

    def __init__(
        self,
        base_url: str,
        user_agent: str = "GameBeliever Crawler/0.1.0",
        timeout: int = 30,
        max_retries: int = 3,
        rate_limit: float = 1.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.rate_limit = rate_limit
        self.last_request_time = 0

        # 创建会话
        self.session = requests.Session()

        # 设置重试策略
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # 设置请求头
        self.session.headers.update(
            {
                "User-Agent": user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }
        )

        logger.info(f"HttpClient initialized: base_url={base_url}")

    def _wait_for_rate_limit(self):
        """等待限流"""
        if self.rate_limit > 0:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.rate_limit:
                wait_time = self.rate_limit - elapsed
                logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
                time.sleep(wait_time)

    def get(
        self,
        url: str,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> requests.Response:
        """发送 GET 请求"""
        self._wait_for_rate_limit()

        full_url = f"{self.base_url}{url}" if not url.startswith("http") else url
        logger.debug(f"GET {full_url}")

        try:
            response = self.session.get(
                full_url,
                params=params,
                headers=headers,
                timeout=self.timeout,
            )
            self.last_request_time = time.time()

            logger.debug(f"Response: {response.status_code}")
            return response

        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

    def post(
        self,
        url: str,
        data: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> requests.Response:
        """发送 POST 请求"""
        self._wait_for_rate_limit()

        full_url = f"{self.base_url}{url}" if not url.startswith("http") else url
        logger.debug(f"POST {full_url}")

        try:
            response = self.session.post(
                full_url,
                data=data,
                json=json,
                headers=headers,
                timeout=self.timeout,
            )
            self.last_request_time = time.time()

            logger.debug(f"Response: {response.status_code}")
            return response

        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

    def get_html(self, url: str) -> str:
        """获取 HTML 内容"""
        response = self.get(url)
        response.raise_for_status()
        return response.text

    def get_json(self, url: str) -> Any:
        """获取 JSON 内容"""
        response = self.get(url)
        response.raise_for_status()
        return response.json()

    def download_image(self, url: str, save_path: str) -> bool:
        """下载图片"""
        try:
            # 直接使用 requests 下载图片（支持流式下载）
            full_url = url if url.startswith("http") else f"{self.base_url}{url}"
            response = requests.get(
                full_url,
                stream=True,
                timeout=self.timeout,
                headers=self.session.headers,
            )
            response.raise_for_status()

            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.debug(f"Image downloaded: {save_path}")
            return True

        except Exception as e:
            logger.error(f"Image download failed: {e}")
            return False

    def close(self):
        """关闭会话"""
        self.session.close()
        logger.debug("HttpClient closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
