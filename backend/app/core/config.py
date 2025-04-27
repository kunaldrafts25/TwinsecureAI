# app/core/config.py

import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import List, Union, Optional
from pydantic import AnyHttpUrl, EmailStr, validator

# Load environment variables from .env file (especially for local development)
# In production (e.g., EKS), environment variables are typically injected directly.
load_dotenv()

class Settings(BaseSettings):
    """
    Application configuration settings.
    Reads environment variables and provides typed configuration.
    """
    PROJECT_NAME: str = "TwinSecure AI Backend"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development" # development, staging, production
    LOG_LEVEL: str = "INFO"

    # --- Security ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- First Superuser ---
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    # --- Database ---
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: Optional[str] = None # Will be constructed

    @validator("DATABASE_URL", pre=True, always=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        # Construct async database URL
        return (
            f"postgresql+asyncpg://{values['POSTGRES_USER']}:{values['POSTGRES_PASSWORD']}"
            f"@{values['POSTGRES_SERVER']}:{values['POSTGRES_PORT']}/{values['POSTGRES_DB']}"
        )

    # --- CORS ---
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            # If it's a comma-separated string, split it
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(v) # Should be a list or comma-separated string

    # --- Alerting ---
    SLACK_WEBHOOK_URL: Optional[str] = None
    SLACK_CHANNEL: str = "#sec-alerts"
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    ALERT_RECIPIENTS: List[EmailStr] = []

    @validator("ALERT_RECIPIENTS", pre=True)
    def assemble_alert_recipients(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str):
            return [EmailStr(i.strip()) for i in v.split(",")]
        elif isinstance(v, list):
            return [EmailStr(i) for i in v]
        return [] # Return empty list if input is invalid or empty

    DISCORD_WEBHOOK_URL: Optional[str] = None

    # --- Enrichment Services ---
    ABUSEIPDB_API_KEY: Optional[str] = None
    ABUSEIPDB_API_URL: str = "https://api.abuseipdb.com/api/v2/check"
    MAXMIND_DB_PATH: Optional[str] = None

    # --- AWS ---
    AWS_REGION: Optional[str] = None
    AWS_SECRETS_MANAGER_SECRET_NAME: Optional[str] = None # For fetching secrets in prod

    # --- ML Module ---
    ML_MODEL_PATH: Optional[str] = None
    ML_TRAINING_SCHEDULE: Optional[str] = None # Cron format

    # --- Rate Limiting ---
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_DEFAULT: str = "100/minute"

    class Config:
        case_sensitive = True
        env_file = ".env" # Specify the env file (redundant with load_dotenv but good practice)

# Instantiate settings
settings = Settings()

# --- Logging Configuration (Basic Example) ---
# You might want to use a more sophisticated setup, e.g., with Loguru
import logging

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Example of how to fetch secrets from AWS Secrets Manager (conceptual)
# You would call this function during startup in a production environment
def load_secrets_from_aws():
    if settings.ENVIRONMENT != "development" and settings.AWS_SECRETS_MANAGER_SECRET_NAME:
        try:
            import boto3
            import json
            session = boto3.session.Session()
            client = session.client(service_name='secretsmanager', region_name=settings.AWS_REGION)
            get_secret_value_response = client.get_secret_value(SecretId=settings.AWS_SECRETS_MANAGER_SECRET_NAME)
            if 'SecretString' in get_secret_value_response:
                secret = json.loads(get_secret_value_response['SecretString'])
                # Override settings from the secret
                settings.POSTGRES_PASSWORD = secret.get("POSTGRES_PASSWORD", settings.POSTGRES_PASSWORD)
                settings.SECRET_KEY = secret.get("SECRET_KEY", settings.SECRET_KEY)
                settings.SMTP_PASSWORD = secret.get("SMTP_PASSWORD", settings.SMTP_PASSWORD)
                settings.ABUSEIPDB_API_KEY = secret.get("ABUSEIPDB_API_KEY", settings.ABUSEIPDB_API_KEY)
                # ... load other secrets
                logger.info("Successfully loaded secrets from AWS Secrets Manager.")
            else:
                # Handle binary secret if needed
                logger.warning("SecretString not found in AWS Secrets Manager response.")
        except ImportError:
            logger.error("Boto3 not installed. Cannot fetch secrets from AWS.")
        except Exception as e:
            logger.error(f"Error fetching secrets from AWS Secrets Manager: {e}")

# Uncomment to load secrets in non-dev environments on startup
# if settings.ENVIRONMENT != "development":
#     load_secrets_from_aws()

