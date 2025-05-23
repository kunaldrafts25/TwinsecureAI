"""
TwinSecure - Advanced Cybersecurity Platform
Copyright © 2024 TwinSecure. All rights reserved.

This file is part of TwinSecure, a proprietary cybersecurity platform.
Unauthorized copying, distribution, modification, or use of this software
is strictly prohibited without explicit written permission.

For licensing inquiries: kunalsingh2514@gmail.com
"""

"""
Base alerting service module.
This module provides the base class for all alerting services.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from app.core.config import settings
from app.db.models.alert import Alert

logger = logging.getLogger(__name__)


class AlertPayload(BaseModel):
    """Model for alert payload."""

    title: str
    message: str
    severity: str
    source_ip: Optional[str] = None
    alert_type: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None

    @classmethod
    def from_alert(cls, alert: Alert) -> "AlertPayload":
        """Create an AlertPayload from an Alert model."""
        return cls(
            title=alert.title or "Security Alert",
            message=alert.description or f"Alert from {alert.source_ip}",
            severity=alert.severity.value if alert.severity else "medium",
            source_ip=str(alert.source_ip) if alert.source_ip else None,
            alert_type=alert.alert_type.value if alert.alert_type else None,
            additional_data={
                "id": str(alert.id),
                "status": alert.status.value if alert.status else "new",
                "triggered_at": (
                    alert.triggered_at.isoformat() if alert.triggered_at else None
                ),
                "ip_info": alert.ip_info,
                "threat_intel": alert.threat_intel,
                "abuse_score": alert.abuse_score,
                "risk_score": alert.risk_score,
            },
        )


class BaseAlerter(ABC):
    """Base class for all alerting services."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the alerter with optional configuration."""
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self.initialize()

    def initialize(self) -> None:
        """Initialize the alerter. Override this method if needed."""
        pass

    @abstractmethod
    async def send_alert(self, payload: AlertPayload) -> bool:
        """
        Send an alert using this alerter.

        Args:
            payload: The alert payload to send

        Returns:
            bool: True if the alert was sent successfully, False otherwise
        """
        pass

    async def format_message(self, payload: AlertPayload) -> str:
        """
        Format the alert message.

        Args:
            payload: The alert payload

        Returns:
            str: The formatted message
        """
        severity_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢",
            "info": "🔵",
        }.get(payload.severity.lower(), "⚪")

        message = f"{severity_emoji} **{payload.title}**\n\n"
        message += f"{payload.message}\n\n"

        if payload.source_ip:
            message += f"Source IP: `{payload.source_ip}`\n"

        if payload.alert_type:
            message += f"Type: {payload.alert_type}\n"

        if payload.additional_data:
            message += "\nAdditional Information:\n"
            for key, value in payload.additional_data.items():
                if value is not None and key not in ["id"]:
                    if isinstance(value, dict):
                        message += f"- {key.replace('_', ' ').title()}:\n"
                        for k, v in value.items():
                            if v is not None:
                                message += f"  - {k}: {v}\n"
                    else:
                        message += f"- {key.replace('_', ' ').title()}: {value}\n"

        message += f"\nAlert ID: {payload.additional_data.get('id', 'N/A')}"
        message += f"\nTimestamp: {payload.additional_data.get('triggered_at', 'N/A')}"

        return message


class AlertingClient:
    """
    Client for managing multiple alerting services.
    This class is responsible for sending alerts through multiple channels.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the alerting client with optional configuration."""
        self.config = config or {}
        self.alerters: List[BaseAlerter] = []
        self.initialize_alerters()

    def initialize_alerters(self) -> None:
        """Initialize all configured alerters."""
        # This will be populated with actual alerters in the implementation
        pass

    def register_alerter(self, alerter: BaseAlerter) -> None:
        """
        Register an alerter with the client.

        Args:
            alerter: The alerter to register
        """
        if alerter.enabled:
            self.alerters.append(alerter)
            logger.info(f"Registered alerter: {alerter.__class__.__name__}")

    async def send_alert(
        self, alert: Union[Alert, AlertPayload], channels: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        Send an alert through all registered alerters or specific channels.

        Args:
            alert: The alert to send
            channels: Optional list of channel names to send to

        Returns:
            Dict[str, bool]: Dictionary of alerter names and their success status
        """
        if isinstance(alert, Alert):
            payload = AlertPayload.from_alert(alert)
        else:
            payload = alert

        results = {}

        for alerter in self.alerters:
            alerter_name = alerter.__class__.__name__

            # Skip if channels are specified and this alerter is not in the list
            if channels and alerter_name not in channels:
                continue

            try:
                success = await alerter.send_alert(payload)
                results[alerter_name] = success
                if success:
                    logger.info(f"Successfully sent alert via {alerter_name}")
                else:
                    logger.warning(f"Failed to send alert via {alerter_name}")
            except Exception as e:
                logger.exception(f"Error sending alert via {alerter_name}: {str(e)}")
                results[alerter_name] = False

        return results
