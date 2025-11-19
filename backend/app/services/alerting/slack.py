"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

Slack alerting channel implementation.
"""

import logging

import httpx

from app.core.config import settings

from .base import AlertChannel, AlertPayload

logger = logging.getLogger(__name__)


class SlackChannel(AlertChannel):
    """Alert channel for Slack webhook notifications."""
    
    def initialize(self) -> None:
        """Initialize Slack channel and validate webhook URL."""
        self.webhook_url = self.config.get("webhook_url") or settings.SLACK_WEBHOOK_URL
        self.channel = self.config.get("channel")  # Optional channel override
        
        if not self.webhook_url:
            logger.warning("Slack webhook URL not configured")
            self.enabled = False
    
    async def send_alert(self, payload: AlertPayload) -> bool:
        """
        Send an alert to Slack via webhook using Block Kit.
        
        Args:
            payload: The alert payload to send
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.debug("Slack channel is disabled, skipping")
            return False
        
        try:
            blocks = self._create_blocks(payload)
            slack_payload = {"blocks": blocks}
            
            # Add channel override if configured
            if self.channel:
                slack_payload["channel"] = self.channel
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.webhook_url, json=slack_payload)
                
                if not (200 <= response.status_code < 300):
                    logger.error(
                        f"Slack webhook failed with status {response.status_code}: "
                        f"{response.text}"
                    )
                    return False
            
            return True
        
        except httpx.RequestError as e:
            logger.error(f"Failed to connect to Slack webhook: {e}")
            return False
        
        except Exception as e:
            logger.exception(f"Unexpected error sending Slack alert: {e}")
            return False
    
    def _create_blocks(self, payload: AlertPayload) -> list[dict]:
        """
        Create Slack Block Kit blocks from the alert payload.
        
        Args:
            payload: The alert payload
            
        Returns:
            List of Slack blocks
        """
        blocks = []
        
        # Header block with severity and title
        severity_prefix = self._get_severity_prefix(payload.severity)
        blocks.append({
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{severity_prefix} {payload.title}"
            }
        })
        
        # Main message section
        message_text = payload.message
        if payload.source_ip:
            message_text += f"\n\n*Source IP:* `{payload.source_ip}`"
        if payload.alert_type:
            message_text += f"\n*Type:* {payload.alert_type}"
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": message_text
            }
        })
        
        # Additional data fields
        if payload.additional_data:
            fields = []
            
            # Abuse score
            if "abuse_score" in payload.additional_data:
                score = payload.additional_data["abuse_score"]
                if score is not None:
                    fields.append({
                        "type": "mrkdwn",
                        "text": f"*Abuse Score:*\n{score}/100"
                    })
            
            # Country
            if "ip_info" in payload.additional_data:
                ip_info = payload.additional_data["ip_info"]
                if ip_info and "country" in ip_info:
                    fields.append({
                        "type": "mrkdwn",
                        "text": f"*Country:*\n{ip_info['country']}"
                    })
            
            # Status
            if "status" in payload.additional_data:
                fields.append({
                    "type": "mrkdwn",
                    "text": f"*Status:*\n{str(payload.additional_data['status']).upper()}"
                })
            
            # Add fields section if any fields exist
            if fields:
                blocks.append({
                    "type": "section",
                    "fields": fields[:10]  # Slack limit: 10 fields
                })
            
            # Context with alert ID and timestamp
            context_elements = []
            
            if "id" in payload.additional_data:
                context_elements.append({
                    "type": "mrkdwn",
                    "text": f"*Alert ID:* {payload.additional_data['id']}"
                })
            
            if "triggered_at" in payload.additional_data:
                context_elements.append({
                    "type": "mrkdwn",
                    "text": f"*Time:* {payload.additional_data['triggered_at']}"
                })
            
            if context_elements:
                blocks.append({
                    "type": "context",
                    "elements": context_elements
                })
        
        return blocks
    
    def _get_severity_prefix(self, severity: str) -> str:
        """
        Get severity prefix for Slack message.
        
        Args:
            severity: Severity level string
            
        Returns:
            Severity indicator with icon
        """
        severity_prefixes = {
            "critical": "[CRITICAL]",
            "high": "[HIGH]",
            "medium": "[MEDIUM]",
            "low": "[LOW]",
            "info": "[INFO]",
        }
        
        return severity_prefixes.get(severity.lower(), "[ALERT]")
