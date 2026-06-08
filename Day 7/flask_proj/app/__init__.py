from flask import Flask

from app.predictions import predictions_bp
from app.logging_config import configure_logging
from app.request_logging import register_request_logging
from app.error_handlers import register_error_handlers


def create_app():
    app = Flask(__name__)

    configure_logging()

    register_request_logging(app)

    register_error_handlers(app)

    app.register_blueprint(predictions_bp)

    return app