from microservices.proxy.clients.service import ServiceClient
from microservices.proxy.config import settings


class MoviesServiceClient(ServiceClient):
    """Клиент для микросервиса фильмов"""

    def __init__(self):
        super().__init__(settings.movies_service_url, "movies-service")


movies_client = MoviesServiceClient()
