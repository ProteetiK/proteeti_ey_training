from flask import jsonify, request, g
from pydantic import ValidationError
import structlog

from app.predictions import predictions_bp
from app.models.prediction import (
    PredictionRequest,
    PredictionResponse
)

logger = structlog.get_logger()

# In-memory storage
predictions = {}


@predictions_bp.route("/predictions", methods=["POST"])
def create_prediction():

    if not request.is_json:
        logger.warning(
            "invalid_content_type",
            correlation_id=g.correlation_id
        )

        return jsonify({
            "error": "Request must be JSON"
        }), 422

    try:
        payload = PredictionRequest.parse_obj(
            request.get_json()
        )

    except ValidationError as e:

        logger.warning(
            "validation_failed",
            correlation_id=g.correlation_id,
            errors=e.errors()
        )

        return jsonify({
            "error": "Validation failed",
            "details": e.errors()
        }), 422

    prediction_id = str(len(predictions) + 1)

    response = PredictionResponse(
        id=prediction_id,
        result="sample_prediction",
        feature1=payload.feature1,
        feature2=payload.feature2
    )

    predictions[prediction_id] = response.dict()

    logger.info(
        "prediction_created",
        correlation_id=g.correlation_id,
        prediction_id=prediction_id
    )

    return jsonify(response.dict()), 201


@predictions_bp.route("/predictions/<prediction_id>", methods=["GET"])
def get_prediction(prediction_id):

    prediction = predictions.get(prediction_id)

    if prediction is None:

        logger.warning(
            "prediction_not_found",
            correlation_id=g.correlation_id,
            prediction_id=prediction_id
        )

        return jsonify({
            "error": "Prediction not found"
        }), 404

    logger.info(
        "prediction_retrieved",
        correlation_id=g.correlation_id,
        prediction_id=prediction_id
    )

    return jsonify(prediction), 200


@predictions_bp.route("/health", methods=["GET"])
def health():

    logger.info(
        "health_check",
        correlation_id=g.correlation_id
    )

    return jsonify({
        "status": "healthy"
    }), 200