from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import UUID4, BaseModel, Field, IPvAnyAddress, field_validator


# Define enums for alert severity and status
class AlertSeverity(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"
    info = "info"


class AlertStatus(str, Enum):
    new = "new"
    acknowledged = "acknowledged"
    in_progress = "in_progress"
    resolved = "resolved"
    false_positive = "false_positive"


# --- Base Schema ---
class AlertBase(BaseModel):
    alert_type: str = Field(..., example="Honeypot Triggered")
    source_ip: Optional[IPvAnyAddress] = Field(None, example="203.0.113.45")
    ip_info: Optional[Dict[str, Any]] = Field(
        None, example={"country": "China", "city": "Beijing", "asn": "AS1234"}
    )
    payload: Optional[Dict[str, Any]] = Field(
        None, example={"headers": {"User-Agent": "..."}, "body": "SELECT *..."}
    )
    raw_log: Optional[str] = None
    abuse_score: Optional[int] = Field(None, ge=0, le=100, example=82)
    severity: Optional[AlertSeverity] = Field(
        AlertSeverity.medium, example=AlertSeverity.high
    )
    status: Optional[AlertStatus] = Field(
        AlertStatus.new, example=AlertStatus.acknowledged
    )
    notes: Optional[str] = None
    triggered_at: Optional[datetime] = Field(
        default_factory=datetime.now, example="2025-04-22T14:35:12+05:30"
    )


# --- Creation Schema ---
# Properties required when creating an alert (most are in Base)
class AlertCreate(AlertBase):
    pass  # Inherits all fields from AlertBase


# --- Update Schema ---
# Properties allowed when updating an alert (e.g., status, notes)
class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None
    severity: Optional[AlertSeverity] = None
    notes: Optional[str] = None
    # Add other fields that analysts might update


# --- Database Interaction Schema ---
class AlertInDBBase(AlertBase):
    id: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # ORM mode


# --- API Response Schema ---
# Properties returned to the client
class Alert(AlertInDBBase):
    pass  # Inherits all fields from AlertInDBBase


# --- Query Filters Schema ---
class AlertQueryFilters(BaseModel):
    """Schema for filtering alerts in GET requests."""

    country: Optional[str] = None
    ip_address: Optional[IPvAnyAddress] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    severity: Optional[AlertSeverity] = None
    status: Optional[AlertStatus] = None
    alert_type: Optional[str] = None
    min_abuse_score: Optional[int] = Field(None, ge=0, le=100)
    max_abuse_score: Optional[int] = Field(None, ge=0, le=100)
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)

    @field_validator("end_time")
    def end_time_must_be_after_start_time(cls, v, info):
        values = info.data
        if v and values.get("start_time") and v < values["start_time"]:
            raise ValueError("end_time must be after start_time")
        return v

    @field_validator("max_abuse_score")
    def max_score_must_be_gte_min_score(cls, v, info):
        values = info.data
        if (
            v is not None
            and values.get("min_abuse_score") is not None
            and v < values["min_abuse_score"]
        ):
            raise ValueError(
                "max_abuse_score must be greater than or equal to min_abuse_score"
            )
        return v
