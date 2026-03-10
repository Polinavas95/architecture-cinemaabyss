from fastapi import Request, Response
import logging

from router import proxy_router

logger = logging.getLogger(__name__)


async def handle_request(request: Request) -> Response:
    """
    Обрабатывает входящий запрос и направляет его через прокси-роутер
    """
    path = request.url.path
    method = request.method

    logger.info(f"Handling {method} request to {path}")

    result = await proxy_router.route_request(request, path, method)

    response = Response(
        content=result.get("content"),
        status_code=result.get("status_code", 200),
        headers=result.get("headers", {})
    )

    # Если есть JSON данные, устанавливаем соответствующий заголовок
    if "data" in result and result["data"]:
        import json
        response = Response(
            content=json.dumps(result["data"]),
            status_code=result.get("status_code", 200),
            headers=result.get("headers", {}),
            media_type="application/json"
        )

    response.headers["X-Proxy-Version"] = "1.0"
    response.headers["X-Target-Service"] = result.get("service", "unknown")

    return response
