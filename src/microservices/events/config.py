from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Annotated


class Settings(BaseSettings):
    port: Annotated[int, Field(alias="PORT")] = 8082
    host: Annotated[str, Field(alias="HOST")] = "0.0.0.0"

    kafka_brokers: Annotated[str, Field(alias="KAFKA_BROKERS")] = "kafka:9092"
    kafka_topic_movies: Annotated[str, Field(alias="KAFKA_TOPIC_MOVIES")] = "movie-events"
    kafka_topic_users: Annotated[str, Field(alias="KAFKA_TOPIC_USERS")] = "user-events"
    kafka_topic_payments: Annotated[str, Field(alias="KAFKA_TOPIC_PAYMENTS")] = "payment-events"
    kafka_consumer_group: Annotated[str, Field(alias="KAFKA_CONSUMER_GROUP")] = "events-service-group"

    auto_offset_reset: Annotated[str, Field(alias="AUTO_OFFSET_RESET")] = "latest"
    enable_auto_commit: Annotated[bool, Field(alias="ENABLE_AUTO_COMMIT")] = True

    enable_consumer: Annotated[bool, Field(alias="ENABLE_CONSUMER")] = True

    @property
    def kafka_brokers_list(self) -> list[str]:
        return self.kafka_brokers.split(",")


settings = Settings()
