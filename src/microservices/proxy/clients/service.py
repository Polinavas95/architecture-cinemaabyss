from json import JSONDecodeError

import httpx
from typing import Any
import logging

from config import settings

logger = logging.getLogger(__name__)


class ServiceClient:
    """Базовый клиент для взаимодействия с сервисами"""

    def __init__(self, base_url: str, service_name: str):
        self.base_url = base_url.rstrip("/")
        self.service_name = service_name
        self.timeout = settings.request_timeout
        self.client = httpx.AsyncClient(timeout=self.timeout)

    async def request(self, method: str, url: str, **kwargs) -> dict[str, Any]:
        try:
            response = await self.client.request(method, url, **kwargs)
            content_type = response.headers.get("content-type", "")
            if response.status_code == 405 or response.status_code >= 400:
                if response.status_code == 405 and not response.content:
                    return {
                        "status_code": response.status_code,
                        "error": f"Method {method} not allowed",
                        "detail": response.reason_phrase
                    }
            if response.content and 'application/json' in content_type:
                try:
                    return response.json()
                except JSONDecodeError:
                    logger.warning(f"Invalid JSON response from {url}: {response.text[:200]}")
                    return {
                        "status_code": response.status_code,
                        "text": response.text
                    }
            else:
                return {
                    "status_code": response.status_code,
                    "content": response.content.decode("utf-8", errors="ignore") if response.content else None
                }

        except Exception as e:
            logger.error(f"Caught an error: {e}", exc_info=True)
            raise

    async def get(self, path: str, params: dict | None = None, headers: dict | None = None):
        """GET запрос"""
        url = self._build_url(path)
        logger.info(f"GET {url}")
        return await self.request("GET", url, params=params, headers=headers)

    async def post(self, path: str, json_data: dict | None = None, headers: dict | None = None):
        """POST запрос с JSON телом"""
        url = self._build_url(path)
        logger.info(f"POST {url}")
        # ВАЖНО: используем параметр 'json', а не 'json_data'
        return await self.request("POST", url, json=json_data, headers=headers)

    async def put(self, path: str, json_data: dict | None = None, headers: dict | None = None):
        """PUT запрос с JSON телом"""
        url = self._build_url(path)
        logger.info(f"PUT {url}")
        # ВАЖНО: используем параметр 'json', а не 'json_data'
        return await self.request("PUT", url, json=json_data, headers=headers)

    async def delete(self, path: str, params: dict | None, headers: dict | None = None):
        """DELETE запрос"""
        url = self._build_url(path)
        logger.info(f"DELETE {url}")
        return await self.request("DELETE", url, params=params, headers=headers)

    async def patch(self, path: str, json_data: dict | None, headers: dict | None = None):
        """PATCH запрос с JSON телом"""
        url = self._build_url(path)
        logger.info(f"PATCH {url}")
        return await self.request("PATCH", url, json=json_data, headers=headers)
    def _build_url(self, path: str) -> str:
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.base_url}{path}"