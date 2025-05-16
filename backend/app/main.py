# app/main.py

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from prometheus_client import Counter, Histogram
import time
from typing import Callable
import asyncio
from contextlib import asynccontextmanager

from app.core.config import settings, logger
from app.api.api_v1.api import api_router
from app.db.base import Base  # Import Base for metadata
from app.db.session import AsyncSessionLocal, engine # Import SessionLocal for startup event
from app.db import init_db # Import the init_db function

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

# Rate limiter setup
limiter = Limiter(
    key_func=get_remote_address,
    enabled=settings.RATE_LIMIT_ENABLED,
    storage_uri=settings.RATE_LIMIT_STORAGE_URI,
    strategy=settings.RATE_LIMIT_STRATEGY
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Handles database initialization and cleanup.
    """
    logger.info("Starting up TwinSecure AI Backend...")
    try:
        # Initialize database and create superuser
        async with AsyncSessionLocal() as db:
            await init_db(db)
        logger.info("Database initialization successful")

        # Initialize services
        from app.services.alerting.client import alert_client
        from app.services.enrichment.geoip import geoip_reader

        logger.info("Services initialized successfully")

        yield
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
        raise
    finally:
        logger.info("Shutting down TwinSecure AI Backend...")

        # Clean up services
        from app.services.enrichment.geoip import close_geoip_reader
        close_geoip_reader()

        # Close database connection
        await engine.dispose()
        logger.info("Shutdown complete")

# Create FastAPI app instance with advanced configuration
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# Rate limiting middleware
if settings.ENABLE_RATE_LIMITING:
    from app.middleware.rate_limiter import RateLimiterMiddleware

    # Parse rate limit string (e.g., "100/minute")
    rate_limit_parts = settings.RATE_LIMIT_DEFAULT.split('/')
    if len(rate_limit_parts) == 2:
        max_requests = int(rate_limit_parts[0])
        time_unit = rate_limit_parts[1].lower()

        # Convert time unit to seconds
        if time_unit == 'second':
            time_window = 1
        elif time_unit == 'minute':
            time_window = 60
        elif time_unit == 'hour':
            time_window = 3600
        elif time_unit == 'day':
            time_window = 86400
        else:
            time_window = 60  # Default to 1 minute

        # Add middleware with excluded paths
        app.add_middleware(
            RateLimiterMiddleware,
            max_requests=max_requests,
            time_window=time_window,
            exclude_paths=[
                r"^/api/v1/docs.*",  # Exclude Swagger docs
                r"^/api/v1/redoc.*",  # Exclude ReDoc
                r"^/api/v1/openapi.json",  # Exclude OpenAPI schema
                r"^/api/v1/health",  # Exclude health check
                r"^/static/.*",  # Exclude static files
            ]
        )
        logger.info(f"Rate limiting enabled: {max_requests} requests per {time_unit}")
    else:
        logger.warning(f"Invalid rate limit format: {settings.RATE_LIMIT_DEFAULT}. Rate limiting disabled.")

# CORS Configuration
origins_str = settings.BACKEND_CORS_ORIGINS
if isinstance(origins_str, str):
    allow_origins_list = [origin.strip() for origin in origins_str.split(",")] if origins_str else []
else:
    allow_origins_list = origins_str if origins_str else []

# Optional: Add logging to verify the list during startup
logger.info(f"Configuring CORS with allow_origins: {allow_origins_list}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_timing_middleware(request: Request, call_next: Callable):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(process_time)

    return response

# Error handling middleware
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next: Callable):
    try:
        response = await call_next(request)
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        return response
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}")
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=500
        ).inc()
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

# Include the main API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Advanced health check endpoint with detailed system status.
    """
    health_status = {
        "status": "ok",
        "version": settings.VERSION,
        "timestamp": time.time(),
        "components": {
            "database": "ok",
            "cache": "ok",
            "storage": "ok"
        }
    }

    # Check database connectivity
    try:
        async with AsyncSessionLocal() as db:
            from sqlalchemy import text
            await db.execute(text("SELECT 1"))
    except Exception as e:
        health_status["components"]["database"] = "error"
        health_status["database_error"] = str(e)

    return health_status

@app.get("/", tags=["Root"])
async def read_root():
    """
    Enhanced root endpoint with system information.
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "documentation": f"{settings.API_V1_STR}/docs",
        "status": "operational"
    }

# Metrics endpoint for Prometheus
@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """
    Expose Prometheus metrics.
    """
    from prometheus_client import generate_latest
    return Response(generate_latest(), media_type="text/plain")

# --- Example of adding Alembic commands (optional, usually run from CLI) ---
# You could potentially expose migration commands via API endpoints for specific use cases,
# but this is generally discouraged for security reasons.
# It's better to run `alembic upgrade head` during deployment.

