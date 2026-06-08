from flask import Blueprint

predictions_bp = Blueprint(
    "predictions",
    __name__
)

from app.predictions import routes