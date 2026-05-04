import httpx
from dataclasses import dataclass

from .config import MINIMAX_API_BASE, MINIMAX_API_KEY, MINIMAX_MODEL


@dataclass
class GeneratedEmail:
    subject: str
    body: str


async def generate_outreach_email(
    streamer_name: str,
    bio: str,
    profile_image_url: str,
) -> GeneratedEmail:
    prompt = f"""Write a short, personal email to a Twitch streamer.

Keep it casual and friendly — like a fan reaching out, not a company selling something.

Rules:
- Max 100 words
- Plain text only (no HTML, no formatting, no checklists, no self-checks, no word counts)
- Subject line: max 60 characters
- Sign it from "Christian at SyncStream"
- Mention what SyncStream does briefly (sync watchalongs so viewers watch in perfect sync from their own Netflix/Disney+/HBO)
- End with a casual CTA to try it

Output a JSON object with exactly two fields: "subject" and "body". The body field must contain the complete email starting with "Dear {streamer_name}," and ending with the signature "Christian at SyncStream". Output NOTHING else — no explanation, no reasoning, no thinking, just the JSON."""

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
                "max_completion_tokens": 400,
                "temperature": 0.8,
                "response_format": {"type": "json_object"},
            },
            timeout=60.0,
        )
        resp.raise_for_status()
        data = resp.json()

    content = data["choices"][0]["message"]["content"]
    return _parse_email_response(content, streamer_name)


def _parse_email_response(content: str, streamer_name: str = "there") -> GeneratedEmail:
    import json

    content = content.strip()

    try:
        parsed = json.loads(content)
        subject = parsed.get("subject", "Let's sync — try SyncStream!")
        body = parsed.get("body", "")
    except json.JSONDecodeError:
        subject = "Let's sync — try SyncStream!"
        body = ""

    if not body or len(body) < 20:
        body = f"Hi {streamer_name},\n\nI love your stream and the community you've built. I've been working on a tool called SyncStream that I think you'd really like — it lets you host watchalongs where everyone watches in perfect sync from their own Netflix or Disney+ account.\n\nWould love for you to try it out for your next watchalong!\n\nChristian at SyncStream"
        subject = "Let's sync — try SyncStream!"

    nl_double = '\n\n'
    nl_single = '\n'
    body_html = body.replace(nl_double, '</p><p style="margin-bottom: 16px;">').replace(nl_single, '<br>')
    html_body = f"""<html>
<body style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; line-height: 1.6;">
{body_html}
</body>
</html>"""

    return GeneratedEmail(subject=subject, body=html_body)
