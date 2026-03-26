"""
Tests for configuration management

Validates that configuration loading and validation work correctly.
"""

import os
import pytest
from pydantic import ValidationError


def test_config_loads_successfully():
    """Test that configuration loads with default values"""
    from app.core.config import Settings
    
    settings = Settings()
    
    assert settings.app_name == "ScholarGrid Backend API"
    assert settings.app_version == "0.1.0"
    assert settings.environment == "development"
    assert settings.rate_limit == 100


def test_cors_origins_list_property():
    """Test that CORS origins are parsed correctly"""
    from app.core.config import Settings
    
    settings = Settings(cors_origins="http://localhost:3000,http://localhost:5173")
    
    origins = settings.cors_origins_list
    assert len(origins) == 2
    assert "http://localhost:3000" in origins
    assert "http://localhost:5173" in origins


def test_is_production_property():
    """Test production environment detection"""
    from app.core.config import Settings
    
    dev_settings = Settings(environment="development")
    assert dev_settings.is_production is False
    
    prod_settings = Settings(
        environment="production",
        secret_key="a" * 32,
        gemini_api_key="test_key"
    )
    assert prod_settings.is_production is True


def test_invalid_database_url():
    """Test that invalid DATABASE_URL raises validation error"""
    from app.core.config import Settings
    
    with pytest.raises(ValidationError) as exc_info:
        Settings(database_url="mysql://localhost:3306/db")
    
    assert "DATABASE_URL must be a valid PostgreSQL connection string" in str(exc_info.value)


def test_invalid_redis_url():
    """Test that invalid REDIS_URL raises validation error"""
    from app.core.config import Settings
    
    with pytest.raises(ValidationError) as exc_info:
        Settings(redis_url="http://localhost:6379")
    
    assert "REDIS_URL must be a valid Redis connection string" in str(exc_info.value)


def test_invalid_rate_limit():
    """Test that invalid RATE_LIMIT raises validation error"""
    from app.core.config import Settings
    
    with pytest.raises(ValidationError) as exc_info:
        Settings(rate_limit=0)
    
    assert "RATE_LIMIT must be a positive integer" in str(exc_info.value)


def test_production_secret_key_validation():
    """Test that production requires a secure SECRET_KEY"""
    from app.core.config import Settings
    
    # Should fail with default dev secret key
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            environment="production",
            secret_key="dev-secret-key-change-in-production"
        )
    
    assert "SECRET_KEY must be set to a secure value" in str(exc_info.value)
    
    # Should fail with short secret key
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            environment="production",
            secret_key="short"
        )
    
    assert "SECRET_KEY must be set to a secure value" in str(exc_info.value)
    
    # Should succeed with proper secret key
    settings = Settings(
        environment="production",
        secret_key="a" * 32,
        gemini_api_key="test_key"
    )
    assert settings.secret_key == "a" * 32


def test_production_gemini_api_key_validation():
    """Test that production requires GEMINI_API_KEY"""
    from app.core.config import Settings
    
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            environment="production",
            secret_key="a" * 32,
            gemini_api_key=""
        )
    
    assert "GEMINI_API_KEY must be set in production environment" in str(exc_info.value)
