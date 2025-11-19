"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.
"""

import logging
import logging.handlers
import secrets
from functools import lru_cache
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

from dotenv import load_dotenv
from pydantic import EmailStr, Field, SecretStr, ValidationInfo, field_validator, model_validator
from pydantic_settings import BaseSettings

load_dotenv()


class SecuritySettings(BaseSettings):
    """Security-related settings"""
    
    model_config = {
        "arbitrary_types_allowed": True
    }
    
    SECRET_KEY: SecretStr = Field(
        default_factory=lambda: SecretStr(secrets.token_urlsafe(32))
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_MIN_LENGTH: int = 12
    PASSWORD_MAX_LENGTH: int = 128
    PASSWORD_PATTERN: str = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{12,}$"
    
    SESSION_COOKIE_NAME: str = "twinsecure_session"
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"
    
    CSRF_COOKIE_NAME: str = "twinsecure_csrf"
    CSRF_COOKIE_SECURE: bool = True
    CSRF_COOKIE_HTTPONLY: bool = True
    CSRF_COOKIE_SAMESITE: str = "Lax"
    
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_STORAGE_URI: str = "memory://"
    RATE_LIMIT_STRATEGY: str = "fixed-window"
    
    JWT_BLACKLIST_ENABLED: bool = True
    JWT_BLACKLIST_TOKEN_CHECKS: list[str] = Field(default_factory=lambda: ["access", "refresh"])


class DatabaseSettings(BaseSettings):
    """Database configuration settings"""
    
    model_config = {
        "arbitrary_types_allowed": True
    }
    
    # SQLite settings (default)
    SQLITE_DB_PATH: str = Field(default="./twinsecure.db")
    DATABASE_TYPE: str = Field(default="sqlite")  # "sqlite" or "postgres"
    
    # PostgreSQL settings (optional, only used if DATABASE_TYPE=postgres)
    POSTGRES_SERVER: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: SecretStr | None = None
    POSTGRES_DB: str = Field(default="TwinSecure")
    
    DATABASE_URL: str | None = None
    
    POOL_SIZE: int = 20
    MAX_OVERFLOW: int = 10
    ECHO: bool = False
    ECHO_POOL: bool = False
    POOL_TIMEOUT: int = 30
    POOL_RECYCLE: int = 1800
    
    @model_validator(mode="after")
    def assemble_db_connection(self) -> "DatabaseSettings":
        """Construct DATABASE_URL from components if not provided"""
        if self.DATABASE_URL:
            return self
        
        db_type = self.DATABASE_TYPE.lower() if self.DATABASE_TYPE else "sqlite"
        
        if db_type == "postgres":
            # PostgreSQL connection
            if not self.POSTGRES_PASSWORD:
                raise ValueError("POSTGRES_PASSWORD is required when using PostgreSQL")
            
            password = self.POSTGRES_PASSWORD
            if isinstance(password, SecretStr):
                password = password.get_secret_value()
            
            password = quote_plus(password)
            
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{password}"
                f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}"
                f"/{self.POSTGRES_DB}"
            )
        else:
            # SQLite connection (default)
            self.DATABASE_URL = f"sqlite+aiosqlite:///{self.SQLITE_DB_PATH}"
        
        return self


class CacheSettings(BaseSettings):
    """Cache configuration settings"""
    
    model_config = {
        "arbitrary_types_allowed": True
    }
    
    REDIS_URL: str | None = None
    REDIS_PASSWORD: SecretStr | None = None
    CACHE_TTL: int = 3600
    CACHE_PREFIX: str = "twinsecure:"
    CACHE_ENABLED: bool = True
    CACHE_MAX_SIZE: int = 1000
    CACHE_DEFAULT_TTL: int = 60
    CACHE_EXCLUDE_PATHS: list[str] = [
        "/api/v1/auth/",
        "/api/v1/users/me",
        "/api/v1/health",
    ]
    CACHE_EXCLUDE_QUERY_PARAMS: list[str] = ["_", "timestamp", "nocache"]


class GeoIP2Settings(BaseSettings):
    """GeoIP2 configuration settings"""
    
    model_config = {
        "env_prefix": "MAXMIND_",
        "case_sensitive": True,
        "arbitrary_types_allowed": True
    }
    
    enabled: bool = Field(default=True)
    db_path: str | None = Field(default=None)
    license_key: str | None = Field(default=None)


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Basic Settings
    PROJECT_NAME: str = "TwinSecure AI Backend"
    PROJECT_DESCRIPTION: str = "Advanced Security and AI Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = Field(
        "development", pattern="^(development|staging|production)$"
    )
    LOG_LEVEL: str = Field("INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    
    # Feature Flags
    ENABLE_ML: bool = True
    ENABLE_ALERTING: bool = True
    ENABLE_CACHING: bool = True
    ENABLE_RATE_LIMITING: bool = True
    
    # Nested Settings
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    geoip2: GeoIP2Settings = Field(default_factory=GeoIP2Settings)
    
    # Backward Compatibility (access via settings.database.* instead)
    # These are optional now - only needed if using PostgreSQL
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: SecretStr | None = None
    POSTGRES_DB: str = "TwinSecure"
    DATABASE_URL: str | None = None
    DATABASE_TYPE: str = "sqlite"  # Default to SQLite
    SQLITE_DB_PATH: str = "./twinsecure.db"
    
    # Alerting Settings
    SLACK_WEBHOOK_URL: str | None = None
    SLACK_CHANNEL: str = "#sec-alerts"
    DISCORD_WEBHOOK_URL: str | None = None
    SMTP_TLS: bool = True
    SMTP_PORT: int | None = None
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: SecretStr | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: str | None = None
    
    @field_validator("EMAILS_FROM_EMAIL", mode="before")
    def validate_email_from(cls, v: str | None) -> str | None:
        if v is None or v == "" or not v.strip():
            return None
        return v.strip()
    ALERT_RECIPIENTS: list[EmailStr] | None = None
    
    @field_validator("ALERT_RECIPIENTS", mode="before")
    def assemble_alert_recipients(cls, v: str | list[str] | None) -> list[str] | None:
        if v is None or v == "":
            return None
        if isinstance(v, str):
            # Handle empty string
            if not v.strip() or v.strip() == "[]":
                return None
            # Try to parse as JSON first (for array format)
            try:
                import json
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed if parsed else None
            except (json.JSONDecodeError, ValueError):
                pass
            # Otherwise, treat as comma-separated
            result = [email.strip() for email in v.split(",") if email.strip()]
            return result if result else None
        if isinstance(v, list):
            return v if v else None
        return None
    
    @model_validator(mode="after")
    def set_default_list_fields(self):
        if self.ALERT_RECIPIENTS is None:
            self.ALERT_RECIPIENTS = []
        if self.BACKEND_CORS_ORIGINS is None:
            self.BACKEND_CORS_ORIGINS = []
        # Set JWT_BLACKLIST_TOKEN_CHECKS if it wasn't set properly due to env parsing issues
        if not hasattr(self.security, 'JWT_BLACKLIST_TOKEN_CHECKS') or not self.security.JWT_BLACKLIST_TOKEN_CHECKS:
            self.security.JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
        return self
    
    # Enrichment Services
    ABUSEIPDB_API_KEY: SecretStr | None = None
    ABUSEIPDB_API_URL: str = "https://api.abuseipdb.com/api/v2/check"
    MAXMIND_DB_PATH: Path | None = None
    MAXMIND_LICENSE_KEY: str | None = None
    
    # Honeypot Security
    HONEYPOT_SECRET_HEADER: str | None = None
    
    # ML Settings
    ML_MODEL_PATH: Path | None = None
    ML_BATCH_SIZE: int = 32
    ML_LEARNING_RATE: float = 0.001
    ML_EPOCHS: int = 100
    
    # First Superuser
    FIRST_SUPERUSER: EmailStr = Field(default="admin@example.com")
    FIRST_SUPERUSER_PASSWORD: SecretStr
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: list[str] | None = None
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: str | list[str] | None) -> list[str] | None:
        if v is None or v == "":
            return None
        if isinstance(v, str):
            # Handle empty string
            if not v.strip() or v.strip() == "[]":
                return None
            # Try to parse as JSON first (for array format)
            try:
                import json
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed if parsed else None
            except (json.JSONDecodeError, ValueError):
                pass
            # Otherwise, treat as comma-separated
            result = [origin.strip() for origin in v.split(",") if origin.strip()]
            return result if result else None
        if isinstance(v, list):
            return v if v else None
        return None
    
    @model_validator(mode="after")
    def assemble_settings_db_connection(self) -> "Settings":
        """Construct DATABASE_URL from components if not provided"""
        if self.DATABASE_URL:
            return self
        
        db_type = self.DATABASE_TYPE.lower() if self.DATABASE_TYPE else "sqlite"
        
        if db_type == "postgres":
            # PostgreSQL connection
            if not self.POSTGRES_PASSWORD:
                raise ValueError("POSTGRES_PASSWORD is required when using PostgreSQL")
            
            password = self.POSTGRES_PASSWORD
            if isinstance(password, SecretStr):
                password = password.get_secret_value()
            
            password = quote_plus(password)
            
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{password}"
                f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}"
                f"/{self.POSTGRES_DB}"
            )
        else:
            # SQLite connection (default)
            self.DATABASE_URL = f"sqlite+aiosqlite:///{self.SQLITE_DB_PATH}"
        
        return self
    
    def get_cors_origins(self) -> list[str]:
        """Get CORS origins with default for development"""
        if not self.BACKEND_CORS_ORIGINS:
            return ["http://localhost:3000"]
        return self.BACKEND_CORS_ORIGINS
    
    
    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "env_nested_delimiter": "__",
        "extra": "allow",
        "arbitrary_types_allowed": True
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    import os
    # Temporarily remove problematic environment variables if they exist and are empty/invalid
    jwt_env_vars = ["SECURITY__JWT_BLACKLIST_TOKEN_CHECKS", "JWT_BLACKLIST_TOKEN_CHECKS"]
    saved_values = {}
    for var in jwt_env_vars:
        if var in os.environ:
            val = os.environ[var]
            # If the value is empty or would cause JSON parsing errors, remove it
            if not val or val.strip() == "":
                saved_values[var] = None
                del os.environ[var]
            else:
                # Try to validate it's valid JSON
                try:
                    import json
                    json.loads(val)
                except (json.JSONDecodeError, ValueError):
                    # Invalid JSON, remove it
                    saved_values[var] = val
                    del os.environ[var]
    
    try:
        return Settings()
    except Exception as e:
        # If there's still an error, restore env vars and try with a default
        for var, val in saved_values.items():
            if val is not None:
                os.environ[var] = val
        # Try one more time - if it still fails, raise
        return Settings()


settings = get_settings()


def setup_logging() -> logging.Logger:
    """Configure logging with rotation and formatting"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10_000_000,
        backupCount=5
    )
    file_handler.setFormatter(file_formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return logging.getLogger(__name__)


logger = setup_logging()
