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
    prompt = f"""Write a SHORT email (max 150 words) to a Twitch streamer named "{streamer_name}".

Write ONLY the subject line and email body. NOTHING else. No explanations. No thinking. No markdown headers.

Subject line must be max 100 characters.
Email body must be plain HTML with inline CSS only. No external stylesheets.

SUBJECT: <your short subject line here>

<html>
<body style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
<p>Hi {streamer_name},</p>
<p>[Your personal message here - keep it short and friendly]</p>
<p style="text-align: center;">
<a href="https://syncstream.app" style="background: #6366f1; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; display: inline-block;">Try SyncStream for free</a>
</p>
</body>
</html>
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
                "max_completion_tokens": 600,
                "temperature": 0.7,
            },
            timeout=60.0,
        )
        resp.raise_for_status()
        data = resp.json()

    content = data["choices"][0]["message"]["content"]
    return _parse_email_response(content)


def _parse_email_response(content: str) -> GeneratedEmail:
    content = content.strip()

    subject = "Let's sync — try SyncStream for your next watchalong!"
    body = content

    if "SUBJECT:" in content.upper():
        parts = content.split("SUBJECT:", 1)
        if len(parts) > 1:
            after = parts[1]
            lines = after.strip().split("\n")
            subject_line = ""
            html_start = -1
            for i, line in enumerate(lines):
                if "<html" in line.lower():
                    html_start = i
                    break
                if line.strip() and not line.strip().startswith("<") and not line.strip().startswith("-"):
                    subject_line = line.strip()
            if html_start > 0:
                body = "\n".join(lines[html_start:])
                if subject_line:
                    subject = subject_line[:500]
            elif len(lines) > 1:
                body = "\n".join(lines[1:])

    body = body.strip()
    if not body.startswith("<html>"):
        body = f"<html><body style=\"font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;\">{body}</body></html>"

    if not subject:
        subject = "Let's sync — try SyncStream for your next watchalong!"

    return GeneratedEmail(subject=subject, body=body)
