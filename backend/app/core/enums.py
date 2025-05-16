"""
Central location for all enum definitions used throughout the application.
This helps prevent circular imports.
"""

import enum


class UserRole(str, enum.Enum):
    """User role enumeration"""

    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"
    API_USER = "api_user"


class UserStatus(str, enum.Enum):
    """User status enumeration"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class AlertType(str, enum.Enum):
    """Alert type enumeration"""

    HONEYPOT_TRIGGER = "honeypot_trigger"
    BRUTE_FORCE = "brute_force"
    SUSPICIOUS_LOGIN = "suspicious_login"
    MALWARE_DETECTED = "malware_detected"
    DATA_EXFILTRATION = "data_exfiltration"
    POLICY_VIOLATION = "policy_violation"
    SYSTEM_ERROR = "system_error"
    CUSTOM = "custom"


class AlertSeverity(str, enum.Enum):
    """Alert severity enumeration"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertStatus(str, enum.Enum):
    """Alert status enumeration"""

    NEW = "new"
    ASSIGNED = "assigned"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    FALSE_POSITIVE = "false_positive"


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
