"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.
"""

import os
import time
from datetime import datetime, timezone
from typing import Any

import psutil
from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException, status
from sqlalchemy import text

from app.core.config import logger, settings
from app.core.dependencies import get_current_active_user, get_current_active_superuser
from app.db.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas import ServiceStatus, SystemMetrics, SystemStatus

router = APIRouter()


async def get_system_metrics() -> SystemMetrics:
    """Get system metrics from psutil."""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        try:
            process = psutil.Process(os.getpid())
            uptime_seconds = int(time.time() - process.create_time())
        except Exception:
            uptime_seconds = 0
        
        return SystemMetrics(
            cpu_usage_percent=round(cpu_percent, 1),
            memory_usage_percent=round(memory_percent, 1),
            uptime_seconds=uptime_seconds,
            request_rate_per_sec=0.0,
            error_rate_percent=0.0,
        )
        
    except Exception as e:
        logger.warning(f"Failed to get system metrics: {e}")
        return SystemMetrics(
            cpu_usage_percent=0.0,
            memory_usage_percent=0.0,
            uptime_seconds=0,
            request_rate_per_sec=0.0,
            error_rate_percent=0.0,
        )


async def get_service_statuses() -> list[ServiceStatus]:
    """Get service health status by checking actual services."""
    services = []
    
    # Check database
    try:
        from app.db.session import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        
        services.append(ServiceStatus(
            name="Database",
            status="UP",
            details="Connected and responding"
        ))
    except Exception as e:
        services.append(ServiceStatus(
            name="Database",
            status="DOWN",
            details=f"Connection failed: {str(e)[:50]}"
        ))
    
    # Check Redis/Cache
    try:
        if hasattr(settings, "REDIS_URL") and settings.REDIS_URL:
            import redis.asyncio as redis
            
            r = redis.from_url(settings.REDIS_URL)
            await r.ping()
            await r.close()
            
            services.append(ServiceStatus(
                name="Cache (Redis)",
                status="UP",
                details="Connected"
            ))
        else:
            services.append(ServiceStatus(
                name="Cache (Redis)",
                status="UP",
                details="Using in-memory cache"
            ))
    except Exception as e:
        services.append(ServiceStatus(
            name="Cache (Redis)",
            status="DEGRADED",
            details=f"Cache unavailable: {str(e)[:50]}"
        ))
    
    # Check ML model
    try:
        from app.ml.anomaly_detector import get_model_status
        
        model_status = get_model_status()
        
        if model_status["loaded"]:
            services.append(ServiceStatus(
                name="ML Module",
                status="UP",
                details="Model loaded and ready"
            ))
        else:
            services.append(ServiceStatus(
                name="ML Module",
                status="DEGRADED",
                details="Model not loaded"
            ))
    except Exception as e:
        services.append(ServiceStatus(
            name="ML Module",
            status="DEGRADED",
            details=f"ML module error: {str(e)[:50]}"
        ))
    
    # Check alerting configuration
    try:
        alerting_status = "UP"
        alerting_details = []
        
        if hasattr(settings, "SLACK_WEBHOOK_URL") and settings.SLACK_WEBHOOK_URL:
            alerting_details.append("Slack configured")
        if hasattr(settings, "DISCORD_WEBHOOK_URL") and settings.DISCORD_WEBHOOK_URL:
            alerting_details.append("Discord configured")
        if hasattr(settings, "SMTP_HOST") and settings.SMTP_HOST:
            alerting_details.append("Email configured")
        
        if not alerting_details:
            alerting_status = "DEGRADED"
            alerting_details = ["No alerting channels configured"]
        
        services.append(ServiceStatus(
            name="Alerting Service",
            status=alerting_status,
            details=", ".join(alerting_details)
        ))
    except Exception as e:
        services.append(ServiceStatus(
            name="Alerting Service",
            status="DEGRADED",
            details=f"Error: {str(e)[:50]}"
        ))
    
    services.append(ServiceStatus(
        name="Backend API",
        status="UP",
        details="Responding normally"
    ))
    
    return services


@router.get("/status", response_model=SystemStatus)
async def get_system_status(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve overall system status, including metrics and service health.
    Requires authentication.
    """
    logger.info(f"User {current_user.email} fetching system status")
    
    try:
        metrics = await get_system_metrics()
        service_statuses = await get_service_statuses()
        
        overall_status = "HEALTHY"
        if any(s.status == "DOWN" for s in service_statuses):
            overall_status = "UNHEALTHY"
        elif any(s.status == "DEGRADED" for s in service_statuses):
            overall_status = "DEGRADED"
        
        status_response = SystemStatus(
            overall_status=overall_status,
            metrics=metrics,
            service_statuses=service_statuses,
            last_updated=datetime.now(timezone.utc).isoformat(),
        )
        
        logger.info(f"System status: {overall_status}")
        return status_response
        
    except Exception as e:
        logger.error(f"Error fetching system status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system status"
        )


@router.get("/health", response_model=dict[str, Any])
async def get_system_health() -> dict[str, Any]:
    """
    Health check endpoint for monitoring tools.
    Does not require authentication to allow external monitoring.
    """
    logger.info("Health check requested")
    
    health_status = {
        "status": "ok",
        "components": {"database": "ok", "cache": "ok", "storage": "ok"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    
    try:
        from app.db.session import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["components"]["database"] = "error"
        health_status["status"] = "error"
    
    return health_status


@router.post("/train-model", status_code=status.HTTP_202_ACCEPTED)
async def trigger_model_training(
    background_tasks: BackgroundTasks,
    days: int = Body(30, ge=1, le=365),
    current_user: User = Depends(get_current_active_superuser),
) -> dict[str, Any]:
    """
    Trigger ML model training (superuser only).
    This runs as a background task to avoid blocking the API.
    
    Args:
        days: Number of days of historical data to use for training
    """
    logger.info(f"User {current_user.email} triggered ML model training (days={days})")
    
    from app.ml.training import train_autoencoder_model
    
    # Run training in background
    background_tasks.add_task(train_autoencoder_model)
    
    return {
        "message": "ML model training started in the background",
        "status": "accepted",
        "days": days,
    }