"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

Alert model for security events and incidents.
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
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

from app.core.enums import AlertSeverity, AlertStatus, AlertType
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
    """Security alert model with enrichment and workflow tracking"""
    
    __tablename__ = "alerts"
    
    __table_args__ = (
        Index("ix_alerts_triggered_at_severity", "triggered_at", "severity"),
        Index("ix_alerts_source_ip_triggered_at", "source_ip", "triggered_at"),
        Index("ix_alerts_status_created_at", "status", "created_at"),
        Index("ix_alerts_type_severity", "alert_type", "severity"),
        Index("ix_alerts_payload_gin", "payload", postgresql_using="gin"),
        Index("ix_alerts_enrichment_gin", "enrichment_data", postgresql_using="gin"),
    )
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Alert classification
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
    ip_info = Column(JSONB, nullable=True)
    threat_intel = Column(JSONB, nullable=True)
    malware_info = Column(JSONB, nullable=True)
    
    # Scoring and risk assessment
    abuse_score = Column(Integer, index=True, nullable=True)
    risk_score = Column(Integer, index=True, nullable=True)
    confidence_score = Column(Float, nullable=True)
    false_positive_probability = Column(Float, nullable=True)
    
    # Tracking and workflow
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    acknowledged_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    related_alerts = Column(ARRAY(UUID), nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    
    # Timestamps
    triggered_at = Column(DateTime(timezone=True), index=True, nullable=True, server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], back_populates="alerts")
    acknowledged_by = relationship("User", foreign_keys=[acknowledged_by_id])
    resolved_by = relationship("User", foreign_keys=[resolved_by_id])
    notes = relationship("AlertNote", back_populates="alert", cascade="all, delete-orphan")
    
    # Validators
    @validates("severity")
    def validate_severity(self, key, severity):
        """Validate severity level"""
        if severity not in AlertSeverity:
            raise ValueError(f"Invalid severity level: {severity}")
        return severity
    
    @validates("status")
    def validate_status(self, key, status):
        """Validate status"""
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
        """Check if alert is stale (unacknowledged for 24 hours)"""
        if self.status == AlertStatus.NEW:
            return self.age > 1440
        return False
    
    @hybrid_property
    def needs_escalation(self) -> bool:
        """Check if alert needs escalation"""
        if self.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
            return self.age > 60
        return False
    
    # Methods
    def acknowledge(self, user_id: UUID) -> None:
        """Acknowledge the alert"""
        self.status = AlertStatus.ACKNOWLEDGED
        self.acknowledged_by_id = user_id
        self.acknowledged_at = datetime.now(timezone.utc)
    
    def resolve(self, user_id: UUID) -> None:
        """Resolve the alert"""
        self.status = AlertStatus.RESOLVED
        self.resolved_by_id = user_id
        self.resolved_at = datetime.now(timezone.utc)
    
    def update_enrichment(self, data: dict) -> None:
        """Update enrichment data"""
        if not self.enrichment_data:
            self.enrichment_data = {}
        self.enrichment_data.update(data)
        self.updated_at = datetime.now(timezone.utc)
    
    def calculate_risk_score(self) -> None:
        """Calculate risk score based on severity and other factors"""
        base_score = {
            AlertSeverity.INFO: 10,
            AlertSeverity.LOW: 30,
            AlertSeverity.MEDIUM: 50,
            AlertSeverity.HIGH: 70,
            AlertSeverity.CRITICAL: 90,
        }.get(self.severity, 50)
        
        if self.abuse_score:
            base_score += (self.abuse_score / 100) * 20
        
        if self.confidence_score:
            base_score *= self.confidence_score / 100
        
        self.risk_score = min(100, max(0, int(base_score)))
    
    def __repr__(self):
        return f"<Alert {self.id} {self.severity.value} {self.status.value}>"


class AlertNote(Base):
    """Model for alert notes and comments"""
    
    __tablename__ = "alert_notes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_id = Column(UUID(as_uuid=True), ForeignKey("alerts.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    content = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    alert = relationship("Alert", back_populates="notes")
    user = relationship("User")
    
    def __repr__(self):
        return f"<AlertNote {self.id} on Alert {self.alert_id}>"
