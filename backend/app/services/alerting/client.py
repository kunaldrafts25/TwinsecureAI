from app.core.config import settings, logger
from app.schemas import Alert # Use the Alert schema for type hinting
import asyncio # For running multiple alerts concurrently
from app.db.models import Report # Import Report model if needed for type hinting report_data
from ..rate_limiter import RateLimiter
from ..validation import validate_alert_payload
import backoff
from datetime import datetime
from typing import Dict, Any, Optional, List, Union

# Import alerters
from .email import EmailAlerter, send_email_alert
from .slack import SlackAlerter, send_slack_message
from .discord import DiscordAlerter, send_discord_message

class AlertingClient:
    """
    Client to orchestrate sending alerts via multiple channels.
    """

    def __init__(self, email_config: Optional[Dict[str, Any]] = None,
                 slack_config: Optional[Dict[str, Any]] = None,
                 discord_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the alerting client with configurations for different alerters.

        Args:
            email_config: Configuration for email alerter
            slack_config: Configuration for Slack alerter
            discord_config: Configuration for Discord alerter
        """
        self.rate_limiter = RateLimiter(max_requests=100, time_window=60)  # 100 requests per minute

        # Initialize alerters
        self.email_alerter = None
        self.slack_alerter = None
        self.discord_alerter = None

        # Set up email alerter if enabled
        if email_config and email_config.get("enabled", True):
            self.email_alerter = EmailAlerter(
                smtp_server=email_config.get("smtp_server", settings.SMTP_HOST),
                smtp_port=email_config.get("smtp_port", settings.SMTP_PORT),
                username=email_config.get("username", settings.SMTP_USER),
                password=email_config.get("password", settings.SMTP_PASSWORD),
                from_email=email_config.get("from_email", settings.EMAILS_FROM_EMAIL),
                to_emails=email_config.get("to_emails", settings.ALERT_RECIPIENTS)
            )

        # Set up Slack alerter if enabled
        if slack_config and slack_config.get("enabled", True):
            self.slack_alerter = SlackAlerter(
                webhook_url=slack_config.get("webhook_url", settings.SLACK_WEBHOOK_URL),
                channel=slack_config.get("channel", settings.SLACK_CHANNEL)
            )

        # Set up Discord alerter if enabled
        if discord_config and discord_config.get("enabled", True):
            self.discord_alerter = DiscordAlerter(
                webhook_url=discord_config.get("webhook_url", settings.DISCORD_WEBHOOK_URL)
            )

        # Legacy channels dict for backward compatibility
        self.channels = {
            'slack': send_slack_message,
            'email': send_email_alert,
            'discord': send_discord_message
        }

        self.retry_config = {
            'max_tries': 3,
            'max_time': 30,
            'jitter': True
        }

    @backoff.on_exception(
        backoff.expo,
        (ConnectionError, TimeoutError),
        max_tries=3,
        max_time=30
    )
    async def _send_with_retry(self, channel: str, **kwargs) -> bool:
        try:
            await self.channels[channel](**kwargs)
            return True
        except Exception as e:
            logger.error(f"Failed to send alert to {channel}: {str(e)}")
            raise

    async def send_alert(
        self,
        alert_data: Dict[str, Any],
        channels: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        Send an alert through configured alerters.

        Args:
            alert_data: Dictionary containing alert information
            channels: Optional list of specific channels to use

        Returns:
            Dict mapping channel names to success status
        """
        results = {}

        # Check if email alerter is configured and should be used
        if self.email_alerter and (not channels or "email" in channels):
            try:
                success = await self.email_alerter.send_alert(alert_data)
                results["email"] = success
            except Exception as e:
                logger.error(f"Failed to send email alert: {str(e)}")
                results["email"] = False

        # Check if Slack alerter is configured and should be used
        if self.slack_alerter and (not channels or "slack" in channels):
            try:
                success = await self.slack_alerter.send_alert(alert_data)
                results["slack"] = success
            except Exception as e:
                logger.error(f"Failed to send Slack alert: {str(e)}")
                results["slack"] = False

        # Check if Discord alerter is configured and should be used
        if self.discord_alerter and (not channels or "discord" in channels):
            try:
                success = await self.discord_alerter.send_alert(alert_data)
                results["discord"] = success
            except Exception as e:
                logger.error(f"Failed to send Discord alert: {str(e)}")
                results["discord"] = False

        return results

    async def send_alert_legacy(
        self,
        alert_type: str,
        severity: str,
        message: str,
        payload: Optional[Dict[str, Any]] = None,
        channels: Optional[List[str]] = None,
        retry: bool = True
    ) -> Dict[str, bool]:
        """
        Legacy method to send an alert through multiple channels concurrently.

        Args:
            alert_type: Type of alert (e.g., 'security', 'performance')
            severity: Alert severity ('critical', 'error', 'warning', 'info')
            message: Alert message
            payload: Optional additional data
            channels: List of channels to send to (defaults to all configured)
            retry: Whether to retry sending the alert if it fails

        Returns:
            Dict mapping channel names to success status
        """
        if not await self.rate_limiter.check_rate_limit('send_alert'):
            logger.warning("Rate limit exceeded for send_alert")
            return {channel: False for channel in self.channels.keys()}

        if not validate_alert_payload({
            'type': alert_type,
            'severity': severity,
            'message': message,
            'payload': payload
        }):
            logger.error("Invalid alert payload")
            return {channel: False for channel in self.channels.keys()}

        channels = channels or list(self.channels.keys())
        results = {}

        async def send_to_channel(channel: str) -> bool:
            try:
                if retry:
                    return await self._send_with_retry(
                        channel,
                        title=f"{severity.upper()} Alert: {alert_type}",
                        message=message,
                        severity=severity,
                        payload=payload
                    )
                else:
                    await self.channels[channel](
                        title=f"{severity.upper()} Alert: {alert_type}",
                        message=message,
                        severity=severity,
                        payload=payload
                    )
                    return True
            except Exception as e:
                logger.error(f"Failed to send alert to {channel}: {str(e)}")
                return False

        tasks = [send_to_channel(channel) for channel in channels]
        results_list = await asyncio.gather(*tasks)

        for channel, result in zip(channels, results_list):
            results[channel] = result

        return results

    async def send_report_notification(
        self,
        report_id: str,
        report_type: str,
        status: str,
        download_url: Optional[str] = None,
        retry: bool = True
    ) -> bool:
        """
        Send a notification about a generated report.

        Args:
            report_id: Unique identifier for the report
            report_type: Type of report generated
            status: Report generation status
            download_url: Optional URL to download the report
            retry: Whether to retry sending the notification if it fails

        Returns:
            bool indicating success
        """
        if not await self.rate_limiter.check_rate_limit('send_report'):
            logger.warning("Rate limit exceeded for send_report")
            return False

        message = f"Report {report_id} ({report_type}) has been {status}"
        if download_url:
            message += f"\nDownload URL: {download_url}"

        try:
            if retry:
                return await self._send_with_retry(
                    'email',
                    subject=f"Report Notification: {report_type}",
                    content=message,
                    severity="info"
                )
            else:
                await send_email_alert(
                    subject=f"Report Notification: {report_type}",
                    content=message,
                    severity="info"
                )
                return True
        except Exception as e:
            logger.error(f"Failed to send report notification: {str(e)}")
            return False

    async def send_bulk_alerts(
        self,
        alerts: List[Dict[str, Any]],
        channels: Optional[List[str]] = None
    ) -> Dict[str, List[bool]]:
        results = {channel: [] for channel in (channels or self.channels.keys())}

        for alert in alerts:
            alert_results = await self.send_alert(
                alert_type=alert['type'],
                severity=alert['severity'],
                message=alert['message'],
                payload=alert.get('payload'),
                channels=channels
            )

            for channel, result in alert_results.items():
                results[channel].append(result)

        return results

    def get_channel_status(self) -> Dict[str, bool]:
        return {
            channel: bool(settings.get(f"{channel.upper()}_WEBHOOK_URL"))
            for channel in self.channels.keys()
        }

# Instantiate the client for use in endpoints
alert_client = AlertingClient()

#-----------------------------------------------------#

# app/services/alerting/slack.py

import httpx
from app.core.config import settings, logger
from app.schemas import Alert # Import Alert schema for type hinting
from typing import Optional

async def send_slack_message(title: str, details: str, alert_data: Optional[Alert] = None):
    """
    Sends a formatted message to the configured Slack channel via webhook.

    Args:
        title: The main title of the alert.
        details: The formatted string containing alert details (using Markdown).
        alert_data: The original Alert object (optional, for adding actions/links).
    """
    if not settings.SLACK_WEBHOOK_URL:
        logger.debug("Slack webhook URL not configured. Skipping Slack notification.")
        return

    # Format message using Slack's Block Kit for better presentation
    # See: https://api.slack.com/block-kit
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": title,
                "emoji": True
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn", # Use Markdown
                "text": details
            }
        }
    ]

    # Optional: Add buttons for actions like Acknowledge, View Logs
    action_elements = []
    if alert_data:
        # Example: Add acknowledge button (requires backend endpoint to handle interaction)
        # action_elements.append({
        #     "type": "button",
        #     "text": { "type": "plain_text", "text": "Acknowledge", "emoji": True },
        #     "style": "primary",
        #     "action_id": f"acknowledge_alert_{alert_data.id}", # Unique action ID
        #     "value": str(alert_data.id) # Pass alert ID as value
        # })

        # Example: Add link to Grafana/Loki (construct URL based on alert data)
        # log_link = f"https://your-grafana.com/loki?query={{...}}&from={...}&to={...}" # Construct link
        # action_elements.append({
        #     "type": "button",
        #     "text": { "type": "plain_text", "text": "View Logs", "emoji": True },
        #     "url": log_link
        # })
        pass # Add actions here if needed

    if action_elements:
        blocks.append({
            "type": "actions",
            "elements": action_elements
        })

    payload = {
        "channel": settings.SLACK_CHANNEL,
        "username": "TwinSecure Bot",
        "icon_emoji": ":shield:",
        "blocks": blocks
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(settings.SLACK_WEBHOOK_URL, json=payload)
            response.raise_for_status() # Raise exception for 4xx/5xx responses
        # Success logged by the calling function (alert_client)
    except httpx.RequestError as e:
        # Error logged by the calling function
        raise ConnectionError(f"Failed to connect to Slack webhook: {e.request.url}") from e
    except httpx.HTTPStatusError as e:
        # Error logged by the calling function
        raise ConnectionError(f"Slack API returned error {e.response.status_code}: {e.response.text}") from e
    except Exception as e:
        # Error logged by the calling function
        raise RuntimeError(f"Unexpected error sending Slack notification: {e}") from e
