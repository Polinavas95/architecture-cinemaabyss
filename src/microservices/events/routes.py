from fastapi import APIRouter, HTTPException, status
import logging

from models import (
    MovieEvent, UserEvent, PaymentEvent,
    EventResponse, Error
)
from kafka.producer import kafka_producer
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/events", tags=["events"])


@router.post(
    "/movie",
    response_model=EventResponse,
    responses={
        400: {"model": Error},
        500: {"model": Error}
    },
    status_code=status.HTTP_201_CREATED
)
async def create_movie_event(event: MovieEvent):
    try:
        partition, offset = await kafka_producer.create_movie_event(event)

        return EventResponse(
            status="success",
            partition=partition,
            offset=offset,
            event={
                "id": f"movie-{event.movie_id}-{event.action}",
                "type": "movie",
                "timestamp": event.timestamp if hasattr(event, 'timestamp') else None,
                "payload": event.dict(exclude_none=True)
            }
        )
    except Exception as e:
        logger.error(f"Failed to create movie event: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": f"Failed to create event: {str(e)}"}
        )


@router.post(
    "/user",
    response_model=EventResponse,
    responses={
        400: {"model": Error},
        500: {"model": Error}
    },
    status_code=status.HTTP_201_CREATED
)
async def create_user_event(event: UserEvent):
    try:
        partition, offset = await kafka_producer.create_user_event(event)

        return EventResponse(
            status="success",
            partition=partition,
            offset=offset,
            event={
                "id": f"user-{event.user_id}-{event.action}",
                "type": "user",
                "timestamp": event.timestamp,
                "payload": event.dict(exclude_none=True)
            }
        )
    except Exception as e:
        logger.error(f"Failed to create user event: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": f"Failed to create event: {str(e)}"}
        )


@router.post(
    "/payment",
    response_model=EventResponse,
    responses={
        400: {"model": Error},
        500: {"model": Error}
    },
    status_code=status.HTTP_201_CREATED
)
async def create_payment_event(event: PaymentEvent):
    try:
        partition, offset = await kafka_producer.create_payment_event(event)

        return EventResponse(
            status="success",
            partition=partition,
            offset=offset,
            event={
                "id": f"payment-{event.payment_id}-{event.status}",
                "type": "payment",
                "timestamp": event.timestamp,
                "payload": event.dict(exclude_none=True)
            }
        )
    except Exception as e:
        logger.error(f"Failed to create payment event: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": f"Failed to create event: {str(e)}"}
        )


@router.get("/health", response_model=dict)
async def health_check():
    kafka_status = "connected" if kafka_producer.producer else "disconnected"

    return {
        "status": True,
        "service": "events-service",
        "kafka": kafka_status,
        "topics": {
            "movies": settings.kafka_topic_movies,
            "users": settings.kafka_topic_users,
            "payments": settings.kafka_topic_payments
        }
    }
