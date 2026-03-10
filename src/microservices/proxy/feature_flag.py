import random
from typing import Any

from microservices.proxy.config import settings
from microservices.proxy.enums import Flags


class FeatureFlagManager:
    """Менеджер Feature Flags для управления миграцией"""

    def __init__(self):
        self.flags: dict[str, Any] = {
            Flags.movies_service_enabled.value: settings.gradual_migration,
            Flags.movies_get_enabled.value: settings.use_movies_service_for_get,
            Flags.movies_post_enabled.value: settings.use_movies_service_for_post,
            Flags.movies_put_enabled.value: settings.use_movies_service_for_put,
            Flags.movies_delete_enabled.value: settings.use_movies_service_for_delete,

            # Процентные флаги (для постепенного переключения)
            Flags.movies_migration_percent.value: settings.movies_migration_percent,

            # Флаги для других сервисов (можно добавить позже)
            Flags.events_service_enabled.value: True,
            Flags.users_service_enabled.value: False,  # Пока нет микросервиса пользователей
            Flags.payments_service_enabled.value: False,  # Пока нет микросервиса платежей
            Flags.subscriptions_service_enabled.value: False,  # Пока нет микросервиса подписок
        }

    def is_enabled(self, flag_name: str) -> bool:
        """Проверяет, включен ли конкретный флаг"""
        return self.flags.get(flag_name, False)

    def should_route_to_movies_service(self, request_data: dict = None) -> bool:
        """
        Определяет, должен ли запрос идти в микросервис фильмов
        на основе feature flags и данных запроса
        """
        if not self.flags[Flags.movies_service_enabled.value]:
            return False

        # Проверяем по методу HTTP
        method = request_data.get("method", "").upper() if request_data else ""

        if method == "GET":
            if not self.flags[Flags.movies_get_enabled.value]:
                return False
            # Постепенное переключение трафика на основе процента
            migration_percent = self.flags[Flags.movies_migration_percent.value]
            user_id = request_data.get("user_id") if request_data else None
            if user_id:
                return (hash(f"user:{user_id}") % 100) < migration_percent
            return random.randint(1, 100) <= migration_percent
        elif method == "POST" and not self.flags[Flags.movies_post_enabled.value]:
            return False
        elif method in ("PUT", "PATCH") and not self.flags[Flags.movies_put_enabled.value]:
            return False
        elif method == "DELETE" and not self.flags[Flags.movies_delete_enabled.value]:
            return False

        return True

    def update_flag(self, flag_name: str, value: Any):
        """Обновляет значение флага (можно вызвать через API админа)"""
        self.flags[flag_name] = value


feature_flags = FeatureFlagManager()
