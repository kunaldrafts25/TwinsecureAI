import logging
from datetime import datetime, timezone  # Import datetime and timezone
from typing import Any, Dict, Optional

import httpx

from app.core.config import settings
from app.schemas import Alert  # Import Alert schema for type hinting

logger = logging.getLogger(__name__)


class DiscordAlerter:
    """Class for sending alerts to Discord."""

    def __init__(self, webhook_url: str):
        """
        Initialize the Discord alerter.

        Args:
            webhook_url: Discord webhook URL
        """
        self.webhook_url = webhook_url

    async def send_alert(self, alert_data: Dict[str, Any]) -> bool:
        """
        Send an alert to Discord.

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

            # Create embed
            embed = {
                "title": title[:256],  # Discord has a 256 character limit for titles
                "description": description[
                    :4096
                ],  # Discord has a 4096 character limit for descriptions
                "color": self._get_color_for_severity(severity),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "fields": [],
            }

            # Add severity field
            embed["fields"].append(
                {"name": "Severity", "value": severity, "inline": True}
            )

            # Add alert ID if available
            if "id" in alert_data:
                embed["fields"].append(
                    {"name": "Alert ID", "value": alert_data["id"], "inline": True}
                )

            # Create payload
            payload = {"username": "TwinSecure Bot", "embeds": [embed]}

            # Send message
            async with httpx.AsyncClient() as client:
                response = await client.post(self.webhook_url, json=payload)
                response.raise_for_status()

            return True
        except Exception as e:
            logger.error(f"Failed to send Discord alert: {str(e)}")
            return False

    def _get_color_for_severity(self, severity: str) -> int:
        """
        Get the color code for a severity level.

        Args:
            severity: Severity level

        Returns:
            int: Color code
        """
        severity = severity.upper()
        if severity == "CRITICAL":
            return 0xFF0000  # Red
        elif severity == "HIGH":
            return 0xFF7F00  # Orange
        elif severity == "MEDIUM":
            return 0xFFFF00  # Yellow
        elif severity == "LOW":
            return 0x00FF00  # Green
        else:
            return 0x0000FF  # Blue


async def send_discord_message(
    title: str, details: str, alert_data: Optional[Alert] = None
):
    """
    Sends a formatted message to the configured Discord channel via webhook.

    Args:
        title: The main title for the embed.
        details: The formatted string for the embed description (supports Markdown).
        alert_data: The original Alert object (optional, for adding fields/context).
    """
    if not settings.DISCORD_WEBHOOK_URL:
        logger.debug(
            "Discord webhook URL not configured. Skipping Discord notification."
        )
        return

    # Format message using Discord's embed structure
    # See: https://discord.com/developers/docs/resources/channel#embed-object
    embed = {
        "title": title[:256],  # Embed title limit is 256 chars
        "description": details[:4096],  # Embed description limit is 4096 chars
        "color": 15158332,  # Example color (Red) - Use decimal representation of hex color (e.g., 0xE74C3C -> 15158332)
        "timestamp": datetime.now(timezone.utc).isoformat(),  # Add timestamp
        "fields": [],
    }

    # Optional: Add fields for structured data from alert_data
    if alert_data:
        if alert_data.severity:
            embed["fields"].append(
                {
                    "name": "Severity",
                    "value": alert_data.severity.upper(),
                    "inline": True,
                }
            )
        if alert_data.status:
            embed["fields"].append(
                {"name": "Status", "value": alert_data.status.upper(), "inline": True}
            )
        if alert_data.source_ip:
            embed["fields"].append(
                {
                    "name": "Source IP",
                    "value": str(alert_data.source_ip),
                    "inline": True,
                }
            )
        if alert_data.abuse_score is not None:
            embed["fields"].append(
                {
                    "name": "Abuse Score",
                    "value": f"{alert_data.abuse_score}/100",
                    "inline": True,
                }
            )
        if alert_data.ip_info and alert_data.ip_info.get("country"):
            embed["fields"].append(
                {
                    "name": "Country",
                    "value": alert_data.ip_info["country"],
                    "inline": True,
                }
            )
        # Add more fields as needed, respect embed limits (25 fields total)

    payload = {
        "username": "TwinSecure Bot",
        # "avatar_url": "URL_TO_YOUR_BOT_AVATAR.png", # Optional avatar
        "embeds": [embed],
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(settings.DISCORD_WEBHOOK_URL, json=payload)
            # Discord webhooks usually return 204 No Content on success
            if not (200 <= response.status_code < 300):
                # Error logged by the calling function
                raise httpx.HTTPStatusError(
                    f"Discord webhook failed with status {response.status_code}",
                    request=response.request,
                    response=response,
                )
            # Success logged by the calling function (alert_client)
    except httpx.RequestError as e:
        # Error logged by the calling function
        raise ConnectionError(
            f"Failed to connect to Discord webhook: {e.request.url}"
        ) from e
    except httpx.HTTPStatusError as e:
        # Error logged by the calling function
        raise ConnectionError(
            f"Discord API returned error {e.response.status_code}: {e.response.text}"
        ) from e
    except Exception as e:
        # Error logged by the calling function
        raise RuntimeError(f"Unexpected error sending Discord notification: {e}") from e
