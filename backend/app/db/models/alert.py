import uuid
from sqlalchemy import Column, String, Integer, DateTime, JSON, func, Index
from sqlalchemy.dialects.postgresql import UUID, INET # Use INET for IP addresses
from app.db.base import Base

class Alert(Base):
    """
    Database model for security alerts.
    """
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_type = Column(String, index=True, nullable=False) # e.g., "Honeypot Triggered", "Anomaly Detected"
    source_ip = Column(INET, index=True, nullable=True) # Store IP address efficiently
    ip_info = Column(JSON, nullable=True) # Store GeoIP info (country, city, ASN)
    payload = Column(JSON, nullable=True) # Store request details (headers, body, etc.) or anomaly features
    raw_log = Column(String, nullable=True) # Optional raw log entry
    abuse_score = Column(Integer, index=True, nullable=True) # Score from AbuseIPDB or internal system
    severity = Column(String, index=True, default="medium") # e.g., low, medium, high, critical
    status = Column(String, index=True, default="new") # e.g., new, acknowledged, investigating, resolved
    notes = Column(String, nullable=True) # Analyst notes

    triggered_at = Column(DateTime(timezone=True), index=True, nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Add relationships if needed, e.g., user who acknowledged the alert
    # acknowledged_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    # acknowledged_by = relationship("User")

    # Add multi-column index for common filtering/sorting
    __table_args__ = (
        Index('ix_alerts_triggered_at_severity', triggered_at.desc(), severity),
        Index('ix_alerts_source_ip_triggered_at', source_ip, triggered_at.desc()),
    )

    def __repr__(self):
        return f"<Alert(id={self.id}, type='{self.alert_type}', ip='{self.source_ip}', triggered_at='{self.triggered_at}')>"
