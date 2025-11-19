# app/main.py

"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

Main application module for TwinSecure AI Backend.

This module initializes the FastAPI application, sets up middleware,
configures routes, and handles application lifecycle events.
"""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import Counter, Histogram, generate_latest
from sqlalchemy import text

from app.api.api_v1.api import api_router
from app.core.config import logger, settings
from app.core.license_manager import license_manager
from app.db import init_db
from app.db.session import AsyncSessionLocal, engine
from app.middleware.cache_middleware import add_cache_middleware
from app.middleware.security_middleware import add_security_middleware

# Prometheus metrics for monitoring
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
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
            raise RuntimeError("Invalid or expired license. Please contact support.")
        
        license_status = license_manager.get_license_status()
        logger.info(f"License status: {license_status['status']} ({license_status['type']})")
        
        # Initialize database and create superuser
        async with AsyncSessionLocal() as db:
            await init_db(db)
            logger.info("Database initialization successful")
        
        # Initialize services
        from app.services.alerting.client import alert_client
        from app.services.enrichment.geoip import geoip_reader
        
        # Start ML training scheduler if configured
        if hasattr(settings, "ENABLE_ML_TRAINING") and settings.ENABLE_ML_TRAINING:
            from app.ml.training import start_ml_training_schedule
            start_ml_training_schedule()
            logger.info("ML training scheduler started")
        
        logger.info("Services initialized successfully")
        
        yield
    
    except Exception as e:
        logger.error(f"Startup error: {e}", exc_info=True)
        raise
    
    finally:
        logger.info("Shutting down TwinSecure AI Backend...")
        
        # Clean up services
        try:
            from app.services.enrichment.geoip import close_geoip_reader
            close_geoip_reader()
        except Exception as e:
            logger.error(f"Error closing GeoIP reader: {e}")
        
        # Close database connection
        try:
            await engine.dispose()
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error disposing database engine: {e}")
        
        logger.info("Shutdown complete")


# Create FastAPI app instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION if hasattr(settings, "PROJECT_DESCRIPTION") else "TwinSecure AI Backend",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)


# CORS Configuration
if hasattr(settings, "BACKEND_CORS_ORIGINS"):
    origins_str = settings.BACKEND_CORS_ORIGINS
    
    if isinstance(origins_str, str):
        allow_origins_list = [origin.strip() for origin in origins_str.split(",")] if origins_str else []
    else:
        allow_origins_list = origins_str if origins_str else []
    
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
async def add_timing_middleware(request: Request, call_next):
    """
    Middleware that measures request processing time and records it as a Prometheus metric.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Record latency
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(process_time)
    
    # Add header
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# Error handling middleware
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    """
    Middleware that handles exceptions and records request metrics.
    """
    try:
        response = await call_next(request)
        
        # Record successful request
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
        ).inc()
        
        return response
    
    except Exception as e:
        logger.error(f"Unhandled error: {e}", exc_info=True)
        
        # Record failed request
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=500
        ).inc()
        
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )


# Add security middleware
add_security_middleware(app)

# Add caching middleware
add_cache_middleware(app)

# Rate limiting middleware (optional)
if hasattr(settings, "ENABLE_RATE_LIMITING") and settings.ENABLE_RATE_LIMITING:
    try:
        from app.middleware.rate_limiter import RateLimiterMiddleware
        
        # Parse rate limit string (e.g., "100/minute")
        if hasattr(settings, "RATE_LIMIT_DEFAULT"):
            rate_limit_parts = settings.RATE_LIMIT_DEFAULT.split("/")
            
            if len(rate_limit_parts) == 2:
                max_requests = int(rate_limit_parts[0])
                time_unit = rate_limit_parts[1].lower()
                
                # Convert time unit to seconds
                time_map = {
                    "second": 1,
                    "minute": 60,
                    "hour": 3600,
                    "day": 86400,
                }
                time_window = time_map.get(time_unit, 60)
                
                app.add_middleware(
                    RateLimiterMiddleware,
                    max_requests=max_requests,
                    time_window=time_window,
                    exclude_paths=[
                        r"^/api/v1/docs.*",
                        r"^/api/v1/redoc.*",
                        r"^/api/v1/openapi.json",
                        r"^/api/v1/health",
                        r"^/health",
                        r"^/metrics",
                    ],
                )
                
                logger.info(f"Rate limiting enabled: {max_requests} requests per {time_unit}")
            else:
                logger.warning(f"Invalid rate limit format: {settings.RATE_LIMIT_DEFAULT}")
    
    except Exception as e:
        logger.warning(f"Failed to enable rate limiting: {e}")


# Include the main API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Advanced health check endpoint with detailed system status.
    
    Returns:
        dict: Health status information
    """
    health_status = {
        "status": "ok",
        "version": settings.VERSION,
        "timestamp": time.time(),
        "components": {
            "database": "ok",
            "cache": "ok",
            "storage": "ok"
        },
    }
    
    # Check database connectivity
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
            logger.debug("Database health check passed")
    
    except Exception as e:
        health_status["components"]["database"] = "error"
        health_status["database_error"] = str(e)
        health_status["status"] = "error"
        logger.error(f"Database health check failed: {e}")
    
    return health_status


@app.get("/", tags=["Root"])
async def read_root():
    """
    Root endpoint with system information.
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "documentation": f"{settings.API_V1_STR}/docs",
        "status": "operational",
    }


@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """
    Expose Prometheus metrics for monitoring.
    """
    return Response(generate_latest(), media_type="text/plain")
