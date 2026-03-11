import pytest
import os
import sys
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import get_db
from app.models.base import Base

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

# Base de datos para testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Crear las tablas antes de los tests
Base.metadata.create_all(bind=engine)

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def cleanup():
    """Cleanup después de todos los tests"""
    yield
    # Limpiar la base de datos después de los tests
    Base.metadata.drop_all(bind=engine)


def test_root_endpoint():
    """Test del endpoint raíz"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_check():
    """Test del health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_create_product():
    """Test de creación de producto"""
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
    assert data["stock"] == 100
    assert "id" in data


def test_get_products_empty():
    """Test obtener productos cuando está vacío"""
    response = client.get("/products/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_products_with_data():
    """Test obtener productos con datos"""
    # Primero crear un producto
    create_response = client.post(
        "/products/",
        json={
            "name": "Another Product",
            "description": "Another test product",
            "price": 15.99,
            "stock": 50
        }
    )
    assert create_response.status_code == 200
    
    # Ahora obtener todos los productos
    response = client.get("/products/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_product():
    """Test obtener producto por ID"""
    # Crear un producto primero
    create_response = client.post(
        "/products/",
        json={
            "name": "Product for Get Test",
            "description": "Product to test GET endpoint",
            "price": 25.99,
            "stock": 75
        }
    )
    assert create_response.status_code == 200
    product_id = create_response.json()["id"]
    
    # Obtener el producto
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Product for Get Test"
    assert data["price"] == 25.99


def test_get_nonexistent_product():
    """Test obtener producto que no existe"""
    response = client.get("/products/99999")
    assert response.status_code == 404


def test_create_product_invalid_data():
    """Test crear producto con datos inválidos"""
    response = client.post(
        "/products/",
        json={
            "name": "",  # Nombre vacío inválido
            "price": -10,  # Precio negativo inválido
            "stock": -5  # Stock negativo inválido
        }
    )
    # FastAPI debería validar los datos con Pydantic
    assert response.status_code == 422  # Unprocessable Entity
    
    # Verificar que el mensaje de error contiene información sobre los campos inválidos
    data = response.json()
    assert "detail" in data


def test_update_product():
    """Test actualizar producto"""
    # Crear un producto
    create_response = client.post(
        "/products/",
        json={
            "name": "Product to Update",
            "description": "Original description",
            "price": 20.00,
            "stock": 30
        }
    )
    assert create_response.status_code == 200
    product_id = create_response.json()["id"]
    
    # Actualizar el producto
    update_response = client.put(
        f"/products/{product_id}",
        json={
            "name": "Updated Product",
            "description": "Updated description",
            "price": 25.00,
            "stock": 40
        }
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "Updated Product"
    assert data["price"] == 25.00


def test_delete_product():
    """Test eliminar producto"""
    # Crear un producto
    create_response = client.post(
        "/products/",
        json={
            "name": "Product to Delete",
            "description": "This will be deleted",
            "price": 30.00,
            "stock": 20
        }
    )
    assert create_response.status_code == 200
    product_id = create_response.json()["id"]
    
    # Eliminar el producto
    delete_response = client.delete(f"/products/{product_id}")
    assert delete_response.status_code == 200
    
    # Verificar que ya no existe
    get_response = client.get(f"/products/{product_id}")
    assert get_response.status_code == 404
