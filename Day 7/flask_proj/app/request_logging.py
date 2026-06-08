import time
import uuid

from flask import g, request
import structlog

logger = structlog.get_logger()


def register_request_logging(app):

    @app.before_request
    def before_request():
        g.start_time = time.time()

        g.correlation_id = str(uuid.uuid4())

    @app.after_request
    def after_request(response):

        duration_ms = round(
            (time.time() - g.start_time) * 1000,
            2
        )

        logger.info(
            "request_completed",
            correlation_id=g.correlation_id,
            method=request.method,
            path=request.path,
            status=response.status_code,
            duration_ms=duration_ms
        )

        return response