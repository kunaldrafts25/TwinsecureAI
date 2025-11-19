"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

System status and metrics schemas.
"""

from pydantic import BaseModel, Field


class ServiceStatus(BaseModel):
    """Status of an individual service."""
    
    name: str = Field(..., example="Backend API")
    status: str = Field(..., example="UP", pattern="^(UP|DOWN|DEGRADED)$")
    details: str | None = Field(None, example="Responding normally")


class SystemMetrics(BaseModel):
    """Key system metrics."""
    
    cpu_usage_percent: float | None = Field(None, ge=0, le=100, example=15.5)
    memory_usage_percent: float | None = Field(None, ge=0, le=100, example=45.2)
    uptime_seconds: int | None = Field(None, ge=0, example=86400)
    request_rate_per_sec: float | None = Field(None, ge=0, example=50.1)
    error_rate_percent: float | None = Field(None, ge=0, le=100, example=0.5)


class SystemStatus(BaseModel):
    """Overall system status response."""
    
    overall_status: str = Field(
        ...,
        example="HEALTHY",
        pattern="^(HEALTHY|DEGRADED|UNHEALTHY)$"
    )
    metrics: SystemMetrics | None = None
    service_statuses: list[ServiceStatus] | None = None
    last_updated: str | None = Field(None, example="2025-04-23T10:00:00Z")
