import argparse
import asyncio
import logging
import sys

from .config import (
    TWITCH_CLIENT_ID,
    TWITCH_CLIENT_SECRET,
    MINIMAX_API_KEY,
    RESEND_API_KEY,
)
from .scraper import TwitchScraper
from .researcher import generate_outreach_email
from .sender import send_email
from .csv_store import is_contacted, mark_contacted


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


async def run(limit: int = 20, test_email: str = None) -> None:
    logger.info(f"Starting outreach run (limit={limit}, test_email={test_email})")

    if test_email:
        logger.info(f"TEST MODE: Generating and sending single email to {test_email}")
        try:
            email = await generate_outreach_email(
                streamer_name="Test Streamer",
                bio="Just a test bio for testing purposes.",
                profile_image_url="",
            )
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            sys.exit(1)

        success = send_email(test_email, email.subject, email.body)
        if success:
            logger.info(f"TEST EMAIL SENT to {test_email}")
        else:
            logger.error(f"TEST EMAIL FAILED to {test_email}")
            sys.exit(1)
        return

    if not TWITCH_CLIENT_ID or not TWITCH_CLIENT_SECRET:
        logger.error("TWITCH_CLIENT_ID or TWITCH_CLIENT_SECRET not set")
        sys.exit(1)
    if not MINIMAX_API_KEY:
        logger.error("MINIMAX_API_KEY not set")
        sys.exit(1)

    scraper = TwitchScraper(TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET)

    logger.info("Fetching top Just Chatting streamers from Twitch...")
    all_streamers = await scraper.get_top_streamers(limit=limit)
    logger.info(f"Fetched {len(all_streamers)} streamers")

    uncontacted = [s for s in all_streamers if not is_contacted(s.twitch_user_id)]
    logger.info(f"{len(uncontacted)} have not been contacted yet")

    sent_count = 0
    skipped_no_email = 0
    failed_count = 0

    for streamer in uncontacted:
        if not streamer.email:
            logger.info(f"[{streamer.display_name}] No email in bio, skipping")
            skipped_no_email += 1
            continue

        logger.info(f"[{streamer.display_name}] Generating personalized email...")
        try:
            email = await generate_outreach_email(
                streamer_name=streamer.display_name,
                bio=streamer.bio,
                profile_image_url=streamer.profile_image_url,
            )
        except Exception as e:
            logger.error(f"[{streamer.display_name}] AI generation failed: {e}")
            failed_count += 1
            continue

        logger.info(f"[{streamer.display_name}] Sending email to {streamer.email}...")
        success = send_email(streamer.email, email.subject, email.body)

        if success:
            mark_contacted(
                twitch_user_id=streamer.twitch_user_id,
                twitch_username=streamer.username,
                email=streamer.email,
                status="sent",
                ai_email_subject=email.subject,
                ai_email_body=email.body,
            )
            sent_count += 1
        else:
            mark_contacted(
                twitch_user_id=streamer.twitch_user_id,
                twitch_username=streamer.username,
                email=streamer.email,
                status="failed",
                ai_email_subject=email.subject,
                ai_email_body=email.body,
            )
            failed_count += 1

        await asyncio.sleep(1)

    logger.info(f"Done. Sent: {sent_count}, Failed: {failed_count}, Skipped (no email): {skipped_no_email}")


def main() -> None:
    parser = argparse.ArgumentParser(description="SyncStream weekly outreach")
    parser.add_argument("--limit", type=int, default=20, help="Max streamers to process")
    parser.add_argument("--test-email", type=str, default=None, help="Send test email to this address instead of running full outreach")
    args = parser.parse_args()
    asyncio.run(run(args.limit, args.test_email))


if __name__ == "__main__":
    main()
