from kafka.producer import kafka_producer
from kafka.consumer import kafka_consumer


async def get_kafka_producer():
    """Dependency для получения продюсера"""
    return kafka_producer


async def get_kafka_consumer():
    """Dependency для получения консюмера"""
    return kafka_consumer
