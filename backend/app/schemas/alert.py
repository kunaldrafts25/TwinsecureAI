"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

Alert schemas for API requests and responses.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, IPvAnyAddress, field_validator


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertStatus(str, Enum):
    """Alert status values."""
    
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class AlertBase(BaseModel):
    """Shared properties across all alert schemas."""
    
    alert_type: str = Field(..., example="Honeypot Triggered")
    source_ip: IPvAnyAddress | None = Field(None, example="203.0.113.45")
    ip_info: dict[str, Any] | None = Field(
        None,
        example={"country": "China", "city": "Beijing", "asn": "AS1234"}
    )
    payload: dict[str, Any] | None = Field(
        None,
        example={"headers": {"User-Agent": "..."}, "body": "SELECT *..."}
    )
    raw_log: str | None = None
    abuse_score: int | None = Field(None, ge=0, le=100, example=82)
    severity: AlertSeverity | None = Field(AlertSeverity.MEDIUM, example=AlertSeverity.HIGH)
    status: AlertStatus | None = Field(AlertStatus.NEW, example=AlertStatus.ACKNOWLEDGED)
    notes: str | None = None
    triggered_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        example="2025-04-22T14:35:12Z"
    )


class AlertCreate(AlertBase):
    """Properties required when creating an alert."""
    pass


class AlertUpdate(BaseModel):
    """Properties allowed when updating an alert."""
    
    status: AlertStatus | None = None
    severity: AlertSeverity | None = None
    notes: str | None = None


class AlertInDBBase(AlertBase):
    """Properties stored in database."""
    
    id: UUID
    created_at: datetime
    updated_at: datetime | None = None
    
    model_config = ConfigDict(from_attributes=True)


class Alert(AlertInDBBase):
    """Properties returned to client."""
    pass


class AlertQueryFilters(BaseModel):
    """Schema for filtering alerts in GET requests."""
    
    country: str | None = None
    ip_address: IPvAnyAddress | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    severity: AlertSeverity | None = None
    status: AlertStatus | None = None
    alert_type: str | None = None
    min_abuse_score: int | None = Field(None, ge=0, le=100)
    max_abuse_score: int | None = Field(None, ge=0, le=100)
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)
    
    @field_validator("end_time")
    @classmethod
    def end_time_must_be_after_start_time(cls, v: datetime | None, info) -> datetime | None:
        if v and info.data.get("start_time") and v < info.data["start_time"]:
            raise ValueError("end_time must be after start_time")
        return v
    
    @field_validator("max_abuse_score")
    @classmethod
    def max_score_must_be_gte_min_score(cls, v: int | None, info) -> int | None:
        min_score = info.data.get("min_abuse_score")
        if v is not None and min_score is not None and v < min_score:
            raise ValueError("max_abuse_score must be >= min_abuse_score")
        return v
