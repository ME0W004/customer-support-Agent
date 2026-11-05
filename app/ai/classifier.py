import os
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from pydantic_ai import Agent
from app.config import settings
from app.ai.schemas import Classification

logger = logging.getLogger(__name__)

os.environ["GEMINI_API_KEY"] = settings.GEMINI_API_KEY
os.environ["PYDANTIC_AI_NO_BANNER"] = "1"

CLASSIFIER_SYSTEM_PROMPT = """
You are an intelligent email triage and intent classifier for the enterprise SaaS platform "CloudScale AI".
Your responsibility is to analyze incoming customer support emails and extract structured metadata:

1. section: The most relevant knowledge base section slug:
   - products: Inquiries about subscription tiers (Starter, Pro, Enterprise), pricing, features, API quotas, CRM capabilities, and add-ons.
   - shipping: Digital license provisioning, automated billing cycles, payment methods, tax invoices, VAT exemption, and receipts.
   - returns: Refund requests, 14-day money-back guarantee, cancellation policies, and annual prorated settlements.
   - warranty: Service Level Agreements (SLA), 99.95% uptime commitment, automated 6-hour backups, security architecture, and incident response.
   - faq: Developer troubleshooting, API keys, HTTP 429 rate limits, webhooks, workspace migration (Jira/Trello/Asana), RBAC roles, and 2FA recovery.
   - general: Legitimate support inquiries that do not map specifically to one of the 5 dedicated sections.
   - irrelevant: Spam, SEO solicitations, promotional marketing, meaningless test messages, or automated noise.

2. is_support_request:
   Set to true if this is an authentic inquiry or support request from a human user. False for spam, automated newsletters, or bot bounces.

3. customer_sentiment:
   The emotional tone of the sender: satisfied, neutral, confused, angry, or urgent.

4. summary:
   A concise, one-sentence English summary describing the customer's core intent or problem.
"""

classifier_agent = Agent(
    model="google:gemini-3.1-flash-lite",
    output_type=Classification,
    system_prompt=CLASSIFIER_SYSTEM_PROMPT
)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1.5, min=2, max=10),
    reraise=True
)
def classify_email(subject: str, body: str) -> Classification:
    """Classifies an incoming customer email with automatic retry on temporary errors."""
    user_prompt = f"Subject: {subject}\n\nEmail Body:\n{body}"
    result = classifier_agent.run_sync(user_prompt)
    return result.output
