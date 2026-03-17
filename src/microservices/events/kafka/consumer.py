import asyncio
import json
import logging
from typing import Callable, Any
from aiokafka import AIOKafkaConsumer

from config import settings

logger = logging.getLogger(__name__)


class KafkaConsumer:

    def __init__(self):
        self.consumer: AIOKafkaConsumer | None = None
        self._task: asyncio.Task | None = None
        self._running = False
        self._handlers: dict[str, Callable] = {}

    def register_handler(self, topic: str, handler: Callable):
        self._handlers[topic] = handler
        logger.info(f"Registered handler for topic: {topic}")

    async def start(self):
        if self.consumer is None:
            # Подписываемся на все топики событий
            topics = [
                settings.kafka_topic_movies,
                settings.kafka_topic_users,
                settings.kafka_topic_payments
            ]

            self.consumer = AIOKafkaConsumer(
                *topics,
                bootstrap_servers=settings.kafka_brokers_list,
                group_id=settings.kafka_consumer_group,
                auto_offset_reset=settings.auto_offset_reset,
                enable_auto_commit=settings.enable_auto_commit,
                value_deserializer=lambda m: json.loads(m.decode("utf-8"))
            )

            await self.consumer.start()
            logger.info(f"Kafka consumer started. Subscribed to: {topics}")

            self._running = True
            self._task = asyncio.create_task(self._consume_loop())

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        if self.consumer:
            await self.consumer.stop()
            logger.info("Kafka consumer stopped")

    async def _consume_loop(self):
        try:
            async for msg in self.consumer:
                if not self._running:
                    break

                await self._process_message(msg)
        except asyncio.CancelledError:
            logger.info("Consumer loop cancelled")
        except Exception as e:
            logger.error(f"Error in consumer loop: {str(e)}")

    async def _process_message(self, msg):
        try:
            topic = msg.topic
            value = msg.value

            logger.info(f"Received message from {topic}: partition={msg.partition}, offset={msg.offset}")
            logger.debug(f"Message value: {value}")
            if topic in self._handlers:
                await self._handlers[topic](value)
            else:
                logger.info(f"No handler for topic {topic}. Event: {value.get('type')}")

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")


kafka_consumer = KafkaConsumer()


async def handle_movie_event(event_data: dict[str, Any]):
    """Обработчик событий фильмов"""
    payload = event_data.get("payload", {})

    logger.info(f"MOVIE EVENT: {payload.get('action', 'unknown')} - {payload.get('title', 'Unknown')}")
    if payload.get("rating"):
        logger.info(f"   Rating: {payload.get('rating')}")
    if payload.get("user_id"):
        logger.info(f"   User ID: {payload.get('user_id')}")
    if payload.get("genres"):
        logger.info(f"   Genres: {', '.join(payload.get('genres', []))}")


async def handle_user_event(event_data: dict[str, Any]):
    """Обработчик событий пользователей"""
    payload = event_data.get("payload", {})

    logger.info(f"USER EVENT: {payload.get('action', 'unknown')} - User ID: {payload.get('user_id')}")
    if payload.get("username"):
        logger.info(f"   Username: {payload.get('username')}")
    if payload.get("email"):
        logger.info(f"   Email: {payload.get('email')}")


async def handle_payment_event(event_data: dict[str, Any]):
    """Обработчик событий платежей"""
    payload = event_data.get("payload", {})

    logger.info(f"PAYMENT EVENT: {payload.get('status', 'unknown')} - Amount: ${payload.get('amount', 0)}")
    logger.info(f"   Payment ID: {payload.get('payment_id')}, User ID: {payload.get('user_id')}")
    if payload.get("method_type"):
        logger.info(f"   Method: {payload.get('method_type')}")
