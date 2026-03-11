import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import get_db
from app.models.base import Base
from main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_create_product():
    response = client.post(
        "/products/",
        json={
            "name": "Test Product",
            "description": "A test product",
            "price": 10.99,
            "stock": 100,
            "image_url": "https://example.com/image.jpg"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Product"
    assert data["price"] == 10.99


def test_get_products():
    response = client.get("/products/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_product():
    response = client.post(
        "/products/",
        json={
            "name": "Another Product",
            "description": "Another test product",
            "price": 15.99,
            "stock": 50
        }
    )
    product_id = response.json()["id"]
    
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Another Product"


def test_get_nonexistent_product():
    response = client.get("/products/999")
    assert response.status_code == 404
