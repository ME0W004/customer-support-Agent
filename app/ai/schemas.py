from typing import Literal
from pydantic import BaseModel, Field

SectionSlug = Literal[
    "products",
    "shipping",
    "returns",
    "warranty",
    "faq",
    "general",
    "irrelevant"
]

CustomerSentiment = Literal[
    "satisfied",
    "neutral",
    "confused",
    "angry",
    "urgent"
]


class Classification(BaseModel):
    """Categorizes the incoming email and evaluates its nature."""
    section: SectionSlug = Field(
        description="The relevant knowledge base section slug that matches the email topic."
    )
    is_support_request: bool = Field(
        description="True if this is a genuine customer inquiry or support request. False for spam, marketing, or automated notices."
    )
    customer_sentiment: CustomerSentiment = Field(
        description="The detected emotional tone of the customer."
    )
    summary: str = Field(
        description="A concise one-line summary in English explaining what the customer is asking."
    )


class AgentReply(BaseModel):
    """Structured response drafted by the support agent."""
    reply_text: str = Field(
        description="The polite, professional English reply to be sent to the customer."
    )
    is_resolved: bool = Field(
        description="True if the customer's question was completely answered using facts in the knowledge base."
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0 regarding the accuracy and completeness of the answer."
    )
    escalate_to_human: bool = Field(
        description="Set to True if the query requires human manual action (e.g. refund payment verification, warehouse check, or angry escalation)."
    )
    escalation_reason: str | None = Field(
        default=None,
        description="Short reason why human escalation is required, if applicable."
    )
