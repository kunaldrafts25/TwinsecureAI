"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

Dashboard data schemas.
"""

from pydantic import BaseModel, Field

from .alert import AlertSeverity, AlertStatus


class AttackVector(BaseModel):
    """Schema for attack vector data."""
    
    name: str
    count: int
    percentage: float | None = None


class Attacker(BaseModel):
    """Schema for attacker data."""
    
    ip: str
    country: str
    count: int
    last_seen: str | None = None


class SecurityMetrics(BaseModel):
    """Schema for security metrics."""
    
    total_alerts: int
    alerts_by_severity: dict[AlertSeverity, int]
    alerts_by_status: dict[AlertStatus, int]
    top_attack_vectors: list[AttackVector]
    top_attackers: list[Attacker]
    risk_score: int = Field(..., ge=0, le=100)


class AlertTrend(BaseModel):
    """Schema for alert trend data."""
    
    date: str
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0


class AlertSeverityDistribution(BaseModel):
    """Schema for alert severity distribution."""
    
    name: AlertSeverity
    value: int
    color: str


class ComplianceItem(BaseModel):
    """Schema for a single compliance item."""
    
    status: str
    compliant: bool
    last_checked: str | None = None


class ComplianceStatus(BaseModel):
    """Schema for compliance status."""
    
    dpdp: ComplianceItem
    gdpr: ComplianceItem
    iso27001: ComplianceItem


class DigitalTwinStatus(BaseModel):
    """Schema for digital twin status."""
    
    active_twins: int
    honeypots: int
    engagements: int
    last_engagement: str | None = None


class DashboardResponse(BaseModel):
    """Schema for the complete dashboard response."""
    
    security_metrics: SecurityMetrics
    alert_trends: list[AlertTrend]
    alert_severity_distribution: list[AlertSeverityDistribution]
    top_attack_vectors: list[AttackVector]
    top_attackers: list[Attacker]
    compliance_status: ComplianceStatus
    digital_twin_status: DigitalTwinStatus
