"""
Tests for configuration validation on startup

Validates that the validate_configuration function works correctly.
"""

import os
import pytest


def test_validate_configuration_success():
    """Test that validate_configuration succeeds with valid config"""
    from app.core.config import validate_configuration
    
    settings = validate_configuration()
    
    assert settings is not None
    assert settings.app_name == "ScholarGrid Backend API"
    assert settings.environment == "development"


def test_configuration_from_env_file():
    """Test that configuration loads from .env file"""
    # This test verifies the Config class is set up correctly
    from app.core.config import Settings
    
    settings = Settings()
    
    # Verify Config class settings
    assert settings.Config.env_file == ".env"
    assert settings.Config.env_file_encoding == "utf-8"
    assert settings.Config.case_sensitive is False


def test_production_validation_checks():
    """Test that production environment has additional validation"""
    from app.core.config import Settings
    
    # Test that production requires secure secret key
    with pytest.raises(Exception) as exc_info:
        Settings(
            environment="production",
            secret_key="short",
            gemini_api_key="test"
        )
    assert "SECRET_KEY" in str(exc_info.value)
    
    # Test that production requires gemini api key
    with pytest.raises(Exception) as exc_info:
        Settings(
            environment="production",
            secret_key="a" * 32,
            gemini_api_key=""
        )
    assert "GEMINI_API_KEY" in str(exc_info.value)
