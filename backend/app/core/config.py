# app/core/config.py

import json
import os
import secrets
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, EmailStr, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings

# Load environment variables from .env file (especially for local development)
# In production (e.g., EKS), environment variables are typically injected directly.
load_dotenv()


class CacheSettings(BaseSettings):
    """Cache configuration settings"""

    REDIS_URL: Optional[str] = None
    REDIS_PASSWORD: Optional[SecretStr] = None
    CACHE_TTL: int = 3600  # Default TTL in seconds
    CACHE_PREFIX: str = "twinsecure:"
    CACHE_ENABLED: bool = True
    CACHE_MAX_SIZE: int = 1000  # Maximum number of items in the in-memory cache
    CACHE_DEFAULT_TTL: int = 60  # Default TTL for in-memory cache in seconds
    CACHE_EXCLUDE_PATHS: List[str] = [
        "/api/v1/auth/",
        "/api/v1/users/me",
        "/api/v1/health",
        "/metrics",
    ]
    CACHE_EXCLUDE_QUERY_PARAMS: List[str] = ["_", "timestamp", "nocache"]


class SecuritySettings(BaseSettings):
    """Security-related settings"""

    SECRET_KEY: SecretStr = Field(
        default_factory=lambda: SecretStr(secrets.token_urlsafe(32))
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_MIN_LENGTH: int = 12
    PASSWORD_MAX_LENGTH: int = 128
    PASSWORD_PATTERN: str = (
        r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{12,}$"
    )
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
    RATE_LIMIT_STORAGE_URI: Optional[str] = None
    RATE_LIMIT_STRATEGY: str = "fixed-window"
    JWT_BLACKLIST_ENABLED: bool = True
    JWT_BLACKLIST_TOKEN_CHECKS: List[str] = ["access", "refresh"]


class DatabaseSettings(BaseSettings):
    """Database configuration settings"""

    POSTGRES_SERVER: str = (
        "localhost"  # Changed from twinsecure_db to localhost for local development
    )
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: SecretStr = Field(
        default_factory=lambda: SecretStr("kUNAL@#$12345")
    )
    POSTGRES_DB: str = "TwinSecure"  # Ensure consistent capitalization
    DATABASE_URL: Optional[str] = None
    POOL_SIZE: int = 20
    MAX_OVERFLOW: int = 10
    ECHO: bool = False
    ECHO_POOL: bool = False
    POOL_TIMEOUT: int = 30
    POOL_RECYCLE: int = 1800

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: Optional[str], info) -> str:
        if isinstance(v, str):
            return v
        values = info.data
        password = values["POSTGRES_PASSWORD"].get_secret_value()
        # URL encode special characters in password
        password = password.replace("@", "%40").replace("#", "%23").replace("$", "%24")
        db_name = values["POSTGRES_DB"]  # Get the database name
        print(f"Using database name: {db_name}")  # Debug print
        return (
            f"postgresql+asyncpg://{values['POSTGRES_USER']}:{password}"
            f"@{values['POSTGRES_SERVER']}:{values['POSTGRES_PORT']}/{db_name}"
        )


class GeoIP2Settings(BaseSettings):
    """GeoIP2 configuration settings."""

    enabled: bool = True
    db_path: str = r"E:\ts\GeoLite2-City.mmdb"
    license_key: Optional[str] = Field(
        None, description="MaxMind license key for GeoLite2 database"
    )

    class Config:
        env_prefix = "MAXMIND_"
        case_sensitive = True
        validate_by_name = True


