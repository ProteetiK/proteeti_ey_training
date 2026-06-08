def test_health_endpoint(client):

    response = client.get("/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "healthy"


def test_invalid_prediction_payload(client):

    response = client.post(
        "/predictions",
        json={
            "feature1": "abc"
        }
    )

    assert response.status_code == 422

    data = response.get_json()

    assert data["error"] == "Validation failed"

def test_prediction_not_found(client):

    response = client.get("/predictions/999")

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Prediction not found"