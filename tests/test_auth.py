
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

client = TestClient(app)

def test_auth_middleware_with_header():
    response = client.get("/test-auth", headers={"X-EMAIL-USER": "test@example.com"})
    assert response.status_code == 200
    assert response.json() == {"user_email": "test@example.com"}

def test_auth_middleware_test_mode():
    settings.test_mode = True
    response = client.get("/test-auth")
    assert response.status_code == 200
    assert response.json() == {"user_email": "test@test.com"}
    settings.test_mode = False

def test_auth_middleware_unauthorized():
    settings.test_mode = False
    response = client.get("/test-auth")
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}
