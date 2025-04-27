import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr, formatdate
from app.core.config import settings, logger
import asyncio # Use asyncio's thread pool for blocking smtplib

async def send_email_alert(subject: str, content: str):
    """
    Sends an email alert using configured SMTP settings.
    Runs the blocking smtplib operations in a separate thread.

    Args:
        subject: The email subject line.
        content: The plain text body of the email.
    """
    if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD, settings.EMAILS_FROM_EMAIL, settings.ALERT_RECIPIENTS]):
        logger.debug("SMTP settings incomplete. Skipping email notification.")
        return

    # Use formataddr for proper 'From' header encoding
    sender_name = str(Header(settings.EMAILS_FROM_NAME or settings.PROJECT_NAME, 'utf-8'))
    sender_email = settings.EMAILS_FROM_EMAIL
    from_header = formataddr((sender_name, sender_email))
    recipients = settings.ALERT_RECIPIENTS

    # Create message
    message = MIMEMultipart('alternative')
    message['Subject'] = Header(subject, 'utf-8').encode()
    message['From'] = from_header
    message['To'] = ", ".join(recipients) # Comma-separated list for header
    message['Date'] = formatdate(localtime=True) # Add Date header

    # Attach plain text part
    # Consider adding an HTML part for richer formatting:
    # html_content = f"<html><body><pre>{content}</pre></body></html>" # Basic HTML example
    # part_html = MIMEText(html_content, 'html', 'utf-8')
    # message.attach(part_html)
    part_text = MIMEText(content, 'plain', 'utf-8')
    message.attach(part_text)

    def send_sync():
        """Synchronous function to send email, to be run in thread pool."""
        smtp_server = None
        try:
            logger.debug(f"Connecting to SMTP server: {settings.SMTP_HOST}:{settings.SMTP_PORT or (587 if settings.SMTP_TLS else 25)}")
            if settings.SMTP_TLS:
                smtp_server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT or 587, timeout=15)
                smtp_server.ehlo() # Identify client to server
                smtp_server.starttls()
                smtp_server.ehlo() # Re-identify after TLS
            else:
                smtp_server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT or 25, timeout=15)
                smtp_server.ehlo()

            logger.debug(f"Logging into SMTP server as user: {settings.SMTP_USER}")
            smtp_server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            logger.debug(f"Sending email to: {recipients}")
            smtp_server.sendmail(sender_email, recipients, message.as_string())
            logger.debug(f"Email '{subject}' sent.")
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication Error sending email: {e}")
            raise ConnectionRefusedError(f"SMTP Authentication failed (Code: {e.smtp_code}): {e.smtp_error}") from e
        except smtplib.SMTPServerDisconnected as e:
             logger.error(f"SMTP Server Disconnected error sending email: {e}")
             raise ConnectionAbortedError(f"SMTP server disconnected unexpectedly.") from e
        except smtplib.SMTPException as e:
            logger.error(f"SMTP Error sending email: {e}")
            raise ConnectionError(f"General SMTP error (Code: {e.smtp_code}): {e.smtp_error}") from e
        except OSError as e: # Catch potential socket errors (includes TimeoutError)
             logger.error(f"Socket or OS error connecting/sending SMTP: {e}")
             raise ConnectionError(f"Network error during SMTP operation: {e}") from e
        except Exception as e:
            logger.error(f"An unexpected error occurred sending email: {e}", exc_info=True)
            raise RuntimeError(f"Unexpected email error: {e}") from e
        finally:
            if smtp_server:
                try:
                    smtp_server.quit()
                    logger.debug("SMTP connection closed.")
                except smtplib.SMTPException:
                    logger.warning("Error closing SMTP connection, might already be closed.")


    try:
        # Run the blocking SMTP operations in asyncio's default thread pool
        await asyncio.to_thread(send_sync)
        # Success logged by the calling function (alert_client)
    except Exception as e:
        # Error logged by the calling function
        # Re-raise the specific exception type caught in send_sync
        raise e
