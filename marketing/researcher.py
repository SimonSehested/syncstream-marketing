import json
import logging

import httpx
from dataclasses import dataclass

from .config import MINIMAX_API_BASE, MINIMAX_API_KEY, MINIMAX_MODEL, EMAIL_PROMPT

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

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{MINIMAX_API_BASE}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {MINIMAX_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MINIMAX_MODEL,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_completion_tokens": 1200,
                "temperature": 0.8,
                "response_format": {"type": "json_object"},
            },
            timeout=120.0,
        )
        resp.raise_for_status()
        data = resp.json()

    content = data["choices"][0]["message"]["content"]
    logger.info(f"MiniMax raw response: {content[:1000]}")
    return _parse_email_response(content, streamer_name, stream_title, game_name)


def _parse_email_response(content: str, streamer_name: str = "there", stream_title: str = "", game_name: str = "") -> GeneratedEmail:
    content = content.strip()

    try:
        parsed = json.loads(content)
        subject = parsed.get("subject", "Let's sync: try SyncStream")
        body = parsed.get("body", "")
    except json.JSONDecodeError:
        subject = "Let's sync: try SyncStream"
        body = ""

    if not body or len(body) < 50:
        personal_detail = stream_title or game_name or "your stream"
        body = f"Hi {streamer_name},\n\nI saw you streaming {personal_detail} and wanted to reach out. I'm building SyncStream, a tool that lets streamers host watchalongs where everyone watches in perfect sync from their own Netflix or Disney+ account.\n\nIt could be a fun thing to try for your community. You can read more at syncstream.app.\n\nChristian at SyncStream"
        subject = "Saw your stream"
    else:
        subject = subject.replace("—", "-").replace("–", "-")

    body = body.replace("—", "-").replace("–", "-")

    nl_double = '\n\n'
    nl_single = '\n'
    body_html = body.replace(nl_double, '</p><p style="margin-bottom: 16px;">').replace(nl_single, '<br>')
    html_body = f"""<html>
<body style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; line-height: 1.6;">
{body_html}
</body>
</html>"""

    return GeneratedEmail(subject=subject, body=html_body)
