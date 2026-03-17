from contextlib import asynccontextmanager
from aioprometheus import MetricsMiddleware
from aioprometheus.asgi.starlette import metrics
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

from middlewares import RequestLoggingMiddleware
from routes import router
from config import settings
from kafka.producer import kafka_producer
from kafka.consumer import (
    kafka_consumer, handle_movie_event,
    handle_user_event, handle_payment_event
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Events Service...")
    logger.info(f"Kafka brokers: {settings.kafka_brokers}")

    await kafka_producer.start()

    if settings.enable_consumer:
        kafka_consumer.register_handler(settings.kafka_topic_movies, handle_movie_event)
        kafka_consumer.register_handler(settings.kafka_topic_users, handle_user_event)
        kafka_consumer.register_handler(settings.kafka_topic_payments, handle_payment_event)
        await kafka_consumer.start()
        logger.info("Kafka consumer started with handlers")

    yield
    logger.info("Shutting down Events Service...")
    await kafka_producer.stop()
    await kafka_consumer.stop()


app = FastAPI(
    title="Events Service for CinemaAbyss",
    description="Микросервис для обработки событий через Kafka",
    version="1.0.0",
    docs_url="/",
    lifespan=lifespan
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
app.include_router(router)


@app.get("/health", response_class=PlainTextResponse)
async def health_check():
    return "Events Server is healthy"


@app.get("/health/detailed")
async def detailed_health():
    """Детальная проверка здоровья"""
    kafka_status = "connected" if kafka_producer.producer else "disconnected"
    consumer_status = "running" if kafka_consumer._running else "stopped"

    return {
        "service": "events-service",
        "status": "healthy",
        "kafka": {
            "status": kafka_status,
            "brokers": settings.kafka_brokers_list
        },
        "consumer": {
            "status": consumer_status,
            "topics": [
                settings.kafka_topic_movies,
                settings.kafka_topic_users,
                settings.kafka_topic_payments
            ]
        }
    }