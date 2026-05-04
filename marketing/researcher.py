import json
import logging

import anthropic
from dataclasses import dataclass

from .config import MINIMAX_API_KEY, MINIMAX_MODEL, EMAIL_PROMPT

logger = logging.getLogger(__name__)


@dataclass
class GeneratedEmail:
    subject: str
    body: str


async def generate_outreach_email(
    streamer_name: str,
    bio: str,
    stream_title: str = "",
    game_name: str = "",
    tags: list[str] = None,
) -> GeneratedEmail:
    if tags is None:
        tags = []
    prompt = EMAIL_PROMPT.format(
        streamer_name=streamer_name,
        bio=bio or "No bio available",
        stream_title=stream_title or "No stream title available",
        game_name=game_name or "Unknown",
        tags=", ".join(tags) if tags else "none",
    )

    client = anthropic.Anthropic(
        base_url="https://api.minimax.io/anthropic",
        api_key=MINIMAX_API_KEY,
    )

    message = client.messages.create(
        model=MINIMAX_MODEL,
        max_tokens=2048,
        system="You are a helpful assistant. Do NOT use any thinking tags like <think> or </thinking>. Do NOT reason out loud. Output ONLY valid JSON directly.",
        messages=[
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }
        ]
    )

    text_content = ""
    for block in message.content:
        if block.type == "text":
            text_content = block.text
            break

    logger.info(f"MiniMax text response length: {len(text_content)}")
    return _parse_email_response(text_content, streamer_name, stream_title, game_name)


def _parse_email_response(content: str, streamer_name: str = "there", stream_title: str = "", game_name: str = "") -> GeneratedEmail:
    import re
    content = str(content).strip()
    
    subject = "Let's sync: try SyncStream"
    body = ""

    try:
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            subject = str(parsed.get("subject", subject))
            body = str(parsed.get("body", ""))
        elif isinstance(parsed, str):
            inner = json.loads(parsed)
            if isinstance(inner, dict):
                subject = str(inner.get("subject", subject))
                body = str(inner.get("body", ""))
    except (json.JSONDecodeError, KeyError, TypeError, AttributeError):
        pass

    if not body or len(body) < 50:
        personal_detail = stream_title or game_name or "your stream"
        body = f"Hi {streamer_name},\n\nI saw you streaming {personal_detail} and wanted to reach out. I'm building SyncStream, a tool that lets streamers host watchalongs where everyone watches in perfect sync from their own Netflix or Disney+ account.\n\nIt could be a fun thing to try for your community. You can read more at syncstream.app.\n\nChristian at SyncStream"
        subject = "Saw your stream"
    else:
        subject = subject.replace("\u2014", "-").replace("\u2013", "-")

    body = body.replace("\u2014", "-").replace("\u2013", "-")

    nl_double = '\n\n'
    nl_single = '\n'
    body_html = body.replace(nl_double, '</p><p style="margin-bottom: 16px;">').replace(nl_single, '<br>')
    html_body = f"""<html>
<body style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; line-height: 1.6;">
{body_html}
</body>
</html>"""

    return GeneratedEmail(subject=subject, body=html_body)