"""
Configuration management for ScholarGrid Backend API

Loads configuration from environment variables with validation and defaults.
"""

import os
import sys
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, computed_field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Application
    app_name: str = "ScholarGrid Backend API"
    app_version: str = "0.1.0"
    environment: str = "development"
    secret_key: str = "dev-secret-key-change-in-production"
    
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/scholargrid"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Firebase
    firebase_credentials_path: str = "./firebase-credentials.json"
    
    # Google Gemini API
    gemini_api_key: str = ""
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    # Rate Limiting
    rate_limit: int = 100
    
    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v, info):
        """Validate SECRET_KEY is set properly in production"""
        environment = info.data.get("environment", "development")
        if environment.lower() == "production":
            if v == "dev-secret-key-change-in-production" or len(v) < 32:
                raise ValueError(
                    "SECRET_KEY must be set to a secure value (at least 32 characters) in production"
                )
        return v
    
    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v):
        """Validate DATABASE_URL is properly formatted"""
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError(
                "DATABASE_URL must be a valid PostgreSQL connection string"
            )
        return v
    
    @field_validator("redis_url")
    @classmethod
    def validate_redis_url(cls, v):
        """Validate REDIS_URL is properly formatted"""
        if not v.startswith("redis://"):
            raise ValueError(
                "REDIS_URL must be a valid Redis connection string"
            )
        return v
    
    @field_validator("firebase_credentials_path")
    @classmethod
    def validate_firebase_credentials(cls, v):
        """Validate Firebase credentials file exists"""
        if not os.path.exists(v):
            print(f"Warning: Firebase credentials file not found at {v}", file=sys.stderr)
        return v
    
    @field_validator("gemini_api_key")
    @classmethod
    def validate_gemini_api_key(cls, v, info):
        """Validate GEMINI_API_KEY is set in production"""
        environment = info.data.get("environment", "development")
        if environment.lower() == "production" and not v:
            raise ValueError(
                "GEMINI_API_KEY must be set in production environment"
            )
        return v
    
    @field_validator("rate_limit")
    @classmethod
    def validate_rate_limit(cls, v):
        """Validate RATE_LIMIT is a positive integer"""
        if v <= 0:
            raise ValueError("RATE_LIMIT must be a positive integer")
        return v
    
    @computed_field
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @computed_field
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"


def validate_configuration():
    """
    Validate configuration on startup.
    
    This function is called during application initialization to ensure
    all required configuration is present and valid. If validation fails,
    the application will not start.
    
    Raises:
        ValueError: If required configuration is missing or invalid
        SystemExit: If critical configuration errors prevent startup
    """
    try:
        # Attempt to instantiate settings - this triggers all validators
        settings = Settings()
        
        # Additional production checks
        if settings.is_production:
            # Ensure production-specific requirements
            if "localhost" in settings.database_url:
                raise ValueError(
                    "DATABASE_URL cannot use localhost in production"
                )
            
            if "localhost" in settings.redis_url:
                raise ValueError(
                    "REDIS_URL cannot use localhost in production"
                )
            
            if "localhost" in settings.cors_origins.lower():
                print(
                    "Warning: CORS_ORIGINS contains localhost in production environment",
                    file=sys.stderr
                )
        
        return settings
    
    except ValueError as e:
        print(f"Configuration validation failed: {e}", file=sys.stderr)
        sys.exit(1)


# Global settings instance with validation
settings = validate_configuration()
