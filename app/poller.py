import sys
import time
import logging
from app.config import settings
from app.gmail import GmailClient
from app.pipeline import process_message

# Ensure UTF-8 stdout for console logging on Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("poller")


def run_poller_cycle(client: GmailClient) -> int:
    """Executes a single polling check against Gmail inbox."""
    try:
        messages = client.list_unprocessed_messages(max_results=10)
        if not messages:
            logger.debug("No new unprocessed messages.")
            return 0

        logger.info(f"Found {len(messages)} new message(s) to process.")
        processed_count = 0

        for msg in messages:
            try:
                res = process_message(client, msg)
                logger.info(f"Message {msg['id']} result: {res.get('status')} ({res.get('action', res.get('reason', ''))})")
                processed_count += 1
            except Exception as e:
                logger.error(f"Error handling message {msg.get('id')}: {e}", exc_info=True)

        return processed_count
    except Exception as e:
        logger.error(f"Error during polling cycle: {e}")
        return 0


def main():
    logger.info("=" * 60)
    logger.info("Starting AI Customer Support Gmail Poller Daemon")
    logger.info(f"Monitoring inbox: {settings.SUPPORT_EMAIL}")
    logger.info(f"Poll interval: {settings.POLL_INTERVAL_SECONDS} seconds")
    logger.info("=" * 60)

    try:
        client = GmailClient()
    except Exception as e:
        logger.critical(f"Failed to initialize GmailClient: {e}", exc_info=True)
        sys.exit(1)

    while True:
        run_poller_cycle(client)
        time.sleep(settings.POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
