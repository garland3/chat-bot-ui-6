import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, AsyncMock
from app.config import settings

@pytest.fixture(scope="function", autouse=True)
def setup_test_mode():
    """Enable test mode for all tests"""
    original_test_mode = settings.test_mode
    settings.test_mode = True
    yield
    settings.test_mode = original_test_mode

@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client
