import logging
from email.utils import parseaddr
from typing import Any
from app.config import settings
from app.gmail import GmailClient, parse_headers, parse_body
from app.guards import get_skip_reason
from app.db import (
    start_event,
    update_event,
    get_or_create_ticket,
    save_message,
    update_ticket_status,
)
from app.ai.classifier import classify_email
from app.ai.agent import answer_customer_email

logger = logging.getLogger(__name__)


def process_message(client: GmailClient, message_item: dict[str, str]) -> dict[str, Any]:
    """
    Processes a single incoming Gmail message through the entire pipeline:
    Guardrails -> Classification -> DB logging -> Agentic Reply -> Gmail Reply -> Labeling.
    """
    msg_id = message_item["id"]
    thread_id = message_item["threadId"]

    # 1. Fetch full message details
    try:
        full_msg = client.get_message(msg_id)
    except Exception as e:
        logger.error(f"Failed to fetch message {msg_id}: {e}")
        return {"status": "error", "message_id": msg_id, "error": str(e)}

    headers = parse_headers(full_msg)
    body = parse_body(full_msg)
    subject = headers.get("subject", "(بدون موضوع)")
    from_raw = headers.get("from", "")
    _, sender_email = parseaddr(from_raw)

    # 2. Register event in Supabase (idempotency check)
    event = start_event(msg_id, thread_id, payload={
        "subject": subject,
        "from": from_raw,
        "date": headers.get("date", "")
    })
    if not event:
        # Already registered and processed
        return {"status": "already_processed", "message_id": msg_id}

    event_id = event["id"]

    # 3. Defensive Safety Guardrails
    skip_reason = get_skip_reason(headers)
    if skip_reason:
        logger.info(f"Skipping message {msg_id} due to guard: {skip_reason}")
        update_event(event_id, status="skipped", error=f"Guard: {skip_reason}")
        client.mark_as_processed(msg_id)
        return {"status": "skipped", "message_id": msg_id, "reason": skip_reason}

    # 4. Intent & Category Classification
    try:
        classification = classify_email(subject, body)
        logger.info(f"Classified {msg_id} as [{classification.section}], is_support={classification.is_support_request}")
    except Exception as e:
        logger.error(f"Classification failed for {msg_id}: {e}")
        update_event(event_id, status="failed", error=f"Classifier error: {e}")
        return {"status": "error", "message_id": msg_id, "error": str(e)}

    # Skip non-support emails (e.g. spam / promotional)
    if not classification.is_support_request or classification.section == "irrelevant":
        update_event(event_id, status="skipped", error="Not a customer support inquiry")
        client.mark_as_processed(msg_id)
        return {"status": "skipped", "message_id": msg_id, "reason": "irrelevant"}

    # 5. Database: Ticket & Inbound Message
    ticket = get_or_create_ticket(
        thread_id=thread_id,
        customer_email=sender_email,
        subject=subject,
        category=classification.section
    )
    ticket_id = ticket["id"]

    save_message(
        ticket_id=ticket_id,
        gmail_message_id=msg_id,
        direction="inbound",
        sender=sender_email,
        recipient=settings.SUPPORT_EMAIL,
        body=body
    )

    # 6. AI Agent Drafting with Knowledge Base Tools
    try:
        agent_reply = answer_customer_email(
            customer_email=sender_email,
            subject=subject,
            body=body,
            category=classification.section
        )
    except Exception as e:
        logger.error(f"Agent failed to draft reply for {msg_id}: {e}")
        update_event(event_id, status="failed", error=f"Agent error: {e}")
        return {"status": "error", "message_id": msg_id, "error": str(e)}

    # 7. Python Decision Engine: Auto-Reply vs. Escalation
    in_reply_to_header = headers.get("message-id", "")
    ticket_short_id = str(ticket_id)[:8]

    if agent_reply.escalate_to_human or agent_reply.confidence < 0.70 or not agent_reply.is_resolved:
        # Escalation path
        update_ticket_status(ticket_id, status="escalated", category=classification.section)
        
        escalation_email = (
            f"Dear Customer,\n\n"
            f"Thank you for contacting CloudScale AI Support. Your inquiry has been logged under Ticket ID [{ticket_short_id}].\n"
            f"Because your request requires specialized administrative review (Billing Operations / Technical Engineering), "
            f"your file has been prioritized and routed to our dedicated specialist team. A senior specialist will follow up with you shortly.\n\n"
            f"Thank you for your patience and for choosing CloudScale AI.\n\n"
            f"Best regards,\n"
            f"CloudScale AI Customer Success & Support Team"
        )
        
        sent_msg = client.send_reply(
            thread_id=thread_id,
            in_reply_to_header=in_reply_to_header,
            to_email=sender_email,
            subject=subject,
            body_text=escalation_email
        )
        save_message(
            ticket_id=ticket_id,
            gmail_message_id=sent_msg["id"],
            direction="outbound",
            sender=settings.SUPPORT_EMAIL,
            recipient=sender_email,
            body=escalation_email
        )
        action_taken = "escalated"
    else:
        # Full automatic resolution
        sent_msg = client.send_reply(
            thread_id=thread_id,
            in_reply_to_header=in_reply_to_header,
            to_email=sender_email,
            subject=subject,
            body_text=agent_reply.reply_text
        )
        save_message(
            ticket_id=ticket_id,
            gmail_message_id=sent_msg["id"],
            direction="outbound",
            sender=settings.SUPPORT_EMAIL,
            recipient=sender_email,
            body=agent_reply.reply_text
        )
        update_ticket_status(ticket_id, status="closed", category=classification.section)
        action_taken = "replied"

    # 8. Mark processed in Gmail & update event in Supabase
    client.mark_as_processed(msg_id)
    update_event(event_id, status="processed")

    logger.info(f"Successfully processed message {msg_id}: action={action_taken}, ticket={ticket_id}")
    return {
        "status": "processed",
        "message_id": msg_id,
        "ticket_id": ticket_id,
        "action": action_taken,
        "confidence": agent_reply.confidence
    }
