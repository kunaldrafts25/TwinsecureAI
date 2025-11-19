"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

Report schemas for API requests and responses.
"""

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ReportBase(BaseModel):
    """Shared properties across all report schemas."""
    
    title: str = Field(..., example="Weekly Security Summary - 2025-W17")
    summary: str | None = Field(
        None,
        example="Increased activity from region X, recommend blocking IPs."
    )
    filename: str = Field(..., example="weekly-summary-2025-04-23.pdf")
    file_location: str = Field(
        ...,
        example="s3://twinsecure-reports/weekly-summary-2025-04-23.pdf"
    )
    generation_params: dict[str, Any] | None = Field(
        None,
        example={"time_range": "last_7_days", "severity": "high"}
    )
    recommendations: str | None = None
    generated_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class ReportCreate(ReportBase):
    """Properties required when creating a report."""
    pass


class ReportUpdate(BaseModel):
    """Properties allowed when updating a report.
    
    Reports are typically immutable once generated, but metadata updates are allowed.
    """
    
    title: str | None = None
    summary: str | None = None
    recommendations: str | None = None


class ReportInDBBase(ReportBase):
    """Properties stored in database."""
    
    id: UUID
    created_at: datetime
    updated_at: datetime | None = None
    
    model_config = ConfigDict(from_attributes=True)


class Report(ReportInDBBase):
    """Properties returned to client."""
    
    download_url: str | None = None  # Constructed in endpoint logic


class ReportQueryFilters(BaseModel):
    """Schema for filtering reports in GET requests."""
    
    start_time: datetime | None = None
    end_time: datetime | None = None
    limit: int = Field(50, ge=1, le=200)
    offset: int = Field(0, ge=0)
    
    @field_validator("end_time")
    @classmethod
    def end_time_must_be_after_start_time(cls, v: datetime | None, info) -> datetime | None:
        if v and info.data.get("start_time") and v < info.data["start_time"]:
            raise ValueError("end_time must be after start_time")
        return v


class ReportGenerationParams(BaseModel):
    """Schema for report generation parameters."""
    
    time_range: str = Field(..., example="last_7_days", description="Time range for the report")
    severity: str | None = Field(None, example="high", description="Filter by severity level")
    report_type: str = Field("summary", example="summary", description="Type of report to generate")
    title: str | None = Field(None, example="Weekly Security Summary", description="Custom report title")
    include_recommendations: bool = Field(True, description="Include security recommendations")