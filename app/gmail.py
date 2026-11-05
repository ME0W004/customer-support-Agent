import base64
import logging
from email.message import EmailMessage
from typing import Any
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from app.config import settings

logger = logging.getLogger(__name__)

PROCESSED_LABEL = "ai-processed"


class GmailClient:
    def __init__(self) -> None:
        self.creds = Credentials(
            token=None,
            refresh_token=settings.GMAIL_REFRESH_TOKEN,
            client_id=settings.GMAIL_CLIENT_ID,
            client_secret=settings.GMAIL_CLIENT_SECRET,
            token_uri="https://oauth2.googleapis.com/token"
        )
        self.service = build("gmail", "v1", credentials=self.creds)
        self.label_id = self.ensure_label_exists(PROCESSED_LABEL)

    def ensure_label_exists(self, label_name: str) -> str:
        """Finds or creates a Gmail user label and returns its ID."""
        labels_resp = self.service.users().labels().list(userId="me").execute()
        labels = labels_resp.get("labels", [])
        for lbl in labels:
            if lbl["name"].lower() == label_name.lower():
                return lbl["id"]

        # Create the label if not found
        created = self.service.users().labels().create(
            userId="me",
            body={
                "name": label_name,
                "labelListVisibility": "labelShow",
                "messageListVisibility": "show"
            }
        ).execute()
        logger.info(f"Created Gmail label '{label_name}' with ID: {created['id']}")
        return created["id"]

    def list_unprocessed_messages(self, max_results: int = 10) -> list[dict[str, str]]:
        """Lists new incoming messages in INBOX that don't have the processed label."""
        query = f"label:INBOX -label:{PROCESSED_LABEL}"
        res = self.service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
        return res.get("messages", [])

    def get_message(self, message_id: str) -> dict[str, Any]:
        """Fetches full message details by ID."""
        return self.service.users().messages().get(userId="me", id=message_id, format="full").execute()

    def get_thread(self, thread_id: str) -> dict[str, Any]:
        """Fetches full thread history."""
        return self.service.users().threads().get(userId="me", id=thread_id, format="full").execute()

    def mark_as_processed(self, message_id: str) -> None:
        """Adds ai-processed label and removes UNREAD."""
        self.service.users().messages().modify(
            userId="me",
            id=message_id,
            body={
                "addLabelIds": [self.label_id],
                "removeLabelIds": ["UNREAD"]
            }
        ).execute()

    def send_reply(
        self,
        thread_id: str,
        in_reply_to_header: str,
        to_email: str,
        subject: str,
        body_text: str
    ) -> dict[str, Any]:
        """Sends an email reply inside the same conversation thread."""
        msg = EmailMessage()
        msg["To"] = to_email
        msg["From"] = settings.SUPPORT_EMAIL
        
        reply_subject = subject if subject.lower().startswith("re:") else f"Re: {subject}"
        msg["Subject"] = reply_subject
        
        if in_reply_to_header:
            msg["In-Reply-To"] = in_reply_to_header
            msg["References"] = in_reply_to_header

        msg.set_content(body_text, subtype="plain", charset="utf-8")

        raw_bytes = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
        
        sent = self.service.users().messages().send(
            userId="me",
            body={
                "raw": raw_bytes,
                "threadId": thread_id
            }
        ).execute()
        logger.info(f"Sent reply to {to_email} (Thread ID: {thread_id}, Message ID: {sent['id']})")
        return sent


def parse_headers(message: dict[str, Any]) -> dict[str, str]:
    """Extracts key headers into a normalized dictionary."""
    headers_dict = {}
    payload = message.get("payload", {})
    headers = payload.get("headers", [])
    for h in headers:
        headers_dict[h["name"].lower()] = h["value"]
    return headers_dict


def parse_body(message: dict[str, Any]) -> str:
    """Recursively decodes the message body text."""
    payload = message.get("payload", {})

    def extract_from_part(part: dict[str, Any]) -> str:
        mime_type = part.get("mimeType", "")
        body_data = part.get("body", {}).get("data")

        if mime_type == "text/plain" and body_data:
            try:
                decoded = base64.urlsafe_b64decode(body_data).decode("utf-8", errors="replace")
                return decoded
            except Exception:
                pass

        if "parts" in part:
            for subpart in part["parts"]:
                txt = extract_from_part(subpart)
                if txt:
                    return txt

        # Fallback to text/html if plain text not available
        if mime_type == "text/html" and body_data:
            try:
                decoded = base64.urlsafe_b64decode(body_data).decode("utf-8", errors="replace")
                return decoded
            except Exception:
                pass

        return ""

    text = extract_from_part(payload)
    if not text and payload.get("body", {}).get("data"):
        try:
            text = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")
        except Exception:
            pass

    return text.strip()
