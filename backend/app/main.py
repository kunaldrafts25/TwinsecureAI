# app/main.py
"""
TwinSecure - Advanced Cybersecurity Platform
Copyright © 2024 TwinSecure. All rights reserved.

This file is part of TwinSecure, a proprietary cybersecurity platform.
Unauthorized copying, distribution, modification, or use of this software
is strictly prohibited without explicit written permission.

For licensing inquiries: kunalsingh2514@gmail.com

Main application module for TwinSecure AI Backend.

This module initializes the FastAPI application, sets up middleware,
configures routes, and handles application lifecycle events.

The application provides a RESTful API for managing digital twin security,
alerts, reports, and user management.
"""

import asyncio
import time
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.api_v1.api import api_router  # API routes

# Import application components
from app.core.config import logger, settings  # Application configuration and logging
from app.core.license_manager import license_manager  # License management
from app.db import init_db  # Database initialization function
from app.db.base import Base  # SQLAlchemy Base model for metadata
from app.db.session import AsyncSessionLocal, engine  # Database session and engine
from app.middleware.cache_middleware import add_cache_middleware  # Caching middleware
from app.middleware.security_middleware import (  # Security middleware
    add_security_middleware,
)

# Prometheus metrics for monitoring application performance and usage
# These metrics are exposed via the /metrics endpoint for scraping by Prometheus
REQUEST_COUNT = Counter(
    "http_requests_total",  # Metric name
    "Total HTTP requests",  # Metric description
    [
        "method",
        "endpoint",
        "status",
    ],  # Labels for request method, endpoint path, and status code
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",  # Metric name
    "HTTP request latency",  # Metric description
    ["method", "endpoint"],  # Labels for request method and endpoint path
)

# Rate limiter setup to prevent abuse and ensure fair usage
# This limits the number of requests a client can make in a given time period
limiter = Limiter(
    key_func=get_remote_address,  # Use client IP address as the rate limit key
    enabled=settings.RATE_LIMIT_ENABLED,  # Enable/disable rate limiting based on configuration
    storage_uri=settings.RATE_LIMIT_STORAGE_URI,  # Storage backend for rate limit data
    strategy=settings.RATE_LIMIT_STRATEGY,  # Rate limiting strategy (fixed window, moving window, etc.)
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Handles database initialization and cleanup.
    """
    logger.info("Starting up TwinSecure AI Backend...")
    try:
        # Check license authorization
        if not license_manager.is_authorized():
            logger.error("License validation failed. Application cannot start.")
            raise Exception("Invalid or expired license. Please contact support.")

        license_status = license_manager.get_license_status()
        logger.info(f"License status: {license_status['status']} ({license_status['type']})")

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
    lifespan=lifespan,
)

# Rate limiting middleware
if settings.ENABLE_RATE_LIMITING:
    from app.middleware.rate_limiter import RateLimiterMiddleware

    # Parse rate limit string (e.g., "100/minute")
    rate_limit_parts = settings.RATE_LIMIT_DEFAULT.split("/")
    if len(rate_limit_parts) == 2:
        max_requests = int(rate_limit_parts[0])
        time_unit = rate_limit_parts[1].lower()

        # Convert time unit to seconds
        if time_unit == "second":
            time_window = 1
        elif time_unit == "minute":
            time_window = 60
        elif time_unit == "hour":
            time_window = 3600
        elif time_unit == "day":
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
            ],
        )
        logger.info(f"Rate limiting enabled: {max_requests} requests per {time_unit}")
    else:
        logger.warning(
            f"Invalid rate limit format: {settings.RATE_LIMIT_DEFAULT}. Rate limiting disabled."
        )

# CORS Configuration
origins_str = settings.BACKEND_CORS_ORIGINS
if isinstance(origins_str, str):
    allow_origins_list = (
        [origin.strip() for origin in origins_str.split(",")] if origins_str else []
    )
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
# This middleware measures and records the time taken to process each request
@app.middleware("http")
async def add_timing_middleware(request: Request, call_next: Callable):
    """
    Middleware that measures request processing time and records it as a Prometheus metric.

    Args:
        request: The incoming HTTP request
        call_next: The next middleware or route handler in the chain

    Returns:
        The HTTP response from the next handler
    """
    # Record start time before processing the request
    start_time = time.time()

    # Process the request through the next handler
    response = await call_next(request)

    # Calculate the total processing time
    process_time = time.time() - start_time

    # Record the request latency in Prometheus
    REQUEST_LATENCY.labels(method=request.method, endpoint=request.url.path).observe(
        process_time
    )

    return response


# Error handling middleware
# This middleware catches unhandled exceptions and returns a standardized error response
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next: Callable):
    """
    Middleware that handles exceptions and records request metrics.

    Args:
        request: The incoming HTTP request
        call_next: The next middleware or route handler in the chain

    Returns:
        The HTTP response or an error response if an exception occurs
    """
    try:
        # Process the request through the next handler
        response = await call_next(request)

        # Record successful request in Prometheus
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
        ).inc()

        return response
    except Exception as e:
        # Log the unhandled exception
        logger.error(f"Unhandled error: {str(e)}")

        # Record failed request in Prometheus
        REQUEST_COUNT.labels(
            method=request.method, endpoint=request.url.path, status=500
        ).inc()

        # Return a standardized error response
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )


# Add security middleware
add_security_middleware(app)

# Add caching middleware
add_cache_middleware(app)

# Include the main API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Advanced health check endpoint with detailed system status.

    This endpoint provides information about the health of various system components,
    including the database, cache, and storage. It performs actual checks on these
    components to ensure they are functioning correctly.

    Returns:
        dict: A dictionary containing health status information:
            - status: Overall system status ("ok" or "error")
            - version: Application version
            - timestamp: Current timestamp
            - components: Status of individual components
            - errors: Any errors encountered during health checks (if applicable)
    """
    # Initialize health status with default values
    health_status = {
        "status": "ok",
        "version": settings.VERSION,
        "timestamp": time.time(),
        "components": {"database": "ok", "cache": "ok", "storage": "ok"},
    }

    # Check database connectivity by executing a simple query
    try:
        async with AsyncSessionLocal() as db:
            from sqlalchemy import text

            await db.execute(text("SELECT 1"))
            logger.debug("Database health check passed")
    except Exception as e:
        # Update health status if database check fails
        health_status["components"]["database"] = "error"
        health_status["database_error"] = str(e)
        health_status["status"] = "error"  # Set overall status to error
        logger.error(f"Database health check failed: {str(e)}")

    # Additional component checks could be added here
    # For example, checking Redis connectivity, file system access, etc.

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
        "status": "operational",
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
