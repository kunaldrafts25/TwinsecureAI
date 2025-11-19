"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

Discord alerting channel implementation.
"""

import logging
from datetime import datetime, timezone

import httpx

from app.core.config import settings

from .base import AlertChannel, AlertPayload

logger = logging.getLogger(__name__)


class DiscordChannel(AlertChannel):
    """Alert channel for Discord webhook notifications."""
    
    def initialize(self) -> None:
        """Initialize Discord channel and validate webhook URL."""
        self.webhook_url = self.config.get("webhook_url") or settings.DISCORD_WEBHOOK_URL
        
        if not self.webhook_url:
            logger.warning("Discord webhook URL not configured")
            self.enabled = False
    
    async def send_alert(self, payload: AlertPayload) -> bool:
        """
        Send an alert to Discord via webhook.
        
        Args:
            payload: The alert payload to send
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.debug("Discord channel is disabled, skipping")
            return False
        
        try:
            embed = self._create_embed(payload)
            discord_payload = {
                "username": "TwinSecure Bot",
                "embeds": [embed]
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.webhook_url, json=discord_payload)
                
                if not (200 <= response.status_code < 300):
                    logger.error(
                        f"Discord webhook failed with status {response.status_code}: "
                        f"{response.text}"
                    )
                    return False
            
            return True
        
        except httpx.RequestError as e:
            logger.error(f"Failed to connect to Discord webhook: {e}")
            return False
        
        except Exception as e:
            logger.exception(f"Unexpected error sending Discord alert: {e}")
            return False
    
    def _create_embed(self, payload: AlertPayload) -> dict:
        """
        Create a Discord embed from the alert payload.
        
        Args:
            payload: The alert payload
            
        Returns:
            Discord embed dictionary
        """
        # Get severity color
        color = self._get_severity_color(payload.severity)
        
        embed = {
            "title": payload.title[:256],  # Discord limit: 256 chars
            "description": payload.message[:4096],  # Discord limit: 4096 chars
            "color": color,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "fields": []
        }
        
        # Add severity field
        embed["fields"].append({
            "name": "Severity",
            "value": payload.severity.upper(),
            "inline": True
        })
        
        # Add source IP if available
        if payload.source_ip:
            embed["fields"].append({
                "name": "Source IP",
                "value": payload.source_ip,
                "inline": True
            })
        
        # Add alert type if available
        if payload.alert_type:
            embed["fields"].append({
                "name": "Type",
                "value": payload.alert_type,
                "inline": True
            })
        
        # Add additional data fields
        if payload.additional_data:
            # Alert ID
            if "id" in payload.additional_data:
                embed["fields"].append({
                    "name": "Alert ID",
                    "value": str(payload.additional_data["id"]),
                    "inline": False
                })
            
            # Abuse score
            if "abuse_score" in payload.additional_data:
                score = payload.additional_data["abuse_score"]
                if score is not None:
                    embed["fields"].append({
                        "name": "Abuse Score",
                        "value": f"{score}/100",
                        "inline": True
                    })
            
            # Country from IP info
            if "ip_info" in payload.additional_data:
                ip_info = payload.additional_data["ip_info"]
                if ip_info and "country" in ip_info:
                    embed["fields"].append({
                        "name": "Country",
                        "value": ip_info["country"],
                        "inline": True
                    })
            
            # Status
            if "status" in payload.additional_data:
                embed["fields"].append({
                    "name": "Status",
                    "value": str(payload.additional_data["status"]).upper(),
                    "inline": True
                })
        
        # Discord limit: 25 fields total
        embed["fields"] = embed["fields"][:25]
        
        return embed
    
    def _get_severity_color(self, severity: str) -> int:
        """
        Get Discord color code for severity level.
        
        Args:
            severity: Severity level string
            
        Returns:
            Integer color code for Discord embed
        """
        severity_colors = {
            "critical": 0xFF0000,  # Red
            "high": 0xFF7F00,      # Orange
            "medium": 0xFFFF00,    # Yellow
            "low": 0x00FF00,       # Green
            "info": 0x0000FF,      # Blue
        }
        
        return severity_colors.get(severity.lower(), 0x808080)  # Gray default
