from pydantic import BaseModel, Field
from typing import Optional, Dict, List

class ServiceStatus(BaseModel):
    """Status of an individual service."""
    name: str = Field(..., example="Backend API")
    status: str = Field(..., example="UP", pattern="^(UP|DOWN|DEGRADED)$") # Enforce specific values
    details: Optional[str] = Field(None, example="Responding normally")

class SystemMetrics(BaseModel):
    """Key system metrics."""
    cpu_usage_percent: Optional[float] = Field(None, ge=0, le=100, example=15.5)
    memory_usage_percent: Optional[float] = Field(None, ge=0, le=100, example=45.2)
    uptime_seconds: Optional[int] = Field(None, ge=0, example=86400)
    request_rate_per_sec: Optional[float] = Field(None, ge=0, example=50.1)
    error_rate_percent: Optional[float] = Field(None, ge=0, le=100, example=0.5)

class SystemStatus(BaseModel):
    """
    Overall system status response for the /api/system/status endpoint.
    This might fetch data from Prometheus/Grafana or internal monitoring.
    """
    overall_status: str = Field(..., example="HEALTHY", pattern="^(HEALTHY|DEGRADED|UNHEALTHY)$")
    metrics: Optional[SystemMetrics] = None
    service_statuses: Optional[List[ServiceStatus]] = None
    last_updated: Optional[str] = Field(None, example="2025-04-23T10:00:00Z") # ISO 8601 format
