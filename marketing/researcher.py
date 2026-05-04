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
    prompt = f"""You are a Danish marketing assistant for SyncStream — a tool that lets streamers host synchronized watchalongs with their viewers, so everyone watches in perfect sync from their own Netflix, Disney+, or HBO account.

Write a short, personal email to this Twitch streamer:
- Display name: {streamer_name}
- Bio: {bio}

The email should:
1. Be friendly and personal (not generic)
2. Briefly explain what SyncStream does
3. Have a clear CTA to try SyncStream for free
4. Be in English (the streamer writes in English based on their bio)
5. Be maximum 200 words
6. Include a compelling subject line

Format your response EXACTLY like this (nothing else):
SUBJECT: <subject line>
---
BODY: <HTML email body — use simple inline CSS styling, no external stylesheets>
"""

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
                "max_completion_tokens": 800,
                "temperature": 0.8,
            },
            timeout=60.0,
        )
        resp.raise_for_status()
        data = resp.json()

    content = data["choices"][0]["message"]["content"]
    return _parse_email_response(content)


def _parse_email_response(content: str) -> GeneratedEmail:
    subject = ""
    body = ""

    if "SUBJECT:" in content:
        parts = content.split("SUBJECT:", 1)
        after_subject = parts[1]
        if "BODY:" in after_subject:
            subject_part, body_part = after_subject.split("BODY:", 1)
        else:
            subject_part = after_subject
            body_part = ""
        subject = subject_part.strip()
        body = body_part.strip()
    else:
        body = content.strip()

    if not body and not subject:
        raise ValueError(f"Could not parse email response: {content!r}")

    return GeneratedEmail(subject=subject, body=body)
