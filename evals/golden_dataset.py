from dataclasses import dataclass
from typing import Literal

@dataclass
class TestCase:
    id: str
    subject: str
    body: str
    expected_section: str
    expected_action: Literal["reply", "escalate", "skip"]
    expected_is_support: bool


GOLDEN_EMAILS: list[TestCase] = [
    # 1. Product & Plan Inquiries (Starter, Pro, Enterprise)
    TestCase(
        id="case_1_plan_comparison_pro_vs_starter",
        subject="Comparing Starter vs Professional Plan",
        body="Hello, we are a team of 6 engineers evaluating CloudScale AI. Could you clarify the differences in API request rate limits and cloud storage between the Starter and Pro tiers, and whether annual discounts apply?",
        expected_section="products",
        expected_action="reply",
        expected_is_support=True
    ),
    TestCase(
        id="case_2_add_ons_pricing",
        subject="Cost of additional user seats and storage expansion",
        body="Hi there, our team is currently subscribed to the Pro plan. We want to add 4 additional team members and expand our cloud storage by 100 GB. What are the specific monthly add-on rates?",
        expected_section="products",
        expected_action="reply",
        expected_is_support=True
    ),
    
    # 2. Billing & License Provisioning
    TestCase(
        id="case_3_license_provisioning_speed",
        subject="License and API key turnaround after checkout",
        body="Hi team, if our procurement department executes an online credit card payment today for an annual Pro subscription, how quickly will our production API credentials and workspaces be provisioned?",
        expected_section="shipping",
        expected_action="reply",
        expected_is_support=True
    ),
    TestCase(
        id="case_4_corporate_tax_invoice_human_escalation",
        subject="Request for signed W-9 and EU VAT reverse charge invoice #INV-8821",
        body="Hello, our finance department requires a signed W-9 form and a formal reverse-charge VAT invoice for our enterprise purchase of invoice #INV-8821. Our corporate VAT ID is DE312345678. Please have your billing specialist review and submit this.",
        expected_section="shipping",
        expected_action="escalate",
        expected_is_support=True
    ),

    # 3. Refunds & Cancellation
    TestCase(
        id="case_5_14_day_money_back_policy",
        subject="Inquiry regarding 14-day money-back guarantee",
        body="Hi, before we commit to an annual plan, could you confirm whether the 14-day money-back guarantee is 100% unconditional, and how the refund process works if the tool does not fit our workflows?",
        expected_section="returns",
        expected_action="reply",
        expected_is_support=True
    ),
    TestCase(
        id="case_6_refund_payout_human_escalation",
        subject="Formal cancellation and refund payout request for Invoice #INV-5540",
        body="Hello, we purchased the Pro annual subscription 5 days ago (Invoice #INV-5540), but our project was abruptly cancelled. We would like to exercise our 14-day money-back guarantee and request a full refund to our corporate credit card ending in 4242. Please process the reversal.",
        expected_section="returns",
        expected_action="escalate",
        expected_is_support=True
    ),

    # 4. SLA, Uptime & Server Issues
    TestCase(
        id="case_7_uptime_sla_and_backups",
        subject="Enterprise SLA commitment and database backup frequency",
        body="Hello CloudScale team, what is your guaranteed monthly uptime percentage under the Pro SLA, what are the credit remedies if downtime occurs, and how frequently are automated database snapshots taken?",
        expected_section="warranty",
        expected_action="reply",
        expected_is_support=True
    ),
    TestCase(
        id="case_8_critical_server_down_outage",
        subject="URGENT P0: Complete API downtime and 502 Bad Gateway across all production endpoints",
        body="CRITICAL INCIDENT: Our production webhooks and API calls have been failing with 502 Bad Gateway for the past 25 minutes. All automated sync jobs are completely halted. We require immediate on-call DevOps intervention and status escalation under our Enterprise SLA.",
        expected_section="warranty",
        expected_action="escalate",
        expected_is_support=True
    ),

    # 5. Technical FAQ & API
    TestCase(
        id="case_9_api_rate_limit_429",
        subject="Encountering HTTP 429 Too Many Requests on bulk export endpoint",
        body="Hi, our data pipeline started receiving HTTP 429 errors from the CloudScale REST API this morning. What does the Retry-After response header indicate, and how can we upgrade our API throughput quota?",
        expected_section="faq",
        expected_action="reply",
        expected_is_support=True
    ),
    TestCase(
        id="case_10_migration_from_trello_jira",
        subject="Migrating active workspaces from Jira and Trello",
        body="Hello, is there an automated migration wizard available to import active sprint tasks, assignee tags, and comments from Jira and Trello directly into CloudScale AI?",
        expected_section="faq",
        expected_action="reply",
        expected_is_support=True
    ),

    # 6. Negative / Spam / Irrelevant
    TestCase(
        id="case_11_spam_promotional",
        subject="Boost your organic website traffic with AI backlinks - 70% off",
        body="Dear Website Owner, our agency offers guaranteed Top 10 Google search rankings and high-DA backlink packages starting at $99/mo. Click here to claim your discount today.",
        expected_section="irrelevant",
        expected_action="skip",
        expected_is_support=False
    ),
    TestCase(
        id="case_12_furious_customer_escalation",
        subject="UNACCEPTABLE SERVICE: Legal breach notice and management escalation",
        body="I am writing to express our extreme dissatisfaction with the lack of response regarding our enterprise account provisioning. Our entire team has been blocked for two days. If our account is not immediately resolved by executive management within 1 hour, our legal counsel will file for breach of contract and demand full damages.",
        expected_section="general",
        expected_action="escalate",
        expected_is_support=True
    )
]
