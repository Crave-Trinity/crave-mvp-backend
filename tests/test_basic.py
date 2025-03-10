# File: tests/test_basic.py

from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)

def test_health_check():
    """
    Basic test to confirm /health is up.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"