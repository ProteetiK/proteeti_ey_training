import uuid

predictions = {}


def create_prediction(data):
    prediction_id = str(uuid.uuid4())

    prediction = {
        "id": prediction_id,
        "input": data,
        "result": "sample_prediction"
    }

    predictions[prediction_id] = prediction

    return prediction


def get_prediction(prediction_id):
    return predictions.get(prediction_id)