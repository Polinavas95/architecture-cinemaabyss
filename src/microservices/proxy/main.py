from contextlib import asynccontextmanager

from aioprometheus import MetricsMiddleware
from aioprometheus.asgi.starlette import metrics
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

from microservices.proxy.config import settings
from microservices.proxy.feature_flag import feature_flags
from microservices.proxy.handlers import handle_request
from microservices.proxy.middlewares import RequestLoggingMiddleware
from microservices.proxy.utils.health_check import check_all_services

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Strangler Fig Proxy...")
    logger.info(f"Monolith URL: {settings.monolith_url}")
    logger.info(f"Movies Service URL: {settings.movies_service_url}")
    logger.info(f"Events Service URL: {settings.events_service_url}")
    logger.info(f"Gradual Migration: {settings.gradual_migration}")
    logger.info(f"Movies Migration Percent: {settings.movies_migration_percent}%")

    yield
    logger.info("Shutting down Strangler Fig Proxy...")


app = FastAPI(
    title="Strangler Fig Proxy for CinemaAbyss",
    description="API Gateway с паттерном Strangler Fig для постепенной миграции с монолита на микросервисы",
    version="1.0.0",
    docs_url="/",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(MetricsMiddleware)
app.add_route("/metrics", metrics)


@app.get("/health", response_class=PlainTextResponse)
async def health_check():
    return "Strangler Fig Proxy is healthy"


@app.get("/health/detailed")
async def detailed_health_check():
    """
    Детальная проверка здоровья всех сервисов
    """
    health_status = await check_all_services()
    return JSONResponse(content=health_status)


@app.get("/config/feature-flags")
async def get_feature_flags():
    """
    Возвращает текущие значения feature flags
    """
    return JSONResponse(content=feature_flags.flags)


@app.post("/config/feature-flags/{flag_name}")
async def update_feature_flag(flag_name: str, request: Request):
    """
    Обновляет значение feature flag (для администрирования)
    """
    try:
        data = await request.json()
        value = data.get("value")

        if value is not None:
            feature_flags.update_flag(flag_name, value)
            return JSONResponse(content={
                "status": "success",
                "flag": flag_name,
                "value": value
            })
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Missing 'value' field"}
            )
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error": str(e)}
        )


@app.get("/config/migration-status")
async def get_migration_status():
    """
    Возвращает статус миграции
    """
    return JSONResponse(content={
        "gradual_migration_enabled": settings.gradual_migration,
        "movies_migration_percent": settings.movies_migration_percent,
        "movies_get_enabled": settings.use_movies_service_for_get,
        "movies_post_enabled": settings.use_movies_service_for_post,
        "monolith_url": settings.monolith_url,
        "movies_service_url": settings.movies_service_url,
        "events_service_url": settings.events_service_url
    })


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def proxy(request: Request, path: str):
    """
    Прокси для всех запросов - маршрутизирует их в соответствующие сервисы
    """
    if path.startswith("health") or path.startswith("config"):
        pass
    return await handle_request(request)
