"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

Email alerting channel implementation.
"""

import asyncio
import logging
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, formatdate

from app.core.config import settings

from .base import AlertChannel, AlertPayload

logger = logging.getLogger(__name__)


class EmailChannel(AlertChannel):
    """Alert channel for email notifications via SMTP."""
    
    def initialize(self) -> None:
        """Initialize email channel and validate SMTP settings."""
        self.smtp_host = self.config.get("smtp_host") or settings.SMTP_HOST
        self.smtp_port = self.config.get("smtp_port") or settings.SMTP_PORT or 587
        self.smtp_user = self.config.get("smtp_user") or settings.SMTP_USER
        self.smtp_password = self.config.get("smtp_password") or settings.SMTP_PASSWORD
        self.use_tls = self.config.get("use_tls", settings.SMTP_TLS)
        self.from_email = self.config.get("from_email") or settings.EMAILS_FROM_EMAIL
        self.from_name = self.config.get("from_name") or settings.EMAILS_FROM_NAME or settings.PROJECT_NAME
        
        recipients = self.config.get("recipients") or settings.ALERT_RECIPIENTS
        if isinstance(recipients, str):
            self.recipients = [recipients]
        elif isinstance(recipients, list):
            self.recipients = recipients
        else:
            self.recipients = []
        
        # Validate required settings
        if not all([self.smtp_host, self.smtp_user, self.smtp_password, self.from_email, self.recipients]):
            logger.warning("Email channel: SMTP settings incomplete")
            self.enabled = False
    
    async def send_alert(self, payload: AlertPayload) -> bool:
        """
        Send an alert via email using SMTP.
        
        Args:
            payload: The alert payload to send
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.debug("Email channel is disabled, skipping")
            return False
        
        try:
            subject = f"[{payload.severity.upper()}] {payload.title}"
            content = await self.format_message(payload)
            
            await self._send_email(subject, content)
            return True
        
        except Exception as e:
            logger.exception(f"Failed to send email alert: {e}")
            return False
    
    async def _send_email(self, subject: str, content: str) -> None:
        """
        Send email using SMTP in a separate thread.
        
        Args:
            subject: Email subject
            content: Email body content
        """
        message = self._create_message(subject, content)
        
        # Run blocking SMTP operations in thread pool
        await asyncio.to_thread(self._send_smtp, message)
    
    def _create_message(self, subject: str, content: str) -> MIMEMultipart:
        """
        Create email message.
        
        Args:
            subject: Email subject
            content: Email body
            
        Returns:
            MIME message object
        """
        message = MIMEMultipart("alternative")
        
        # Set headers
        sender_name = str(Header(self.from_name, "utf-8"))
        from_header = formataddr((sender_name, self.from_email))
        
        message["Subject"] = Header(subject, "utf-8").encode()
        message["From"] = from_header
        message["To"] = ", ".join(self.recipients)
        message["Date"] = formatdate(localtime=True)
        
        # Attach text part
        part_text = MIMEText(content, "plain", "utf-8")
        message.attach(part_text)
        
        # Optional: Add HTML part for richer formatting
        # html_content = f"<html><body><pre>{content}</pre></body></html>"
        # part_html = MIMEText(html_content, "html", "utf-8")
        # message.attach(part_html)
        
        return message
    
    def _send_smtp(self, message: MIMEMultipart) -> None:
        """
        Send email via SMTP (synchronous, runs in thread pool).
        
        Args:
            message: MIME message to send
            
        Raises:
            Various SMTP exceptions on failure
        """
        smtp_server = None
        
        try:
            logger.debug(f"Connecting to SMTP server: {self.smtp_host}:{self.smtp_port}")
            
            # Connect to SMTP server
            smtp_server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=15)
            smtp_server.ehlo()
            
            # Use TLS if enabled
            if self.use_tls:
                smtp_server.starttls()
                smtp_server.ehlo()  # Re-identify after TLS
            
            # Authenticate
            logger.debug(f"Logging into SMTP server as: {self.smtp_user}")
            smtp_server.login(self.smtp_user, self.smtp_password)
            
            # Send email
            logger.debug(f"Sending email to: {self.recipients}")
            smtp_server.sendmail(self.from_email, self.recipients, message.as_string())
            
            logger.info(f"Email sent successfully to {len(self.recipients)} recipient(s)")
        
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication Error: {e}")
            raise ConnectionRefusedError(
                f"SMTP Authentication failed (Code: {e.smtp_code}): {e.smtp_error}"
            ) from e
        
        except smtplib.SMTPServerDisconnected as e:
            logger.error(f"SMTP Server Disconnected: {e}")
            raise ConnectionAbortedError("SMTP server disconnected unexpectedly") from e
        
        except smtplib.SMTPException as e:
            logger.error(f"SMTP Error: {e}")
            raise ConnectionError(
                f"SMTP error (Code: {e.smtp_code}): {e.smtp_error}"
            ) from e
        
        except OSError as e:
            logger.error(f"Network error during SMTP: {e}")
            raise ConnectionError(f"Network error: {e}") from e
        
        finally:
            if smtp_server:
                try:
                    smtp_server.quit()
                    logger.debug("SMTP connection closed")
                except smtplib.SMTPException:
                    logger.warning("Error closing SMTP connection")
