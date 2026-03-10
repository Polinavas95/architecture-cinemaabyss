import json
import logging
from typing import Optional
from aiokafka import AIOKafkaProducer
import asyncio

from config import settings
from models import MovieEvent, UserEvent, PaymentEvent, Event

logger = logging.getLogger(__name__)


class KafkaProducer:
    """Продюсер для отправки событий в Kafka"""

    def __init__(self):
        self.producer: Optional[AIOKafkaProducer] = None
        self._loop = asyncio.get_event_loop()

    async def start(self):
        if self.producer is None:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=settings.kafka_brokers_list,
                loop=self._loop,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
            )
            await self.producer.start()
            logger.info("Kafka producer started")

    async def stop(self):
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka producer stopped")

    async def send_event(self, topic: str, event: Event) -> tuple[int, int]:
        if not self.producer:
            await self.start()

        event_dict = event.model_dump(mode="json")
        future = await self.producer.send(topic, event_dict)
        result = await future

        logger.info(f"Event sent to {topic}: partition={result.partition}, offset={result.offset}")
        logger.debug(f"Event data: {event_dict}")

        return result.partition, result.offset

    async def create_movie_event(self, movie_data: MovieEvent) -> tuple[int, int]:
        """Создание и отправка события фильма"""
        event = Event(
            type="movie",
            payload=movie_data.dict(exclude_none=True)
        )
        return await self.send_event(settings.kafka_topic_movies, event)

    async def create_user_event(self, user_data: UserEvent) -> tuple[int, int]:
        """Создание и отправка события пользователя"""
        event = Event(
            type="user",
            payload=user_data.dict(exclude_none=True)
        )
        return await self.send_event(settings.kafka_topic_users, event)

    async def create_payment_event(self, payment_data: PaymentEvent) -> tuple[int, int]:
        """Создание и отправка события платежа"""
        event = Event(
            type="payment",
            payload=payment_data.dict(exclude_none=True)
        )
        return await self.send_event(settings.kafka_topic_payments, event)


kafka_producer = KafkaProducer()
