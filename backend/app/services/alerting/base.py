"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

Base alerting service module providing abstract classes for all alert channels.
"""

import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.db.models.alert import Alert

logger = logging.getLogger(__name__)


class AlertChannelType(str, Enum):
    """Supported alert channel types."""
    
    EMAIL = "email"
    DISCORD = "discord"
    SLACK = "slack"
    WEBHOOK = "webhook"


class AlertPayload(BaseModel):
    """Model for alert payload."""
    
    title: str
    message: str
    severity: str
    source_ip: str | None = None
    alert_type: str | None = None
    additional_data: dict[str, Any] | None = None
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_alert(cls, alert: Alert) -> "AlertPayload":
        """Create an AlertPayload from an Alert model."""
        return cls(
            title=alert.alert_type or "Security Alert",
            message=alert.raw_log or f"Alert from {alert.source_ip}",
            severity=alert.severity.value if alert.severity else "medium",
            source_ip=str(alert.source_ip) if alert.source_ip else None,
            alert_type=alert.alert_type,
            additional_data={
                "id": str(alert.id),
                "status": alert.status.value if alert.status else "new",
                "triggered_at": (
                    alert.triggered_at.isoformat() if alert.triggered_at else None
                ),
                "ip_info": alert.ip_info,
                "abuse_score": alert.abuse_score,
            },
        )


class AlertChannel(ABC):
    """Base class for all alert channels."""
    
    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the alert channel with optional configuration."""
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self.initialize()
    
    def initialize(self) -> None:
        """Initialize the channel. Override if needed."""
        pass
    
    @abstractmethod
    async def send_alert(self, payload: AlertPayload) -> bool:
        """
        Send an alert using this channel.
        
        Args:
            payload: The alert payload to send
            
        Returns:
            True if the alert was sent successfully, False otherwise
        """
        pass
    
    async def format_message(self, payload: AlertPayload) -> str:
        """
        Format the alert message with emoji indicators.
        
        Args:
            payload: The alert payload
            
        Returns:
            Formatted message string
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
            message += "\n**Additional Information:**\n"
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


class AlertClient:
    """
    Client for managing multiple alert channels.
    
    Sends alerts through Discord, Email, Slack, etc.
    """
    
    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the alerting client with optional configuration."""
        self.config = config or {}
        self.channels: list[AlertChannel] = []
        self.initialize_channels()
    
    def initialize_channels(self) -> None:
        """Initialize all configured alert channels."""
        # Channels are registered manually via register_channel()
        pass
    
    def register_channel(self, channel: AlertChannel) -> None:
        """
        Register an alert channel with the client.
        
        Args:
            channel: The alert channel to register
        """
        if channel.enabled:
            self.channels.append(channel)
            logger.info(f"Registered alert channel: {channel.__class__.__name__}")
    
    async def send_alert(
        self,
        alert: Alert | AlertPayload,
        channels: list[str] | None = None
    ) -> dict[str, bool]:
        """
        Send an alert through all registered channels or specific ones.
        
        Args:
            alert: The alert to send
            channels: Optional list of channel names to send to
            
        Returns:
            Dictionary of channel names and their success status
        """
        if isinstance(alert, Alert):
            payload = AlertPayload.from_alert(alert)
        else:
            payload = alert
        
        results = {}
        
        for channel in self.channels:
            channel_name = channel.__class__.__name__
            
            # Skip if specific channels are requested and this isn't one
            if channels and channel_name not in channels:
                continue
            
            try:
                success = await channel.send_alert(payload)
                results[channel_name] = success
                
                if success:
                    logger.info(f" Alert sent via {channel_name}")
                else:
                    logger.warning(f" Failed to send alert via {channel_name}")
            
            except Exception as e:
                logger.exception(f" Error sending alert via {channel_name}: {e}")
                results[channel_name] = False
        
        return results
