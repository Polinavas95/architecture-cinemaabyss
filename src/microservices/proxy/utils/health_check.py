from typing import Any
import httpx
import asyncio
import logging

from config import settings

logger = logging.getLogger(__name__)


async def check_service_health(url: str, service_name: str) -> dict[str, Any]:
    """
    Проверяет здоровье конкретного сервиса
    """
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{url}/health")

            if response.status_code == 200:
                return {
                    "name": service_name,
                    "status": "healthy",
                    "url": url,
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                return {
                    "name": service_name,
                    "status": "unhealthy",
                    "url": url,
                    "error": f"HTTP {response.status_code}"
                }
    except httpx.TimeoutException:
        logger.warning(f"Health check timeout for {service_name}")
        return {
            "name": service_name,
            "status": "unhealthy",
            "url": url,
            "error": "timeout"
        }
    except Exception as e:
        logger.warning(f"Health check error for {service_name}: {str(e)}")
        return {
            "name": service_name,
            "status": "unhealthy",
            "url": url,
            "error": str(e)
        }


async def check_all_services() -> dict[str, Any]:
    """
    Проверяет здоровье всех сервисов
    """
    services = [
        (settings.monolith_url, "monolith"),
        (settings.movies_service_url, "movies-service"),
        (settings.events_service_url, "events-service"),
    ]

    tasks = [check_service_health(url, name) for url, name in services]
    results = await asyncio.gather(*tasks)

    all_healthy = all(r["status"] == "healthy" for r in results)

    return {
        "status": "healthy" if all_healthy else "degraded",
        "proxy_version": "1.0",
        "services": results
    }
