
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_customers_data():
    response = client.get("/data/customers", headers={"X-EMAIL-USER": "test@example.com"})
    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "name": "Alice Smith", "email": "alice@example.com"},
        {"id": 2, "name": "Bob Johnson", "email": "bob@example.com"},
    ]

def test_get_products_data():
    response = client.get("/data/products", headers={"X-EMAIL-USER": "test@example.com"})
    assert response.status_code == 200
    assert response.json() == [
        {"id": 101, "name": "Laptop", "price": 1200.00},
        {"id": 102, "name": "Mouse", "price": 25.00},
    ]

def test_get_nonexistent_data_source():
    response = client.get("/data/nonexistent", headers={"X-EMAIL-USER": "test@example.com"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Data source not found"}

def test_get_data_unauthorized():
    response = client.get("/data/customers")
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}
