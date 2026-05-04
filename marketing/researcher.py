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
- Output ONLY the email — nothing else

Output format:
SUBJECT: <subject line>

Dear {streamer_name},

<email body>"""

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
            },
            timeout=60.0,
        )
        resp.raise_for_status()
        data = resp.json()

    content = data["choices"][0]["message"]["content"]
    return _parse_email_response(content)


def _parse_email_response(content: str) -> GeneratedEmail:
    content = content.strip()

    lines = content.split("\n")
    subject = "Let's sync — try SyncStream!"
    body_lines = []
    in_email = False

    for i, line in enumerate(lines):
        upper = line.upper().strip()

        if upper.startswith("SUBJECT:") and i < 3:
            subject = line[len("SUBJECT:"):].strip()[:100]
            continue

        if line.strip().startswith("Dear"):
            in_email = True

        if in_email:
            body_lines.append(line)

        garbage_starts = [
            "let me count",
            "actually wait",
            "actually re-reading",
            "this looks good",
            "word count",
            "subject line",
            "under 100",
            "under 60",
            "good under",
            "that's ",
            "you should",
            "re-reading",
            "<system",
        ]
        lower_line = line.lower().strip()
        if any(lower_line.startswith(g) for g in garbage_starts):
            body_lines = body_lines[:-1]
            break

    body = "\n".join(body_lines).strip()

    if not body or len(body) < 20:
        body = "Hi [Name],\n\nI love your stream and the community you've built. I've been working on a tool called SyncStream that I think you'd really like — it lets you host watchalongs where everyone watches in perfect sync from their own Netflix or Disney+ account.\n\nWould love for you to try it out for your next watchalong!\n\nChristian at SyncStream"

    if "Dear [Name]" in body or "Dear Test Streamer" in body:
        body = body.replace("Dear [Name]", "Hi there").replace("Dear Test Streamer", "Hi there")

    nl_double = '\n\n'
    nl_single = '\n'
    body_html = body.replace(nl_double, '</p><p style="margin-bottom: 16px;">').replace(nl_single, '<br>')
    html_body = f"""<html>
<body style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; line-height: 1.6;">
{body_html}
</body>
</html>"""

    return GeneratedEmail(subject=subject, body=html_body)
