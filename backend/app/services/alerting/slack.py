"""
TwinSecure - Advanced Cybersecurity Platform
Copyright © 2024 TwinSecure. All rights reserved.

This file is part of TwinSecure, a proprietary cybersecurity platform.
Unauthorized copying, distribution, modification, or use of this software
is strictly prohibited without explicit written permission.

For licensing inquiries: kunalsingh2514@gmail.com
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import httpx
import requests

from app.core.config import settings

logger = logging.getLogger(__name__)


class SlackAlerter:
    """Class for sending alerts to Slack."""

    def __init__(self, webhook_url: str, channel: Optional[str] = None):
        """
        Initialize the Slack alerter.

        Args:
            webhook_url: Slack webhook URL
            channel: Optional Slack channel to send messages to
        """
        self.webhook_url = webhook_url
        self.channel = channel

    async def send_alert(self, alert_data: Dict[str, Any]) -> bool:
        """
        Send an alert to Slack.

        Args:
            alert_data: Dictionary containing alert information

        Returns:
            bool: True if the alert was sent successfully, False otherwise
        """
        try:
            # Extract alert information
            title = alert_data.get("title", "Security Alert")
            severity = alert_data.get("severity", "MEDIUM")
            description = alert_data.get("description", "")

            # Create message blocks
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{severity} Alert: {title}",
                        "emoji": True,
                    },
                },
                {"type": "section", "text": {"type": "mrkdwn", "text": description}},
            ]

            # Add alert ID if available
            if "id" in alert_data:
                blocks.append(
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Alert ID:* {alert_data['id']}",
                            }
                        ],
                    }
                )

            # Create payload
            payload = {"blocks": blocks}

            # Add channel if specified
            if self.channel:
                payload["channel"] = self.channel

            # Send message
            async with httpx.AsyncClient() as client:
                response = await client.post(self.webhook_url, json=payload)
                response.raise_for_status()

            return True
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {str(e)}")
            return False


def send_slack_message(message: str, webhook_url: str) -> Optional[requests.Response]:
    """
    Sends a message to a Slack channel using an incoming webhook.

    Args:
        message: The text content of the message to send.
        webhook_url: The Slack incoming webhook URL.

    Returns:
        The requests.Response object if the request was successful,
        None otherwise.
    """
    # Prepare the payload for the Slack message
    payload = {"text": message}

    try:
        # Send the HTTP POST request to the Slack webhook URL
        response = requests.post(webhook_url, json=payload)

        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        logger.info(
            f"Slack message sent successfully. Status code: {response.status_code}"
        )
        return response

    except requests.exceptions.RequestException as e:
        # Handle any errors that occur during the request
        logger.error(f"Failed to send Slack message: {e}")
        return None
    except Exception as e:
        # Catch any other unexpected errors
        logger.error(f"An unexpected error occurred while sending Slack message: {e}")
        return None
