import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, DateTime, JSON, func, ForeignKey, Enum, Boolean, Text, Integer, Index
from sqlalchemy.dialects.postgresql import UUID
from app.db.types import JSONB, ARRAY
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property
import enum
from app.db.base import Base

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
    """
    Enhanced database model for generated reports with advanced features.
    """
    __tablename__ = "reports"
    __table_args__ = (
        # Add indexes for common queries
        Index('ix_reports_type_created_at', 'report_type', 'created_at'),
        Index('ix_reports_status_created_at', 'status', 'created_at'),
        Index('ix_reports_creator_created_at', 'creator_id', 'created_at'),
    )

    # Primary key and basic info
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_type = Column(Enum(ReportType), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING)

    # File information
    filename = Column(String, unique=True, nullable=False)
    file_location = Column(String, nullable=False)
    file_size = Column(Integer, nullable=True)  # Size in bytes
    file_format = Column(Enum(ReportFormat), default=ReportFormat.PDF)
    file_hash = Column(String, nullable=True)  # For integrity verification

    # Report content and metadata
    summary = Column(Text, nullable=True)
    key_findings = Column(JSONB, nullable=True)
    recommendations = Column(JSONB, nullable=True)
    metrics = Column(JSONB, nullable=True)  # Key metrics and statistics
    visualizations = Column(JSONB, nullable=True)  # Chart configurations
    tags = Column(ARRAY(String), nullable=True)

    # Generation parameters
    generation_params = Column(JSONB, nullable=True)
    time_range = Column(JSONB, nullable=True)  # Start and end times
    filters = Column(JSONB, nullable=True)  # Applied filters
    included_sections = Column(ARRAY(String), nullable=True)

    # Scheduling and automation
    is_scheduled = Column(Boolean, default=False)
    schedule_cron = Column(String, nullable=True)  # Cron expression
    next_run = Column(DateTime(timezone=True), nullable=True)
    last_run = Column(DateTime(timezone=True), nullable=True)
    retention_days = Column(Integer, default=90)  # Days to keep the report

    # Access control
    is_public = Column(Boolean, default=False)
    allowed_roles = Column(ARRAY(String), nullable=True)
    allowed_users = Column(ARRAY(UUID), nullable=True)

    # Relationships
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    creator = relationship("User", back_populates="reports")
    related_alerts = Column(ARRAY(UUID), nullable=True)  # Related alert IDs
    related_reports = Column(ARRAY(UUID), nullable=True)  # Related report IDs

    # Timestamps
    generated_at = Column(DateTime(timezone=True), index=True, nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    archived_at = Column(DateTime(timezone=True), nullable=True)

    # Audit fields
    version = Column(Integer, default=1)
    change_history = Column(JSONB, default=[])

    # Validators
    @validates('report_type')
    def validate_report_type(self, key, report_type):
        """Validate report type"""
        if report_type not in ReportType:
            raise ValueError(f"Invalid report type: {report_type}")
        return report_type

    @validates('file_format')
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
        """Check if report needs to be regenerated"""
        if not self.is_scheduled:
            return False
        if not self.next_run:
            return True
        return datetime.now(timezone.utc) >= self.next_run

    # Methods
    def update_status(self, status: ReportStatus, error: Optional[str] = None) -> None:
        """Update report status"""
        self.status = status
        if error:
            self.add_to_change_history({
                'status': status.value,
                'error': error
            })
        else:
            self.add_to_change_history({
                'status': status.value
            })

    def archive(self) -> None:
        """Archive the report"""
        self.status = ReportStatus.ARCHIVED
        self.archived_at = datetime.now(timezone.utc)
        self.add_to_change_history({
            'action': 'archive',
            'archived_at': self.archived_at.isoformat()
        })

    def add_to_change_history(self, change: Dict[str, Any]) -> None:
        """Add entry to change history"""
        if not self.change_history:
            self.change_history = []
        change['timestamp'] = datetime.now(timezone.utc).isoformat()
        self.change_history.append(change)
        self.version += 1

    def schedule_generation(self, cron_expression: str) -> None:
        """Schedule report generation"""
        self.is_scheduled = True
        self.schedule_cron = cron_expression
        self.add_to_change_history({
            'action': 'schedule',
            'cron_expression': cron_expression
        })

    def cancel_schedule(self) -> None:
        """Cancel scheduled generation"""
        self.is_scheduled = False
        self.schedule_cron = None
        self.next_run = None
        self.add_to_change_history({
            'action': 'cancel_schedule'
        })

    def update_access_control(self, is_public: bool, allowed_roles: List[str] = None, allowed_users: List[UUID] = None) -> None:
        """Update report access control settings"""
        self.is_public = is_public
        self.allowed_roles = allowed_roles
        self.allowed_users = allowed_users
        self.add_to_change_history({
            'action': 'update_access_control',
            'is_public': is_public,
            'allowed_roles': allowed_roles,
            'allowed_users': [str(uuid) for uuid in allowed_users] if allowed_users else None
        })

    def to_dict(self) -> dict:
        """Convert report to dictionary"""
        return {
            'id': str(self.id),
            'report_type': self.report_type.value,
            'title': self.title,
            'status': self.status.value,
            'file_format': self.file_format.value,
            'created_at': self.created_at.isoformat(),
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'creator_id': str(self.creator_id),
            'is_scheduled': self.is_scheduled,
            'is_public': self.is_public,
            'version': self.version,
            'file_size': self.file_size,
            'tags': self.tags,
            'retention_days': self.retention_days,
            'is_expired': self.is_expired,
            'needs_regeneration': self.needs_regeneration
        }

    def __repr__(self):
        return f"<Report(id={self.id}, type='{self.report_type.value}', status='{self.status.value}')>"

class ReportTemplate(Base):
    """
    Model for report templates.
    """
    __tablename__ = "report_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    report_type = Column(Enum(ReportType), nullable=False)
    template_data = Column(JSONB, nullable=False)  # Template configuration
    default_params = Column(JSONB, nullable=True)  # Default generation parameters
    is_active = Column(Boolean, default=True)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    created_by = relationship("User")

    def __repr__(self):
        return f"<ReportTemplate(id={self.id}, name='{self.name}', type='{self.report_type.value}')>"