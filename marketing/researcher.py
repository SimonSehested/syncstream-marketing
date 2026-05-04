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
        logger.info(f"API response data keys: {list(data.keys())}")
        logger.info(f"Choices[0] keys: {list(data.get('choices', [{}])[0].keys()) if data.get('choices') else 'no choices'}")
        
    content = data["choices"][0]["message"]["content"]
    logger.info(f"MiniMax raw response type: {type(content)}, content: {str(content)[:500]}")
    if isinstance(content, dict):
        logger.info(f"Content is dict, keys: {list(content.keys())}")
    return _parse_email_response(content, streamer_name, stream_title, game_name)


def _parse_email_response(content: str, streamer_name: str = "there", stream_title: str = "", game_name: str = "") -> GeneratedEmail:
    if isinstance(content, dict):
        content = json.dumps(content)
    
    content = str(content).strip()
    logger.info(f"Parsing content: {content[:500]}")

    subject = "Let's sync: try SyncStream"
    body = ""

    try:
        parsed = json.loads(content)
        logger.info(f"Parsed type: {type(parsed)}, content repr: {repr(parsed)[:200]}")
        
        if isinstance(parsed, dict):
            logger.info(f"Dict keys: {list(parsed.keys())}")
            try:
                subject = str(parsed["subject"])
            except KeyError:
                try:
                    subject = str(parsed['"subject"'])
                except KeyError:
                    subject = "Let's sync: try SyncStream"
            try:
                body = str(parsed["body"])
            except KeyError:
                try:
                    body = str(parsed['"body"'])
                except KeyError:
                    body = ""
        elif isinstance(parsed, str):
            logger.info(f"Parsed is string, re-parsing: {parsed[:200]}")
            inner = json.loads(parsed)
            logger.info(f"Inner dict keys: {list(inner.keys())}")
            subject = str(inner.get("subject", subject))
            body = str(inner.get("body", ""))
        else:
            logger.info(f"Parsed type not handled: {type(parsed)}, trying line-by-line")
            raise json.JSONDecodeError("Not a dict or str", content, 0)
            
    except (json.JSONDecodeError, KeyError, TypeError, AttributeError) as e:
        logger.info(f"Parse failed: {type(e).__name__}: {e}, trying line-by-line")
        lines = content.split("\n")
        body_lines = []
        in_body = False
        for line in lines:
            upper = line.upper().strip()
            if upper.startswith("SUBJECT:"):
                subject = line[len("SUBJECT:"):].strip()
                continue
            if "DEAR " in upper or upper.startswith("DEAR"):
                in_body = True
            if in_body:
                body_lines.append(line)
        body = "\n".join(body_lines).strip()

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
