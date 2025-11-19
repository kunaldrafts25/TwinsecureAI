"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

Report model for generated security reports and templates.
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, validates

from app.db.base import Base
from app.db.types import ARRAY, JSONB


class ReportType(str, enum.Enum):
    """Report type enumeration"""
    
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_SUMMARY = "weekly_summary"
    MONTHLY_SUMMARY = "monthly_summary"
    QUARTERLY_REVIEW = "quarterly_review"
    ANNUAL_REVIEW = "annual_review"
    INCIDENT_REPORT = "incident_report"
    THREAT_ANALYSIS = "threat_analysis"
    COMPLIANCE_REPORT = "compliance_report"
    CUSTOM = "custom"


class ReportFormat(str, enum.Enum):
    """Report format enumeration"""
    
    PDF = "pdf"
    HTML = "html"
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"
    MARKDOWN = "markdown"


class ReportStatus(str, enum.Enum):
    """Report status enumeration"""
    
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class Report(Base):
    """Database model for generated security reports"""
    
    __tablename__ = "reports"
    
    __table_args__ = (
        Index("ix_reports_type_created_at", "report_type", "created_at"),
        Index("ix_reports_status_created_at", "status", "created_at"),
        Index("ix_reports_creator_created_at", "created_by_id", "created_at"),
    )
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic info
    report_type = Column(Enum(ReportType), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING)
    
    # File information
    filename = Column(String, unique=True, nullable=False)
    file_location = Column(String, nullable=False)
    file_size = Column(Integer, nullable=True)
    file_format = Column(Enum(ReportFormat), default=ReportFormat.PDF)
    file_hash = Column(String, nullable=True)
    
    # Report content
    summary = Column(Text, nullable=True)
    key_findings = Column(JSONB, nullable=True)
    recommendations = Column(JSONB, nullable=True)
    metrics = Column(JSONB, nullable=True)
    visualizations = Column(JSONB, nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    
    # Generation parameters
    generation_params = Column(JSONB, nullable=True)
    time_range = Column(JSONB, nullable=True)
    filters = Column(JSONB, nullable=True)
    included_sections = Column(ARRAY(String), nullable=True)
    
    # Scheduling
    is_scheduled = Column(Boolean, default=False)
    schedule_cron = Column(String, nullable=True)
    next_run = Column(DateTime(timezone=True), nullable=True)
    last_run = Column(DateTime(timezone=True), nullable=True)
    retention_days = Column(Integer, default=90)
    
    # Access control
    is_public = Column(Boolean, default=False)
    allowed_roles = Column(ARRAY(String), nullable=True)
    allowed_users = Column(ARRAY(UUID), nullable=True)
    
    # Relationships
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    creator = relationship("User", back_populates="reports")
    related_alerts = Column(ARRAY(UUID), nullable=True)
    related_reports = Column(ARRAY(UUID), nullable=True)
    
    # Timestamps
    generated_at = Column(DateTime(timezone=True), index=True, nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    archived_at = Column(DateTime(timezone=True), nullable=True)
    
    # Audit
    version = Column(Integer, default=1)
    change_history = Column(JSONB, default=[])
    
    # Validators
    @validates("report_type")
    def validate_report_type(self, key, report_type):
        """Validate report type"""
        if report_type not in ReportType:
            raise ValueError(f"Invalid report type: {report_type}")
        return report_type
    
    @validates("file_format")
    def validate_file_format(self, key, file_format):
        """Validate file format"""
        if file_format not in ReportFormat:
            raise ValueError(f"Invalid file format: {file_format}")
        return file_format
    
    # Hybrid properties
    @hybrid_property
    def is_expired(self) -> bool:
        """Check if report has expired based on retention policy"""
        if not self.generated_at:
            return False
        age = datetime.now(timezone.utc) - self.generated_at
        return age.days > self.retention_days
    
    @hybrid_property
    def needs_regeneration(self) -> bool:
        """Check if scheduled report needs to be regenerated"""
        if not self.is_scheduled:
            return False
        if not self.next_run:
            return True
        return datetime.now(timezone.utc) >= self.next_run
    
    def __repr__(self):
        return f"<Report {self.title} ({self.report_type.value})>"


class ReportTemplate(Base):
    """Model for report templates"""
    
    __tablename__ = "report_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    report_type = Column(Enum(ReportType), nullable=False)
    template_data = Column(JSONB, nullable=False)
    default_params = Column(JSONB, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_by = relationship("User")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ReportTemplate {self.name}>"
