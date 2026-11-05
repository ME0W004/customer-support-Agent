from datetime import datetime, timezone
import logging
from typing import Any
from supabase import create_client, Client
from app.config import settings

logger = logging.getLogger(__name__)

_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        _client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    return _client


def start_event(gmail_message_id: str, thread_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
    """
    Atomically registers an incoming email event.
    Returns the event record if newly created, or None if already processed (deduplication).
    """
    sb = get_client()
    # Check if already processed
    existing = sb.table("events").select("*").eq("gmail_message_id", gmail_message_id).execute()
    if existing.data and len(existing.data) > 0:
        logger.info(f"Event for message {gmail_message_id} already exists, skipping.")
        return None

    res = sb.table("events").insert({
        "gmail_message_id": gmail_message_id,
        "thread_id": thread_id,
        "payload": payload,
        "status": "pending"
    }).execute()

    return res.data[0] if res.data else None


def update_event(event_id: str, status: str, error: str | None = None) -> None:
    """Updates event status and optional error message."""
    sb = get_client()
    sb.table("events").update({
        "status": status,
        "error": error
    }).eq("id", event_id).execute()


def get_or_create_ticket(thread_id: str, customer_email: str, subject: str, category: str = "general") -> dict[str, Any]:
    """Finds an existing ticket for the email thread or creates a new one."""
    sb = get_client()
    existing = sb.table("tickets").select("*").eq("thread_id", thread_id).execute()
    if existing.data and len(existing.data) > 0:
        return existing.data[0]

    now_iso = datetime.now(timezone.utc).isoformat()
    res = sb.table("tickets").insert({
        "thread_id": thread_id,
        "customer_email": customer_email,
        "subject": subject,
        "status": "open",
        "category": category,
        "created_at": now_iso,
        "updated_at": now_iso
    }).execute()

    return res.data[0]


def save_message(ticket_id: str, gmail_message_id: str, direction: str, sender: str, recipient: str, body: str) -> dict[str, Any]:
    """Logs an inbound or outbound email message under a ticket."""
    sb = get_client()
    # Check if message already recorded
    existing = sb.table("messages").select("*").eq("gmail_message_id", gmail_message_id).execute()
    if existing.data and len(existing.data) > 0:
        return existing.data[0]

    res = sb.table("messages").insert({
        "ticket_id": ticket_id,
        "gmail_message_id": gmail_message_id,
        "direction": direction,
        "sender": sender,
        "recipient": recipient,
        "body": body
    }).execute()

    return res.data[0]


def update_ticket_status(ticket_id: str, status: str, category: str | None = None) -> None:
    """Updates ticket status (e.g. 'open', 'escalated', 'closed') and category."""
    sb = get_client()
    data: dict[str, Any] = {
        "status": status,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    if category:
        data["category"] = category
    sb.table("tickets").update(data).eq("id", ticket_id).execute()


def get_knowledge_base_section(slug: str) -> str | None:
    """Fetches the markdown content for a given knowledge base slug."""
    sb = get_client()
    res = sb.table("knowledge_base").select("content").eq("slug", slug).execute()
    if res.data and len(res.data) > 0:
        return res.data[0]["content"]
    return None


def list_knowledge_base_sections() -> list[dict[str, Any]]:
    """Returns all knowledge base articles."""
    sb = get_client()
    res = sb.table("knowledge_base").select("id, slug, title, updated_at").execute()
    return res.data or []


def upsert_knowledge_base_section(slug: str, title: str, content: str) -> None:
    """Inserts or updates a knowledge base article."""
    sb = get_client()
    now_iso = datetime.now(timezone.utc).isoformat()
    existing = sb.table("knowledge_base").select("id").eq("slug", slug).execute()
    if existing.data and len(existing.data) > 0:
        sb.table("knowledge_base").update({
            "title": title,
            "content": content,
            "updated_at": now_iso
        }).eq("slug", slug).execute()
    else:
        sb.table("knowledge_base").insert({
            "slug": slug,
            "title": title,
            "content": content,
            "updated_at": now_iso
        }).execute()
