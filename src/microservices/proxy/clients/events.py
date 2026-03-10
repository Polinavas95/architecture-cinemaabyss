from clients.service import ServiceClient

from config import settings


class EventsServiceClient(ServiceClient):
    """Клиент для микросервиса событий"""

    def __init__(self):
        super().__init__(settings.events_service_url, "events-service")


events_client = EventsServiceClient()
