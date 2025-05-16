import enum
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, validates

from app.core.enums import AlertSeverity, AlertStatus, AlertType, UserRole
from app.db.base import Base
from app.db.types import ARRAY, INET, JSONB


class AlertSource(str, enum.Enum):
    """Alert source enumeration"""

    HONEYPOT = "honeypot"
    IDS = "ids"
    WAF = "waf"
    SIEM = "siem"
    ML_MODEL = "ml_model"
    MANUAL = "manual"
    EXTERNAL = "external"


class Alert(Base):
    """
    Enhanced database model for security alerts with advanced features.
    """

    __tablename__ = "alerts"
    __table_args__ = (
        # Add indexes for common queries
        Index("ix_alerts_triggered_at_severity", "triggered_at", "severity"),
        Index("ix_alerts_source_ip_triggered_at", "source_ip", "triggered_at"),
        Index("ix_alerts_status_created_at", "status", "created_at"),
        Index("ix_alerts_type_severity", "alert_type", "severity"),
        # Add GIN index for JSON fields
        Index("ix_alerts_payload_gin", "payload", postgresql_using="gin"),
        Index("ix_alerts_enrichment_gin", "enrichment_data", postgresql_using="gin"),
    )

    # Primary key and basic info
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_type = Column(Enum(AlertType), index=True, nullable=False)
    source = Column(Enum(AlertSource), nullable=True, default=AlertSource.MANUAL)
    severity = Column(Enum(AlertSeverity), index=True, default=AlertSeverity.MEDIUM)
    status = Column(Enum(AlertStatus), index=True, default=AlertStatus.NEW)

    # Source information
    source_ip = Column(INET, index=True, nullable=True)
    source_hostname = Column(String, nullable=True)
    source_mac = Column(String, nullable=True)
    source_ports = Column(ARRAY(Integer), nullable=True)
    source_protocol = Column(String, nullable=True)

    # Target information
    target_ip = Column(INET, index=True, nullable=True)
    target_hostname = Column(String, nullable=True)
    target_port = Column(Integer, nullable=True)
    target_protocol = Column(String, nullable=True)
    target_service = Column(String, nullable=True)

    # Alert details
    title = Column(String, nullable=True, default="Untitled Alert")
    description = Column(Text, nullable=True)
    payload = Column(JSONB, nullable=True)
    raw_log = Column(Text, nullable=True)

    # Enrichment data
    enrichment_data = Column(JSONB, default={})
    ip_info = Column(JSONB, nullable=True)  # GeoIP info
    threat_intel = Column(JSONB, nullable=True)  # Threat intelligence data
    malware_info = Column(JSONB, nullable=True)  # Malware analysis results

    # Scoring and risk assessment
    abuse_score = Column(Integer, index=True, nullable=True)
    risk_score = Column(Integer, index=True, nullable=True)
    confidence_score = Column(Float, nullable=True)
    false_positive_probability = Column(Float, nullable=True)

    # Tracking and workflow
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    acknowledged_by_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    resolved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    related_alerts = Column(ARRAY(UUID), nullable=True)
    tags = Column(ARRAY(String), nullable=True)

    # Timestamps
    triggered_at = Column(
        DateTime(timezone=True), index=True, nullable=True, server_default=func.now()
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    last_updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    assigned_to = relationship(
        "User",
        foreign_keys=[assigned_to_id],
        backref="assigned_alerts",
        overlaps="alerts",
    )
    acknowledged_by = relationship(
        "User", foreign_keys=[acknowledged_by_id], backref="acknowledged_alerts"
    )
    resolved_by = relationship(
        "User", foreign_keys=[resolved_by_id], backref="resolved_alerts"
    )
    notes = relationship(
        "AlertNote", back_populates="alert", cascade="all, delete-orphan"
    )

    # Validators
    @validates("severity")
    def validate_severity(self, key, severity):
        """Validate severity level"""
        if severity not in AlertSeverity:
            raise ValueError(f"Invalid severity level: {severity}")
        return severity

    @validates("status")
    def validate_status(self, key, status):
        """Validate status transitions"""
        if status not in AlertStatus:
            raise ValueError(f"Invalid status: {status}")
        return status

    # Hybrid properties
    @hybrid_property
    def age(self) -> int:
        """Calculate alert age in minutes"""
        return (datetime.now(timezone.utc) - self.triggered_at).total_seconds() / 60

    @hybrid_property
    def is_stale(self) -> bool:
        """Check if alert is stale (unacknowledged for too long)"""
        if self.status == AlertStatus.NEW:
            return self.age > 1440  # 24 hours
        return False

    @hybrid_property
    def needs_escalation(self) -> bool:
        """Check if alert needs escalation"""
        if self.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
            return self.age > 60  # 1 hour for high/critical
        return False

    # Methods
    def acknowledge(self, user_id: UUID) -> None:
        """Acknowledge the alert"""
        self.status = AlertStatus.ACKNOWLEDGED
        self.acknowledged_by_id = user_id
        self.acknowledged_at = datetime.now(timezone.utc)
        self.add_note(user_id, "Alert acknowledged")

    def resolve(self, user_id: UUID, resolution: str) -> None:
        """Resolve the alert"""
        self.status = AlertStatus.RESOLVED
        self.resolved_by_id = user_id
        self.resolved_at = datetime.now(timezone.utc)
        self.notes.append(
            AlertNote(user_id=user_id, content=f"Alert resolved: {resolution}")
        )

    def escalate(self, user_id: UUID, reason: str) -> None:
        """Escalate the alert"""
        self.status = AlertStatus.ESCALATED
        self.add_note(user_id, f"Alert escalated: {reason}")

    def mark_false_positive(self, user_id: UUID, reason: str) -> None:
        """Mark alert as false positive"""
        self.status = AlertStatus.FALSE_POSITIVE
        self.add_note(user_id, f"Marked as false positive: {reason}")

    def add_note(self, user_id: UUID, content: str) -> None:
        """Add a note to the alert"""
        self.notes.append(AlertNote(user_id=user_id, content=content))

    def update_enrichment(self, data: Dict[str, Any]) -> None:
        """Update enrichment data"""
        if not self.enrichment_data:
            self.enrichment_data = {}
        self.enrichment_data.update(data)
        self.updated_at = datetime.now(timezone.utc)

    def calculate_risk_score(self) -> None:
        """Calculate risk score based on various factors"""
        base_score = {
            AlertSeverity.INFO: 10,
            AlertSeverity.LOW: 30,
            AlertSeverity.MEDIUM: 50,
            AlertSeverity.HIGH: 70,
            AlertSeverity.CRITICAL: 90,
        }.get(self.severity, 50)

        # Adjust score based on enrichment data
        if self.abuse_score:
            base_score += (self.abuse_score / 100) * 20

        if self.confidence_score:
            base_score *= self.confidence_score / 100

        self.risk_score = min(100, max(0, int(base_score)))

    def to_dict(self) -> dict:
        """Convert alert to dictionary"""
        return {
            "id": str(self.id),
            "alert_type": self.alert_type.value,
            "source": self.source.value,
            "severity": self.severity.value,
            "status": self.status.value,
            "title": self.title,
            "description": self.description,
            "source_ip": str(self.source_ip) if self.source_ip else None,
            "target_ip": str(self.target_ip) if self.target_ip else None,
            "triggered_at": self.triggered_at.isoformat(),
            "age": self.age,
            "risk_score": self.risk_score,
            "confidence_score": self.confidence_score,
            "assigned_to": str(self.assigned_to_id) if self.assigned_to_id else None,
            "tags": self.tags,
            "enrichment_data": self.enrichment_data,
        }

    def __repr__(self):
        return f"<Alert(id={self.id}, type='{self.alert_type.value}', severity='{self.severity.value}')>"


class AlertNote(Base):
    """
    Model for alert notes and comments.
    """

    __tablename__ = "alert_notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_id = Column(UUID(as_uuid=True), ForeignKey("alerts.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    user_role = Column(Enum(UserRole), nullable=True)
    content = Column(Text, nullable=False)
    is_internal = Column(
        Boolean, default=False
    )  # Internal notes not visible to external users
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Define foreign key constraint
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id", "user_role"],
            ["users.id", "users.role"],
        ),
    )

    # Relationships
    alert = relationship("Alert", back_populates="notes")
    user = relationship("User")

    def __repr__(self):
        return f"<AlertNote(id={self.id}, alert_id={self.alert_id}, user_id={self.user_id})>"
