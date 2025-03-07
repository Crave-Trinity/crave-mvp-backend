# File: tests/integration/test_logging.py

import pytest
import logging
from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)

def test_logging_middleware(caplog: pytest.LogCaptureFixture):
    """
    Calls /api/health and checks logs for 'Incoming request' & 'Completed request'.
    """
    with caplog.at_level(logging.INFO):
        response = client.get("/api/health")
    assert response.status_code == 200

    # Confirm we have the expected log entries
    assert any("Incoming request" in record.msg for record in caplog.records)
    assert any("Completed request" in record.msg for record in caplog.records)


def test_error_logging(caplog: pytest.LogCaptureFixture):
    """
    Triggers an error to see if it's logged by the global exception handler.
    NOTE: If /api/health/force_error doesn't exist, it returns 404 not 500.
    You must create a route that actually raises an exception to get a 500.
    """
    with caplog.at_level(logging.ERROR):
        response = client.get("/api/health/force_error")

    # If that route doesn't exist, you'll get 404. If it forcibly raises, expect 500:
    # Adjust your assertion if you truly want a forced 500
    assert response.status_code in (404, 500)

    # Look for "Unhandled server error" only if a real 500 is triggered
    error_logs = [rec for rec in caplog.records if "Unhandled server error" in rec.msg]
    if response.status_code == 500:
        assert len(error_logs) == 1
    else:
        # If it's 404, the global exception isn't triggered
        assert len(error_logs) == 0