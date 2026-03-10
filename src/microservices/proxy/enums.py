from enum import Enum


class Flags(Enum):
    movies_service_enabled: str = "movies_service_enabled"
    movies_get_enabled: str = "movies_get_enabled"
    movies_post_enabled: str = "movies_post_enabled"
    movies_put_enabled: str = "movies_put_enabled"
    movies_delete_enabled: str = "movies_delete_enabled"
    movies_migration_percent: str = "movies_migration_percent"
    events_service_enabled: str = "events_service_enabled"
    users_service_enabled: str = "users_service_enabled"
    payments_service_enabled: str = "payments_service_enabled"
    subscriptions_service_enabled: str = "subscriptions_service_enabled"


class AppClient(Enum):
    monolith: str = "monolith"
    movies: str = "movies"
    events: str = "events"

