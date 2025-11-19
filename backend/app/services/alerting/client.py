"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

Unified alert client for managing multiple channels.
"""

import logging

from app.core.config import settings
from app.db.models.alert import Alert

from .base import AlertChannel, AlertClient, AlertPayload
from .discord import DiscordChannel
from .email import EmailChannel
from .slack import SlackChannel

logger = logging.getLogger(__name__)


def create_alert_client() -> AlertClient:
    """
    Factory function to create and configure the alert client.
    
    Returns:
        Configured AlertClient instance with all enabled channels
    """
    client = AlertClient()
    
    # Register Discord channel if configured
    if settings.DISCORD_WEBHOOK_URL:
        discord = DiscordChannel(config={"webhook_url": settings.DISCORD_WEBHOOK_URL})
        client.register_channel(discord)
    
    # Register Email channel if configured
    if all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD]):
        email = EmailChannel(config={
            "smtp_host": settings.SMTP_HOST,
            "smtp_port": settings.SMTP_PORT,
            "smtp_user": settings.SMTP_USER,
            "smtp_password": settings.SMTP_PASSWORD,
            "from_email": settings.EMAILS_FROM_EMAIL,
            "from_name": settings.EMAILS_FROM_NAME or settings.PROJECT_NAME,
            "recipients": settings.ALERT_RECIPIENTS,
            "use_tls": settings.SMTP_TLS,
        })
        client.register_channel(email)
    
    # Register Slack channel if configured
    if settings.SLACK_WEBHOOK_URL:
        slack = SlackChannel(config={
            "webhook_url": settings.SLACK_WEBHOOK_URL,
            "channel": getattr(settings, "SLACK_CHANNEL", None),
        })
        client.register_channel(slack)
    
    logger.info(f"Alert client initialized with {len(client.channels)} channel(s)")
    return client


# Global alert client instance
alert_client = create_alert_client()
