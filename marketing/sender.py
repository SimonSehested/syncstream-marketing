import logging
import resend
from typing import Optional

from .config import RESEND_API_KEY, RESEND_FROM_EMAIL


logger = logging.getLogger(__name__)


resend.api_key = RESEND_API_KEY


def send_email(to_email: str, subject: str, html_body: str, bcc_email: Optional[str] = None) -> bool:
    if not to_email:
        logger.warning(f"[SENDER] No email address provided, skipping")
        return False

    if not RESEND_API_KEY:
        logger.info(f"[SENDER] Would send email to {to_email}: {subject}")
        return True

    params = {
        "from": RESEND_FROM_EMAIL,
        "to": to_email,
        "subject": subject,
        "html": html_body,
    }
    if bcc_email:
        params["bcc"] = bcc_email

    try:
        resp = resend.Emails.send(params)
        logger.info(f"[SENDER] Email sent to {to_email}: {resp}")
        return True
    except Exception as e:
        logger.error(f"[SENDER] Failed to send to {to_email}: {e}")
        return False
