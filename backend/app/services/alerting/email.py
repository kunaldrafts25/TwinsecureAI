"""
TwinSecure - Advanced Cybersecurity Platform
Copyright © 2024 TwinSecure. All rights reserved.

This file is part of TwinSecure, a proprietary cybersecurity platform.
Unauthorized copying, distribution, modification, or use of this software
is strictly prohibited without explicit written permission.

For licensing inquiries: kunalsingh2514@gmail.com
"""

import asyncio  # Use asyncio's thread pool for blocking smtplib
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, formatdate
from typing import Any, Dict, List, Optional, Union

from app.core.config import logger, settings


class EmailAlerter:
    """Class for sending alerts via email."""

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int = 587,
        username: Optional[str] = None,
        password: Optional[str] = None,
        from_email: str = "alerts@example.com",
        to_emails: Union[str, List[str]] = None,
        use_tls: bool = True,
    ):
        """
        Initialize the email alerter.

        Args:
            smtp_server: SMTP server hostname
            smtp_port: SMTP server port
            username: SMTP username
            password: SMTP password
            from_email: Sender email address
            to_emails: Recipient email address(es)
            use_tls: Whether to use TLS
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email

        if isinstance(to_emails, str):
            self.to_emails = [to_emails]
        elif isinstance(to_emails, list):
            self.to_emails = to_emails
        else:
            self.to_emails = []

        self.use_tls = use_tls

    async def send_alert(self, alert_data: Dict[str, Any]) -> bool:
        """
        Send an alert via email.

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

            # Create subject and content
            subject = f"{severity} Alert: {title}"
            content = f"Alert: {title}\nSeverity: {severity}\n\n{description}"

            # Add additional information if available
            if "id" in alert_data:
                content += f"\n\nAlert ID: {alert_data['id']}"

            # Send the email
            await self._send_email(subject, content)
            return True
        except Exception as e:
            logger.error(f"Failed to send email alert: {str(e)}")
            return False

    async def _send_email(self, subject: str, content: str) -> None:
        """
        Send an email using SMTP.

        Args:
            subject: Email subject
            content: Email content
        """
        # Create message
        message = MIMEMultipart()
        message["Subject"] = subject
        message["From"] = self.from_email
        message["To"] = ", ".join(self.to_emails)
        message["Date"] = formatdate(localtime=True)

        # Attach content
        part = MIMEText(content, "plain")
        message.attach(part)

        # Define synchronous function to send email
        def send_sync():
            smtp = None
            try:
                # Connect to SMTP server
                smtp = smtplib.SMTP(self.smtp_server, self.smtp_port)

                # Use TLS if enabled
                if self.use_tls:
                    smtp.starttls()

                # Login if credentials provided
                if self.username and self.password:
                    smtp.login(self.username, self.password)

                # Send email
                smtp.send_message(message)

                return True
            finally:
                # Close connection
                if smtp:
                    smtp.quit()

        # Run synchronous function in thread pool
        await asyncio.to_thread(send_sync)


async def send_email_alert(subject: str, content: str):
    """
    Sends an email alert using configured SMTP settings.
    Runs the blocking smtplib operations in a separate thread.

    Args:
        subject: The email subject line.
        content: The plain text body of the email.
    """
    if not all(
        [
            settings.SMTP_HOST,
            settings.SMTP_USER,
            settings.SMTP_PASSWORD,
            settings.EMAILS_FROM_EMAIL,
            settings.ALERT_RECIPIENTS,
        ]
    ):
        logger.debug("SMTP settings incomplete. Skipping email notification.")
        return

    # Use formataddr for proper 'From' header encoding
    sender_name = str(
        Header(settings.EMAILS_FROM_NAME or settings.PROJECT_NAME, "utf-8")
    )
    sender_email = settings.EMAILS_FROM_EMAIL
    from_header = formataddr((sender_name, sender_email))
    recipients = settings.ALERT_RECIPIENTS

    # Create message
    message = MIMEMultipart("alternative")
    message["Subject"] = Header(subject, "utf-8").encode()
    message["From"] = from_header
    message["To"] = ", ".join(recipients)  # Comma-separated list for header
    message["Date"] = formatdate(localtime=True)  # Add Date header

    # Attach plain text part
    # Consider adding an HTML part for richer formatting:
    # html_content = f"<html><body><pre>{content}</pre></body></html>" # Basic HTML example
    # part_html = MIMEText(html_content, 'html', 'utf-8')
    # message.attach(part_html)
    part_text = MIMEText(content, "plain", "utf-8")
    message.attach(part_text)

    def send_sync():
        """Synchronous function to send email, to be run in thread pool."""
        smtp_server = None
        try:
            logger.debug(
                f"Connecting to SMTP server: {settings.SMTP_HOST}:{settings.SMTP_PORT or (587 if settings.SMTP_TLS else 25)}"
            )
            if settings.SMTP_TLS:
                smtp_server = smtplib.SMTP(
                    settings.SMTP_HOST, settings.SMTP_PORT or 587, timeout=15
                )
                smtp_server.ehlo()  # Identify client to server
                smtp_server.starttls()
                smtp_server.ehlo()  # Re-identify after TLS
            else:
                smtp_server = smtplib.SMTP(
                    settings.SMTP_HOST, settings.SMTP_PORT or 25, timeout=15
                )
                smtp_server.ehlo()

            logger.debug(f"Logging into SMTP server as user: {settings.SMTP_USER}")
            smtp_server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            logger.debug(f"Sending email to: {recipients}")
            smtp_server.sendmail(sender_email, recipients, message.as_string())
            logger.debug(f"Email '{subject}' sent.")
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication Error sending email: {e}")
            raise ConnectionRefusedError(
                f"SMTP Authentication failed (Code: {e.smtp_code}): {e.smtp_error}"
            ) from e
        except smtplib.SMTPServerDisconnected as e:
            logger.error(f"SMTP Server Disconnected error sending email: {e}")
            raise ConnectionAbortedError(
                f"SMTP server disconnected unexpectedly."
            ) from e
        except smtplib.SMTPException as e:
            logger.error(f"SMTP Error sending email: {e}")
            raise ConnectionError(
                f"General SMTP error (Code: {e.smtp_code}): {e.smtp_error}"
            ) from e
        except OSError as e:  # Catch potential socket errors (includes TimeoutError)
            logger.error(f"Socket or OS error connecting/sending SMTP: {e}")
            raise ConnectionError(f"Network error during SMTP operation: {e}") from e
        except Exception as e:
            logger.error(
                f"An unexpected error occurred sending email: {e}", exc_info=True
            )
            raise RuntimeError(f"Unexpected email error: {e}") from e
        finally:
            if smtp_server:
                try:
                    smtp_server.quit()
                    logger.debug("SMTP connection closed.")
                except smtplib.SMTPException:
                    logger.warning(
                        "Error closing SMTP connection, might already be closed."
                    )

    try:
        # Run the blocking SMTP operations in asyncio's default thread pool
        await asyncio.to_thread(send_sync)
        # Success logged by the calling function (alert_client)
    except Exception as e:
        # Error logged by the calling function
        # Re-raise the specific exception type caught in send_sync
        raise e
