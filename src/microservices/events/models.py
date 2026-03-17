from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid


class Event(BaseModel):
    """Базовая модель события"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict


class MovieEvent(BaseModel):
    """Событие фильма"""
    movie_id: int
    title: str
    action: str
    user_id: int | None = None
    rating: float | None = None
    genres: list[str] | None = None
    description: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserEvent(BaseModel):
    """Событие пользователя"""
    user_id: int
    action: str
    username: str | None = None
    email: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaymentEvent(BaseModel):
    """Событие платежа"""
    payment_id: int
    user_id: int
    amount: float
    status: str
    timestamp: datetime
    method_type: str | None = None


class EventResponse(BaseModel):
    """Ответ на создание события"""
    status: str
    partition: int
    offset: int
    event: Event


class EventMovieResponse(EventResponse):
    timestamp: datetime


class Error(BaseModel):
    """Модель ошибки"""
    error: str