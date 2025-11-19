"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

Pydantic schemas for request/response validation.
"""

from .alert import (
    Alert,
    AlertCreate,
    AlertQueryFilters,
    AlertSeverity,
    AlertStatus,
    AlertUpdate,
)
from .dashboard import (
    AlertSeverityDistribution,
    AlertTrend,
    Attacker,
    AttackVector,
    ComplianceStatus,
    DashboardResponse,
    DigitalTwinStatus,
    SecurityMetrics,
)
from .digital_twin import (
    DigitalTwin,
    DigitalTwinCreate,
    DigitalTwinUpdate,
    NetworkTopology,
    NetworkTopologyCreate,
    TwinEngagement,
    TwinEngagementCreate,
)
from .honeypot import HoneypotData
from .report import Report, ReportCreate, ReportGenerationParams, ReportQueryFilters, ReportUpdate
from .system import ServiceStatus, SystemMetrics, SystemStatus
from .token import Token, TokenPayload
from .user_schema import User, UserCreate, UserInDBBase, UserUpdate

__all__ = [
    # Alert schemas
    "Alert",
    "AlertCreate",
    "AlertUpdate",
    "AlertQueryFilters",
    "AlertSeverity",
    "AlertStatus",
    # Dashboard schemas
    "AlertSeverityDistribution",
    "AlertTrend",
    "Attacker",
    "AttackVector",
    "ComplianceStatus",
    "DashboardResponse",
    "DigitalTwinStatus",
    "SecurityMetrics",
    # Digital Twin schemas
    "DigitalTwin",
    "DigitalTwinCreate",
    "DigitalTwinUpdate",
    "NetworkTopology",
    "NetworkTopologyCreate",
    "TwinEngagement",
    "TwinEngagementCreate",
    # Honeypot schemas
    "HoneypotData",
    # Report schemas
    "Report",
    "ReportCreate",
    "ReportUpdate",
    "ReportQueryFilters",
    "ReportGenerationParams",
    # System schemas
    "ServiceStatus",
    "SystemMetrics",
    "SystemStatus",
    # Token schemas
    "Token",
    "TokenPayload",
    # User schemas
    "User",
    "UserCreate",
    "UserUpdate",
    "UserInDBBase",
]
