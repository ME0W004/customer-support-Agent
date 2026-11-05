from email.utils import parseaddr
from app.config import settings


def get_skip_reason(headers: dict[str, str]) -> str | None:
    """
    Evaluates defensive guards before invoking LLMs.
    Returns a string reason to skip, or None if safe to process.
    """
    from_header = headers.get("from", "")
    _, sender_email = parseaddr(from_header)
    sender_email = sender_email.lower().strip()

    # 1. Prevent self-reply loops
    own_email = settings.SUPPORT_EMAIL.lower().strip()
    if sender_email == own_email:
        return "own_address"

    # 2. Automated bounce and robot addresses
    if any(bot in sender_email for bot in ["mailer-daemon", "noreply", "no-reply", "postmaster"]):
        return "automated_sender"

    # 3. Auto-Submitted header (RFC 3834)
    auto_submitted = headers.get("auto-submitted", "").lower()
    if auto_submitted and auto_submitted != "no":
        return f"auto_submitted_{auto_submitted}"

    # 4. Common Out-of-office / auto-reply headers
    if headers.get("x-autoreply", "").lower() == "yes":
        return "x_autoreply"
    if headers.get("x-autorespond", "").lower() == "yes":
        return "x_autorespond"

    # 5. Bulk / list / spam precedence
    precedence = headers.get("precedence", "").lower()
    if precedence in ["bulk", "junk", "list"]:
        return f"precedence_{precedence}"

    # 6. Delivery failure / bounce subjects
    subject = headers.get("subject", "").lower()
    bounce_indicators = [
        "delivery status notification",
        "undeliverable:",
        "failure notice",
        "mail delivery failed",
        "returned mail"
    ]
    if any(indicator in subject for indicator in bounce_indicators):
        return "bounce_notification"

    return None
