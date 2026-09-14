from fastapi.testclient import TestClient
from feedbackos_api.main import app


def test_health_endpoint_reports_api_liveness_without_cors() -> None:
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {"service": "feedbackos-api", "status": "ok"}
    assert response.headers["cache-control"] == "no-store"
    assert "access-control-allow-origin" not in response.headers
