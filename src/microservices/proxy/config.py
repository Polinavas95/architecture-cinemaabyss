from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Annotated


class Settings(BaseSettings):
    port: Annotated[int, Field(alias="PORT")] = 8000
    host: Annotated[str, Field(alias="HOST")] = "0.0.0.0"
    monolith_url: Annotated[str, Field(alias="MONOLITH_URL")] = "http://monolith:8080"
    movies_service_url: Annotated[str, Field(alias="MOVIES_SERVICE_URL")] = "http://movies-service:8081"
    events_service_url: Annotated[str, Field(alias="EVENTS_SERVICE_URL")] = "http://events-service:8082"
    # Feature Flags для постепенной миграции
    gradual_migration: Annotated[bool, Field(alias="GRADUAL_MIGRATION")] = True
    # Процент трафика на микросервис фильмов (0-100)
    movies_migration_percent: Annotated[int, Field(alias="MOVIES_MIGRATION_PERCENT")] = 50
    use_movies_service_for_get: Annotated[bool, Field(alias="USE_MOVIES_SERVICE_FOR_GET")] = True
    use_movies_service_for_post: Annotated[bool, Field(alias="USE_MOVIES_SERVICE_FOR_POST")] = False
    use_movies_service_for_put: Annotated[bool, Field(alias="USE_MOVIES_SERVICE_FOR_PUT")] = False
    use_movies_service_for_delete: Annotated[bool, Field(alias="USE_MOVIES_SERVICE_FOR_DELETE")] = False
    request_timeout: Annotated[int, Field(alias="REQUEST_TIMEOUT")] = 10
    # Настройки кэширования
    enable_caching: Annotated[bool, Field(alias="ENABLE_CACHING")] = True
    cache_ttl: Annotated[int, Field(alias="CACHE_TTL")] = 300  # 5 минут


settings = Settings()