class Settings(BaseSettings):
    """
    Application configuration settings with advanced features.
    """

    # Basic Settings
    PROJECT_NAME: str = "TwinSecure AI Backend"
    PROJECT_DESCRIPTION: str = "Advanced Security and AI Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = Field(
        "development", pattern="^(development|staging|production)$"
    )
    LOG_LEVEL: str = Field("INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    DEBUG: bool = False

    # Feature Flags
    ENABLE_ML: bool = True
    ENABLE_ALERTING: bool = True
    ENABLE_METRICS: bool = True
    ENABLE_CACHING: bool = True
    ENABLE_RATE_LIMITING: bool = True

    # Nested Settings
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    geoip2: GeoIP2Settings = Field(default_factory=GeoIP2Settings)

    # MaxMind Settings
    MAXMIND_LICENSE_KEY: Optional[str] = None

    # Rate Limiting Settings
    ENABLE_RATE_LIMITING: bool = True
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_STORAGE_URI: str = "memory://"
    RATE_LIMIT_STRATEGY: str = "fixed-window"

    # Security Settings
    SECURITY__SECRET_KEY: SecretStr = Field(
        default_factory=lambda: SecretStr(secrets.token_urlsafe(32))
    )
    SECURITY__ALGORITHM: str = "HS256"
    SECURITY__ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SECURITY__REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SECURITY__PASSWORD_MIN_LENGTH: int = 12
    SECURITY__PASSWORD_MAX_LENGTH: int = 128
    SECURITY__PASSWORD_PATTERN: str = (
        r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{12,}$"
    )
    SECURITY__SESSION_COOKIE_NAME: str = "twinsecure_session"
    SECURITY__SESSION_COOKIE_SECURE: bool = True
    SECURITY__SESSION_COOKIE_HTTPONLY: bool = True
    SECURITY__SESSION_COOKIE_SAMESITE: str = "Lax"
    SECURITY__CSRF_COOKIE_NAME: str = "twinsecure_csrf"
    SECURITY__CSRF_COOKIE_SECURE: bool = True
    SECURITY__CSRF_COOKIE_HTTPONLY: bool = True
    SECURITY__CSRF_COOKIE_SAMESITE: str = "Lax"
    SECURITY__RATE_LIMIT_ENABLED: bool = True
    SECURITY__RATE_LIMIT_DEFAULT: str = "100/minute"
    SECURITY__JWT_BLACKLIST_ENABLED: bool = True
    SECURITY__JWT_BLACKLIST_TOKEN_CHECKS: List[str] = ["access", "refresh"]

    # Database Settings
    POSTGRES_SERVER: str = (
        "localhost"  # Changed from twinsecure_db to localhost for local development
    )
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: SecretStr = Field(
        default_factory=lambda: SecretStr("kUNAL@#$12345")
    )
    POSTGRES_DB: str = "TwinSecure"  # Ensure consistent capitalization
    DATABASE_URL: Optional[str] = None

    # Cache Settings
    REDIS_URL: Optional[str] = None
    REDIS_PASSWORD: Optional[SecretStr] = None
    CACHE_TTL: int = 3600
    CACHE_PREFIX: str = "twinsecure:"
    CACHE_ENABLED: bool = True
    CACHE_MAX_SIZE: int = 1000
    CACHE_DEFAULT_TTL: int = 60
    CACHE_EXCLUDE_PATHS: List[str] = [
        "/api/v1/auth/",
        "/api/v1/users/me",
        "/api/v1/health",
        "/metrics",
    ]
    CACHE_EXCLUDE_QUERY_PARAMS: List[str] = ["_", "timestamp", "nocache"]

    # Alerting Settings
    SLACK_WEBHOOK_URL: Optional[str] = None
    SLACK_CHANNEL: str = "#sec-alerts"
    DISCORD_WEBHOOK_URL: Optional[str] = None
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[SecretStr] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    ALERT_RECIPIENTS: List[EmailStr] = []

    # Enrichment Services
    ABUSEIPDB_API_KEY: Optional[SecretStr] = None
    ABUSEIPDB_API_URL: str = "https://api.abuseipdb.com/api/v2/check"
    MAXMIND_DB_PATH: Optional[Path] = None

    # AWS Settings
    AWS_REGION: Optional[str] = None
    AWS_SECRETS_MANAGER_SECRET_NAME: Optional[str] = None
    AWS_ACCESS_KEY_ID: Optional[SecretStr] = None
    AWS_SECRET_ACCESS_KEY: Optional[SecretStr] = None

    # ML Settings
    ML_MODEL_PATH: Optional[Path] = None
    ML_TRAINING_SCHEDULE: Optional[str] = None
    ML_BATCH_SIZE: int = 32
    ML_LEARNING_RATE: float = 0.001
    ML_EPOCHS: int = 100

    # Metrics Settings
    PROMETHEUS_MULTIPROC_DIR: Optional[Path] = None
    ENABLE_PROMETHEUS: bool = True
    METRICS_PORT: int = 9090

    # First Superuser
    FIRST_SUPERUSER: EmailStr = Field(default="admin@example.com")
    FIRST_SUPERUSER_PASSWORD: SecretStr = Field(
        default_factory=lambda: SecretStr("admin123")
    )

    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: Optional[str], info) -> str:
        if isinstance(v, str):
            return v
        values = info.data
        password = values["POSTGRES_PASSWORD"].get_secret_value()
        # URL encode special characters in password
        password = password.replace("@", "%40").replace("#", "%23").replace("$", "%24")
        return (
            f"postgresql+asyncpg://{values['POSTGRES_USER']}:{password}"
            f"@{values['POSTGRES_SERVER']}:{values['POSTGRES_PORT']}/{values['POSTGRES_DB']}"
        )

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_nested_delimiter = "__"
        validate_by_name = True
        extra = "allow"  # Allow extra fields from environment variables

    def generate_secret_key(self) -> str:
        """Generate a secure secret key if not set"""
        if not self.SECURITY__SECRET_KEY:
            return secrets.token_urlsafe(32)
        return self.SECURITY__SECRET_KEY.get_secret_value()

    def get_cors_origins(self) -> List[str]:
        """Get CORS origins with validation"""
        if not self.BACKEND_CORS_ORIGINS:
            return ["http://localhost:3000"]  # Default for development
        return self.BACKEND_CORS_ORIGINS


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Initialize settings
settings = get_settings()

