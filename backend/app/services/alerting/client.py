from app.core.config import settings, logger
from app.schemas import Alert # Use the Alert schema for type hinting
from .slack import send_slack_message
from .email import send_email_alert
from .discord import send_discord_message
import asyncio # For running multiple alerts concurrently
from app.db.models import Report # Import Report model if needed for type hinting report_data

class AlertingClient:
    """
    Client to orchestrate sending alerts via multiple channels.
    """

    async def send_alert(self, alert_data: Alert):
        """
        Sends an alert notification through all configured channels.

        Args:
            alert_data: The Alert object containing details to send.
        """
        logger.info(f"Sending alert notifications for Alert ID: {alert_data.id}, Type: {alert_data.alert_type}, IP: {alert_data.source_ip}")

        # --- Format the message (customize as needed) ---
        title = f"🚨 TwinSecure Alert: {alert_data.alert_type} 🚨"
        details = (
            f"*Timestamp:* {alert_data.triggered_at.isoformat() if alert_data.triggered_at else 'N/A'}\n"
            f"*Source IP:* {alert_data.source_ip or 'N/A'}\n"
            f"*Severity:* {alert_data.severity.upper() if alert_data.severity else 'N/A'}\n"
            f"*Status:* {alert_data.status.upper() if alert_data.status else 'N/A'}\n"
        )
        if alert_data.ip_info:
            details += f"*Location:* {alert_data.ip_info.get('city', 'N/A')}, {alert_data.ip_info.get('country', 'N/A')}\n"
            # Add ASN if available in your GeoIP data structure
            # details += f"*ASN:* {alert_data.ip_info.get('asn', 'N/A')}\n"
        if alert_data.abuse_score is not None:
            details += f"*Abuse Score:* {alert_data.abuse_score}/100\n"
        if alert_data.payload:
            # Avoid sending huge payloads directly, maybe summarize or link
            try:
                # Attempt to pretty-print if JSON, otherwise just take string slice
                import json
                payload_summary = json.dumps(alert_data.payload, indent=2)
                if len(payload_summary) > 300:
                     payload_summary = payload_summary[:300] + "\n... (truncated)"
            except (TypeError, json.JSONDecodeError):
                 payload_summary = str(alert_data.payload)[:300] + "..." # Limit payload preview

            details += f"*Payload Snippet:* ```\n{payload_summary}\n```\n"
        if alert_data.notes:
            details += f"*Notes:* {alert_data.notes}\n"

        # Add link to dashboard (replace with actual frontend URL from settings?)
        # dashboard_link = f"{settings.FRONTEND_URL}/alerts/{alert_data.id}"
        # details += f"\n*Link:* <{dashboard_link}|View in Dashboard>"

        # --- Send concurrently ---
        tasks = []
        if settings.SLACK_WEBHOOK_URL:
            # Pass alert_data if Slack function needs more context
            tasks.append(send_slack_message(title=title, details=details, alert_data=alert_data))
        if settings.SMTP_HOST and settings.ALERT_RECIPIENTS:
             # Email might need different formatting (HTML?)
            email_subject = title
            # Basic text conversion, consider HTML for better formatting
            email_body = details.replace("*", "").replace("`", "")
            tasks.append(send_email_alert(subject=email_subject, content=email_body))
        if settings.DISCORD_WEBHOOK_URL:
             # Pass alert_data if Discord function needs more context
            tasks.append(send_discord_message(title=title, details=details, alert_data=alert_data))

        if not tasks:
            logger.warning(f"No alerting channels configured for alert ID: {alert_data.id}")
            return

        logger.debug(f"Dispatching {len(tasks)} alert notifications for alert ID: {alert_data.id}")
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Log results/errors
        # Determine which task failed based on order and configuration
        channel_map = []
        if settings.SLACK_WEBHOOK_URL: channel_map.append("Slack")
        if settings.SMTP_HOST and settings.ALERT_RECIPIENTS: channel_map.append("Email")
        if settings.DISCORD_WEBHOOK_URL: channel_map.append("Discord")

        for i, result in enumerate(results):
            channel = channel_map[i] if i < len(channel_map) else "Unknown Channel"
            if isinstance(result, Exception):
                logger.error(f"Failed to send alert ID {alert_data.id} via {channel}: {result}", exc_info=False) # Avoid logging full trace unless needed
            else:
                 logger.info(f"Alert ID {alert_data.id} sent successfully via {channel}.")


    async def send_report_notification(self, report_data: dict):
        """
        Sends a notification about a newly generated report (primarily email).

        Args:
            report_data: Dictionary containing report metadata (title, summary, download_url, generated_at, recommendations).
                         Should ideally match the Report schema structure.
        """
        report_title = report_data.get('title', 'N/A')
        logger.info(f"Sending notification for generated report: {report_title}")

        subject = f"📊 TwinSecure Report Generated: {report_title}"
        generated_at_str = report_data.get('generated_at')
        if isinstance(generated_at_str, datetime): # Format datetime if needed
             generated_at_str = generated_at_str.strftime('%Y-%m-%d %H:%M:%S UTC')

        body = (
            f"A new security report has been generated:\n\n"
            f"Title: {report_title}\n"
            f"Summary: {report_data.get('summary', 'N/A')}\n"
            f"Generated At: {generated_at_str or 'N/A'}\n\n"
            # Assuming a download URL is constructed and passed in report_data
            f"Download Link: {report_data.get('download_url', 'Link not available')}\n\n"
            f"Recommendations:\n{report_data.get('recommendations', 'N/A')}\n"
        )

        if settings.SMTP_HOST and settings.ALERT_RECIPIENTS:
            try:
                await send_email_alert(subject=subject, content=body)
                logger.info(f"Report notification email sent successfully for: {report_title}")
            except Exception as e:
                logger.error(f"Failed to send report notification email for {report_title}: {e}")
        else:
            logger.warning(f"Email (SMTP) is not configured. Cannot send report notification for: {report_title}")


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
