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
            },
            timeout=120.0,
        )
        resp.raise_for_status()
        data = resp.json()

    logger.info(f"Full API response type: {type(data)}, keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
    
    if not isinstance(data, dict):
        logger.error(f"API response is not a dict: {type(data)}, value: {str(data)[:500]}")
        raise TypeError(f"API response is {type(data)}, expected dict")
    
    choices = data.get("choices", [])
    logger.info(f"Choices count: {len(choices)}")
    
    if not choices:
        logger.error(f"No choices in API response")
        raise ValueError("No choices in API response")
    
    message = choices[0].get("message", {})
    logger.info(f"Message type: {type(message)}, keys: {list(message.keys()) if isinstance(message, dict) else 'N/A'}")
    
    content = message.get("content", "")
    logger.info(f"Content type: {type(content)}, preview: {str(content)[:200]}")
    return _parse_email_response(content, streamer_name, stream_title, game_name)


def _parse_email_response(content: str, streamer_name: str = "there", stream_title: str = "", game_name: str = "") -> GeneratedEmail:
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