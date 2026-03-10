import logging
from typing import Any

from fastapi import Request

from microservices.proxy.clients.events import events_client
from microservices.proxy.clients.monolith import monolith_client
from microservices.proxy.clients.movies import movies_client
from microservices.proxy.enums import AppClient, Flags
from microservices.proxy.feature_flag import feature_flags

logger = logging.getLogger(__name__)


class ProxyRouter:
    """
    Маршрутизатор запросов между монолитом и микросервисами
    на основе feature flags
    """

    def __init__(self):
        self.services = {
            AppClient.monolith.value: monolith_client,
            AppClient.movies.value: movies_client,
            AppClient.events.value: events_client
        }

    async def route_request(
            self,
            request: Request,
            path: str,
            method: str
    ) -> dict[str, Any]:
        """
        Маршрутизирует запрос к соответствующему сервису
        """
        params = dict(request.query_params)
        body = None
        try:
            if request.method in ["POST", "PUT", "PATCH"]:
                body = await request.json()
        except Exception as e:
            logger.exception(f"Caught an exception: '{e}'")
            body = None

        headers = dict(request.headers)
        headers.pop("host", None)
        headers.pop("content-length", None)

        request_data = {
            "method": method,
            "path": path,
            "params": params,
            "body": body,
            "headers": headers
        }

        service_name = self._determine_target_service(path, request_data)

        logger.info(f"Routing {method} {path} to {service_name}")

        if "headers" not in request_data:
            request_data["headers"] = {}
        request_data["headers"]["X-Routed-By"] = "strangler-fig-proxy"
        request_data["headers"]["X-Target-Service"] = service_name

        result = await self._execute_request(service_name, request_data)
        return result

    def _determine_target_service(self, path: str, request_data: dict) -> str:
        """
        Определяет целевой сервис на основе пути и feature flags
        """
        if path == "/health":
            return AppClient.monolith.value

        if path == "/api/movies/health":
            if feature_flags.is_enabled(Flags.movies_service_enabled.value):
                return AppClient.movies.value
            return AppClient.monolith.value

        if path == "/api/events/health":
            return AppClient.events.value

        # Маршрутизация для /api/movies
        if path.startswith("/api/movies"):
            if feature_flags.should_route_to_movies_service(request_data):
                return AppClient.movies.value
            return AppClient.monolith.value

        # Маршрутизация для /api/events
        if path.startswith("/api/events"):
            return AppClient.events.value

        return AppClient.monolith.value

    async def _execute_request(self, service_name: str, request_data: dict) -> dict[str, Any]:
        """
        Выполняет запрос к указанному сервису
        """
        client = self.services.get(service_name)

        if not client:
            logger.error(f"Unknown service: {service_name}")
            return {
                "status_code": 500,
                "data": {"error": f"Unknown service: {service_name}"},
                "headers": {}
            }

        method = request_data["method"]
        path = request_data["path"]
        params = request_data.get("params", {})
        body = request_data.get("body")
        headers = request_data.get("headers", {})

        try:
            return {
                "GET": await client.get(path, params=params, headers=headers),
                "POST": await client.post(path, json_data=body, headers=headers),
                "PUT": await client.put(path, json_data=body, headers=headers),
                "DELETE": await client.delete(path, params=params, headers=headers),
            }.get(method, await client.request(method, path, params=params, json_data=body, headers=headers))
        except Exception as e:
            logger.error(f"Error executing request to {service_name}: {str(e)}")
            return {
                "status_code": 500,
                "data": {"error": f"Internal Server Error: {str(e)}"},
                "headers": {}
            }


proxy_router = ProxyRouter()
