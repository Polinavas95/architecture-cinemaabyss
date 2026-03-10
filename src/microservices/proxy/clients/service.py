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

    async def request(
            self,
            method: str,
            path: str,
            params: dict | None = None,
            json_data: dict | None = None,
            headers: dict | None = None
    ) -> dict[str, Any]:
        """
        Выполняет HTTP запрос к сервису
        """
        url = f"{self.base_url}{path}"

        # Подготавливаем заголовки
        request_headers = headers or {}
        request_headers["X-Service-Name"] = self.service_name
        request_headers["X-Proxy-Version"] = "1.0"

        logger.info(f"ServiceClient: {method} {url}")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=request_headers,
                    follow_redirects=True
                )
                try:
                    response_data = response.json()
                except Exception as e:
                    logger.exception(f"Caught an error: '{e}'")
                    response_data = {"content": response.text}

                return {
                    "status_code": response.status_code,
                    "data": response_data,
                    "headers": dict(response.headers),
                    "service": self.service_name
                }

        except httpx.TimeoutException:
            logger.error(f"Timeout error calling {self.service_name} at {url}")
            return {
                "status_code": 504,
                "data": {"error": f"Gateway Timeout: {self.service_name} not responding"},
                "service": self.service_name,
                "error": "timeout"
            }
        except Exception as e:
            logger.error(f"Unexpected error calling {self.service_name}: {str(e)}")
            return {
                "status_code": 500,
                "data": {"error": f"Internal Server Error: {str(e)}"},
                "service": self.service_name,
                "error": "unexpected_error"
            }

    async def get(self, path: str, params: dict | None = None, headers: dict | None = None):
        return await self.request("GET", path, params=params, headers=headers)

    async def post(self, path: str, json_data: dict | None = None, headers: dict | None = None):
        return await self.request("POST", path, json_data=json_data, headers=headers)

    async def put(self, path: str, json_data: dict | None = None, headers: dict | None = None):
        return await self.request("PUT", path, json_data=json_data, headers=headers)

    async def delete(self, path: str, params: dict | None = None, headers: dict | None = None):
        return await self.request("DELETE", path, params=params, headers=headers)