# Advanced logging configuration
import logging
import logging.handlers
from pathlib import Path


def setup_logging():
    """Configure advanced logging with rotation and formatting"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Create formatters
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Create handlers
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "app.log", maxBytes=10_000_000, backupCount=5  # 10MB
    )
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Create application logger
    logger = logging.getLogger(__name__)
    return logger


logger = setup_logging()


# AWS Secrets Manager integration
def load_secrets_from_aws() -> None:
    """Load secrets from AWS Secrets Manager with error handling and retries"""
    if (
        settings.ENVIRONMENT != "development"
        and settings.AWS_SECRETS_MANAGER_SECRET_NAME
    ):
        try:
            import backoff
            import boto3
            from botocore.exceptions import ClientError

            @backoff.on_exception(backoff.expo, ClientError, max_tries=3)
            def get_secret():
                session = boto3.session.Session(
                    aws_access_key_id=(
                        settings.AWS_ACCESS_KEY_ID.get_secret_value()
                        if settings.AWS_ACCESS_KEY_ID
                        else None
                    ),
                    aws_secret_access_key=(
                        settings.AWS_SECRET_ACCESS_KEY.get_secret_value()
                        if settings.AWS_SECRET_ACCESS_KEY
                        else None
                    ),
                    region_name=settings.AWS_REGION,
                )
                client = session.client(
                    service_name="secretsmanager", region_name=settings.AWS_REGION
                )
                return client.get_secret_value(
                    SecretId=settings.AWS_SECRETS_MANAGER_SECRET_NAME
                )

            response = get_secret()
            if "SecretString" in response:
                secret = json.loads(response["SecretString"])
                # Update settings with secrets
                for key, value in secret.items():
                    if hasattr(settings, key):
                        setattr(settings, key, value)
                logger.info("Successfully loaded secrets from AWS Secrets Manager")
            else:
                logger.warning("SecretString not found in AWS Secrets Manager response")
        except ImportError:
            logger.error("Boto3 not installed. Cannot fetch secrets from AWS")
        except Exception as e:
            logger.error(f"Error fetching secrets from AWS Secrets Manager: {e}")
            raise


# Load secrets in non-dev environments
if settings.ENVIRONMENT != "development":
    load_secrets_from_aws()
