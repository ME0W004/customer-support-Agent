import os
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from pydantic_ai import Agent
from app.config import settings
from app.ai.schemas import AgentReply
from app.db import get_knowledge_base_section, list_knowledge_base_sections

logger = logging.getLogger(__name__)

os.environ["GEMINI_API_KEY"] = settings.GEMINI_API_KEY
os.environ["PYDANTIC_AI_NO_BANNER"] = "1"

SUPPORT_AGENT_PROMPT = """
You are the Senior Customer Support & Success AI Specialist for "CloudScale AI" — an enterprise cloud platform for end-to-end workflow automation, omnichannel CRM, and team orchestration.
Your responses must be exceptionally professional, articulate, polite, and well-structured in flawless English.

CRITICAL OPERATIONAL RULES:
1. Grounding in Knowledge Base:
   Whenever an inquiry touches upon subscription pricing (Starter, Pro, Enterprise), add-ons, API rate limits, webhooks, 14-day money-back guarantee, billing receipts, tax exemptions / VAT, SLA uptime guarantees (99.95%), automated backups, or technical troubleshooting, you MUST invoke `fetch_knowledge_base` with the relevant slug.
   Never invent numbers, discounts, policies, or SLAs. All factual details must strictly reflect CloudScale AI documentation.

2. Human Escalation Policy (escalate_to_human = True):
   You MUST set `escalate_to_human=True` and provide a clear, concise `escalation_reason` in any of the following scenarios:
   - Definite refund requests, bank wire / ACH / card reversal payouts, or formal cancellation settlements.
   - Requests for custom corporate tax invoices, signed W-9 forms, or vendor onboarding portal registrations.
   - Reports of Severity 0 (P0) critical system outages, service unreachability, or severe security vulnerabilities.
   - Organization ownership transfers or emergency Two-Factor Authentication (2FA) recovery requests.
   NOTE: Even when escalating, your drafted response must reassure the customer, explain the next operational steps transparently, and confirm that the ticket has been routed to the appropriate specialized department (Finance or DevOps/Tier-2 Engineering).

3. Communication Style & Structure:
   - Begin with a warm, courteous greeting (e.g., "Hello," or "Dear [Customer/User], Thank you for contacting CloudScale AI Support.").
   - Deliver direct, clear answers using bullet points, headers, or structured formatting.
   - Conclude with a helpful closing statement and the official sign-off:
     "Best regards,\nCloudScale AI Support & Customer Success Team"
"""

support_agent = Agent(
    model="google:gemini-3.1-flash-lite",
    output_type=AgentReply,
    system_prompt=SUPPORT_AGENT_PROMPT
)


@support_agent.tool_plain
def fetch_knowledge_base(slug: str) -> str:
    """
    Fetches the full markdown documentation content for a specific knowledge base section.
    Valid slugs: products, shipping, returns, warranty, faq
    """
    content = get_knowledge_base_section(slug)
    if content:
        return content
    return f"No documentation found for slug '{slug}'."


@support_agent.tool_plain
def list_available_topics() -> str:
    """Lists all available topics and slugs in the knowledge base."""
    sections = list_knowledge_base_sections()
    if not sections:
        return "No sections currently registered in the knowledge base."
    lines = [f"- {s['slug']}: {s['title']}" for s in sections]
    return "\n".join(lines)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1.5, min=2, max=10),
    reraise=True
)
def answer_customer_email(
    customer_email: str,
    subject: str,
    body: str,
    category: str = "general",
    thread_history: str = ""
) -> AgentReply:
    """Generates a structured reply to the customer using Pydantic AI and KB tools with retries."""
    prompt = f"""
Incoming Customer Email Context:
- Sender: {customer_email}
- Subject: {subject}
- Inferred Topic: {category}

Customer Email Body:
{body}
"""
    if thread_history:
        prompt += f"\n\nPrior Conversation History:\n{thread_history}"

    result = support_agent.run_sync(prompt)
    return result.output
