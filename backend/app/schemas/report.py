from pydantic import BaseModel, UUID4, Field, field_validator
from typing import Optional, Dict, Any
from datetime import datetime

# --- Base Schema ---
class ReportBase(BaseModel):
    title: str = Field(..., example="Weekly Security Summary - 2025-W17")
    summary: Optional[str] = Field(None, example="Increased activity from region X, recommend blocking IPs.")
    filename: str = Field(..., example="weekly-summary-2025-04-23.pdf")
    file_location: str = Field(..., example="s3://twinsecure-reports/weekly-summary-2025-04-23.pdf") # Or a download URL
    generation_params: Optional[Dict[str, Any]] = Field(None, example={"time_range": "last_7_days"})
    recommendations: Optional[str] = None
    generated_at: Optional[datetime] = Field(default_factory=datetime.now)

# --- Creation Schema ---
class ReportCreate(ReportBase):
    pass

# --- Update Schema ---
# Reports are typically immutable once generated, but you might allow updating metadata
class ReportUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    recommendations: Optional[str] = None

# --- Database Interaction Schema ---
class ReportInDBBase(ReportBase):
    id: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True # ORM mode

# --- API Response Schema ---
class Report(ReportInDBBase):
    # Add a download URL field if file_location is just a path/key
    download_url: Optional[str] = None # This would be constructed in the endpoint logic

# --- Query Filters Schema ---
class ReportQueryFilters(BaseModel):
    """Schema for filtering reports in GET requests."""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = Field(50, ge=1, le=200)
    offset: int = Field(0, ge=0)

    @field_validator('end_time')
    @classmethod
    def end_time_must_be_after_start_time(cls, v, values):
        if v and values.get('start_time') and v < values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v