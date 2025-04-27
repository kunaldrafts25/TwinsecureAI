import httpx
from app.core.config import settings, logger
from app.schemas import Alert # Import Alert schema for type hinting
from typing import Optional
from datetime import datetime, timezone # Import datetime and timezone

async def send_discord_message(title: str, details: str, alert_data: Optional[Alert] = None):
    """
    Sends a formatted message to the configured Discord channel via webhook.

    Args:
        title: The main title for the embed.
        details: The formatted string for the embed description (supports Markdown).
        alert_data: The original Alert object (optional, for adding fields/context).
    """
    if not settings.DISCORD_WEBHOOK_URL:
        logger.debug("Discord webhook URL not configured. Skipping Discord notification.")
        return

    # Format message using Discord's embed structure
    # See: https://discord.com/developers/docs/resources/channel#embed-object
    embed = {
        "title": title[:256], # Embed title limit is 256 chars
        "description": details[:4096], # Embed description limit is 4096 chars
        "color": 15158332, # Example color (Red) - Use decimal representation of hex color (e.g., 0xE74C3C -> 15158332)
        "timestamp": datetime.now(timezone.utc).isoformat(), # Add timestamp
        "fields": []
    }

    # Optional: Add fields for structured data from alert_data
    if alert_data:
        if alert_data.severity:
            embed["fields"].append({"name": "Severity", "value": alert_data.severity.upper(), "inline": True})
        if alert_data.status:
             embed["fields"].append({"name": "Status", "value": alert_data.status.upper(), "inline": True})
        if alert_data.source_ip:
             embed["fields"].append({"name": "Source IP", "value": str(alert_data.source_ip), "inline": True})
        if alert_data.abuse_score is not None:
             embed["fields"].append({"name": "Abuse Score", "value": f"{alert_data.abuse_score}/100", "inline": True})
        if alert_data.ip_info and alert_data.ip_info.get('country'):
              embed["fields"].append({"name": "Country", "value": alert_data.ip_info['country'], "inline": True})
        # Add more fields as needed, respect embed limits (25 fields total)

    payload = {
        "username": "TwinSecure Bot",
        # "avatar_url": "URL_TO_YOUR_BOT_AVATAR.png", # Optional avatar
        "embeds": [embed]
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(settings.DISCORD_WEBHOOK_URL, json=payload)
            # Discord webhooks usually return 204 No Content on success
            if not (200 <= response.status_code < 300):
                 # Error logged by the calling function
                 raise httpx.HTTPStatusError(f"Discord webhook failed with status {response.status_code}", request=response.request, response=response)
            # Success logged by the calling function (alert_client)
    except httpx.RequestError as e:
        # Error logged by the calling function
        raise ConnectionError(f"Failed to connect to Discord webhook: {e.request.url}") from e
    except httpx.HTTPStatusError as e:
        # Error logged by the calling function
        raise ConnectionError(f"Discord API returned error {e.response.status_code}: {e.response.text}") from e
    except Exception as e:
        # Error logged by the calling function
        raise RuntimeError(f"Unexpected error sending Discord notification: {e}") from e