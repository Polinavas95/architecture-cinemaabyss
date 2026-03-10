from clients.service import ServiceClient
from config import settings


class MonolithClient(ServiceClient):
    """Клиент для монолитного приложения"""

    def __init__(self):
        super().__init__(settings.monolith_url, "monolith")


monolith_client = MonolithClient()
