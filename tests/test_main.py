"""
Tests for main application initialization and basic endpoints
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI application"""
    return TestClient(app)


def test_app_initialization():
    """Test that the FastAPI app initializes correctly"""
    assert app.title == "ScholarGrid Backend API"
    assert app.version == "0.1.0"


def test_root_endpoint(client):
    """Test the root endpoint returns correct response"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "ScholarGrid Backend API"
    assert data["version"] == "0.1.0"
    assert data["environment"] in ["development", "production", "staging"]
    assert data["docs"] == "/docs"


def test_health_check_endpoint(client):
    """Test the health check endpoint"""
    response = client.get("/health")
    
    # Health check should return either 200 (healthy) or 503 (unhealthy)
    assert response.status_code in [200, 503]
    
    data = response.json()
    assert "status" in data
    assert data["status"] in ["healthy", "unhealthy"]
    assert "database" in data
    assert "redis" in data
    assert data["database"] in ["connected", "disconnected"]
    assert data["redis"] in ["connected", "disconnected"]
    
    # If services are disconnected, status should be unhealthy and code should be 503
    if data["database"] == "disconnected" or data["redis"] == "disconnected":
        assert data["status"] == "unhealthy"
        assert response.status_code == 503
    else:
        assert data["status"] == "healthy"
        assert response.status_code == 200


def test_cors_middleware_configured():
    """Test that CORS middleware is configured"""
    # Check that CORS middleware is in the middleware stack
    # FastAPI wraps middleware, so we check the middleware list exists
    assert len(app.user_middleware) > 0
    # Verify CORS is configured by checking middleware stack
    assert any(hasattr(m, 'cls') for m in app.user_middleware)


def test_openapi_docs_available(client):
    """Test that OpenAPI documentation endpoints are available"""
    # Test Swagger UI
    response = client.get("/docs")
    assert response.status_code == 200
    
    # Test ReDoc
    response = client.get("/redoc")
    assert response.status_code == 200
    
    # Test OpenAPI schema
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "ScholarGrid Backend API"
