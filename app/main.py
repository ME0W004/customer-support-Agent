import os
from pathlib import Path
from typing import Any
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.config import settings
from app.db import (
    get_client,
    list_knowledge_base_sections,
    get_knowledge_base_section,
    upsert_knowledge_base_section,
    update_ticket_status
)
from app.gmail import GmailClient
from app.poller import run_poller_cycle

app = FastAPI(
    title="AI Customer Support Automation API",
    description="Backend API for Customer Support Agent with Supabase and Gemini",
    version="1.0.0"
)

# Enable CORS for local Vite dashboard development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_cached_gmail_client: GmailClient | None = None


def get_gmail_client() -> GmailClient:
    global _cached_gmail_client
    if _cached_gmail_client is None:
        _cached_gmail_client = GmailClient()
    return _cached_gmail_client


class KBUpdateRequest(BaseModel):
    title: str
    content: str


class TicketStatusUpdateRequest(BaseModel):
    status: str
    category: str | None = None


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "ai-customer-support",
        "environment": settings.APP_ENV,
        "support_email": settings.SUPPORT_EMAIL
    }


@app.get("/api/stats")
def get_stats() -> dict[str, Any]:
    sb = get_client()
    events_res = sb.table("events").select("id", count="exact").execute()
    tickets_res = sb.table("tickets").select("id, status").execute()

    total_events = events_res.count or 0
    tickets = tickets_res.data or []
    total_tickets = len(tickets)
    
    open_tickets = sum(1 for t in tickets if t.get("status") in ["new", "open"])
    escalated_tickets = sum(1 for t in tickets if t.get("status") == "escalated")
    closed_tickets = sum(1 for t in tickets if t.get("status") == "closed")

    return {
        "total_events": total_events,
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "escalated_tickets": escalated_tickets,
        "closed_tickets": closed_tickets
    }


@app.get("/api/events")
def list_events(limit: int = 50) -> list[dict[str, Any]]:
    sb = get_client()
    res = sb.table("events").select("*").order("created_at", desc=True).limit(limit).execute()
    return res.data or []


@app.get("/api/tickets")
def list_tickets(status: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
    sb = get_client()
    query = sb.table("tickets").select("*").order("updated_at", desc=True).limit(limit)
    if status:
        query = query.eq("status", status)
    res = query.execute()
    return res.data or []


@app.get("/api/tickets/{ticket_id}")
def get_ticket_details(ticket_id: str) -> dict[str, Any]:
    sb = get_client()
    ticket_res = sb.table("tickets").select("*").eq("id", ticket_id).execute()
    if not ticket_res.data:
        raise HTTPException(status_code=404, detail="Ticket not found")

    messages_res = sb.table("messages").select("*").eq("ticket_id", ticket_id).order("created_at", desc=False).execute()
    return {
        "ticket": ticket_res.data[0],
        "messages": messages_res.data or []
    }


@app.patch("/api/tickets/{ticket_id}")
def update_ticket(ticket_id: str, req: TicketStatusUpdateRequest) -> dict[str, str]:
    update_ticket_status(ticket_id, status=req.status, category=req.category)
    return {"message": "Ticket updated successfully"}


@app.get("/api/kb")
def get_knowledge_base() -> list[dict[str, Any]]:
    sb = get_client()
    res = sb.table("knowledge_base").select("*").order("slug").execute()
    return res.data or []


@app.get("/api/kb/{slug}")
def get_kb_article(slug: str) -> dict[str, Any]:
    content = get_knowledge_base_section(slug)
    if not content:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"slug": slug, "content": content}


@app.put("/api/kb/{slug}")
def update_kb_article(slug: str, req: KBUpdateRequest) -> dict[str, str]:
    upsert_knowledge_base_section(slug, title=req.title, content=req.content)
    return {"message": f"Article '{slug}' saved successfully"}


@app.post("/api/poll-now")
def trigger_poll_now(background_tasks: BackgroundTasks) -> dict[str, str]:
    """Manually triggers a poller cycle in the background."""
    def task():
        client = get_gmail_client()
        run_poller_cycle(client)

    background_tasks.add_task(task)
    return {"message": "Polling cycle initiated in background"}


# Serve static React Dashboard if built
dist_dir = Path("dashboard/dist")
if dist_dir.exists():
    app.mount("/", StaticFiles(directory=str(dist_dir), html=True), name="static")
