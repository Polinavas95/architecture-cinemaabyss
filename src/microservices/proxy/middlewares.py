from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
from typing import Callable
import uuid

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware для логирования запросов и ответов
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        logger.info(f"Request [{request_id}]: {request.method} {request.url.path}")
        start_time = time.time()
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)

            logger.info(
                f"Response [{request_id}]: {response.status_code} "
                f"({process_time:.3f}s)"
            )

            return response

        except Exception as e:
            logger.error(f"Error processing request [{request_id}]: {str(e)}")
            raise
