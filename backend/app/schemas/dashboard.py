from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

from .alert import AlertSeverity, AlertStatus

class AttackVector(BaseModel):
    """Schema for attack vector data."""
    name: str
    count: int
    percentage: Optional[float] = None

class Attacker(BaseModel):
    """Schema for attacker data."""
    ip: str
    country: str
    count: int
    last_seen: Optional[str] = None

class SecurityMetrics(BaseModel):
    """Schema for security metrics."""
    total_alerts: int
    alerts_by_severity: Dict[AlertSeverity, int]
    alerts_by_status: Dict[AlertStatus, int]
    top_attack_vectors: List[AttackVector]
    top_attackers: List[Attacker]
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
    last_checked: Optional[str] = None

class ComplianceStatus(BaseModel):
    """Schema for compliance status."""
    dpdp: ComplianceItem
    gdpr: ComplianceItem
    iso27001: ComplianceItem

class DigitalTwinStatus(BaseModel):
    """Schema for digital twin status."""
    activeTwins: int
    honeypots: int
    engagements: int
    last_engagement: Optional[str] = None

class DashboardResponse(BaseModel):
    """Schema for the complete dashboard response."""
    securityMetrics: SecurityMetrics
    alertTrends: List[AlertTrend]
    alertSeverityDistribution: List[AlertSeverityDistribution]
    topAttackVectors: List[AttackVector]
    topAttackers: List[Attacker]
    complianceStatus: ComplianceStatus
    digitalTwinStatus: DigitalTwinStatus
