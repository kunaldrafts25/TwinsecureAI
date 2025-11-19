"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

Service layer for alerting, enrichment, and security utilities.
"""

# Alerting services
from .alerting import (
    AlertChannel,
    AlertChannelType,
    AlertClient,
    AlertPayload,
    DiscordChannel,
    EmailChannel,
    SlackChannel,
    alert_client,
    create_alert_client,
)

# Enrichment services
from .enrichment import (
    AbuseIPDBClient,
    GeoIPClient,
    check_ip_reputation,
    get_ip_location,
)

# Utility services (top level)
from .attack_detection import AttackDetector, detect_attack_patterns
from .attack_response import AttackResponder, respond_to_attack
from .pdf_generator import PDFReportGenerator, generate_pdf_report
from .rate_limiter import RateLimiter
from .validation import validate_alert_payload, validate_ip_address

__all__ = [
    # Alerting
    "AlertChannel",
    "AlertChannelType",
    "AlertClient",
    "AlertPayload",
    "DiscordChannel",
    "EmailChannel",
    "SlackChannel",
    "alert_client",
    "create_alert_client",
    # Enrichment
    "AbuseIPDBClient",
    "GeoIPClient",
    "check_ip_reputation",
    "get_ip_location",
    # Utilities
    "AttackDetector",
    "detect_attack_patterns",
    "AttackResponder",
    "respond_to_attack",
    "PDFReportGenerator",
    "generate_pdf_report",
    "RateLimiter",
    "validate_alert_payload",
    "validate_ip_address",
]
