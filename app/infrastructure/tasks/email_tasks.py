"""
Email-related background tasks.
"""
import logging
from typing import Optional

from app.infrastructure.tasks.base import BaseTask
from app.infrastructure.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    base=BaseTask,
    bind=True,
    name="app.infrastructure.tasks.email_tasks.send_email",
)
def send_email(
    self,
    to_email: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None,
) -> dict:
    """
    Send an email asynchronously.

    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Plain text body
        html_body: Optional HTML body

    Returns:
        dict with status and message_id

    Note:
        Implement actual email sending logic here.
        This is a placeholder that logs the email.
    """
    logger.info(f"Sending email to {to_email}: {subject}")

    # TODO: Implement actual email sending
    # Example with SMTP:
    # import smtplib
    # from email.mime.text import MIMEText
    # from email.mime.multipart import MIMEMultipart
    #
    # msg = MIMEMultipart("alternative")
    # msg["Subject"] = subject
    # msg["From"] = settings.email_from
    # msg["To"] = to_email
    #
    # msg.attach(MIMEText(body, "plain"))
    # if html_body:
    #     msg.attach(MIMEText(html_body, "html"))
    #
    # with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
    #     server.starttls()
    #     server.login(settings.smtp_user, settings.smtp_password)
    #     server.send_message(msg)

    return {
        "status": "sent",
        "to": to_email,
        "subject": subject,
    }


@celery_app.task(
    base=BaseTask,
    bind=True,
    name="app.infrastructure.tasks.email_tasks.send_welcome_email",
)
def send_welcome_email(self, user_email: str, user_name: str) -> dict:
    """Send welcome email to new user"""
    subject = "Welcome to Our Platform!"
    body = f"""
Hi {user_name},

Welcome to our platform! We're excited to have you on board.

Best regards,
The Team
"""

    return send_email.delay(
        to_email=user_email,
        subject=subject,
        body=body,
    ).get()


@celery_app.task(
    base=BaseTask,
    bind=True,
    name="app.infrastructure.tasks.email_tasks.send_password_reset_email",
)
def send_password_reset_email(
    self,
    user_email: str,
    reset_token: str,
    reset_url: str,
) -> dict:
    """Send password reset email"""
    subject = "Password Reset Request"
    body = f"""
You requested a password reset.

Click the link below to reset your password:
{reset_url}?token={reset_token}

This link will expire in 1 hour.

If you didn't request this, please ignore this email.

Best regards,
The Team
"""

    return send_email.delay(
        to_email=user_email,
        subject=subject,
        body=body,
    ).get()
