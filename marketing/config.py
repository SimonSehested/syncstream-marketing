import os


TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID", "")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET", "")
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
RESEND_FROM_EMAIL = "SyncStream <christian@syncstream.app>"
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://syncstream.app")

TWITCH_OAUTH_TOKEN_URL = "https://id.twitch.tv/oauth2/token"
TWITCH_API_BASE = "https://api.twitch.tv/helix"
TWITCH_JUST_CHATTING_GAME_ID = "509670"

MINIMAX_API_BASE = "https://api.minimax.io"
MINIMAX_MODEL = "MiniMax-M2.7"

EMAIL_PROMPT = os.getenv("EMAIL_PROMPT", """Write a short, personal email to a Twitch streamer.

Keep it casual and friendly — like a fan reaching out, not a company selling something.

Rules:
- Max 100 words
- Plain text only (no HTML, no formatting, no checklists, no self-checks, no word counts)
- Subject line: max 60 characters
- Sign it from "Christian at SyncStream"
- Mention what SyncStream does briefly (sync watchalongs so viewers watch in perfect sync from their own Netflix/Disney+/HBO)
- End with a casual CTA to try it

Output a JSON object with exactly two fields: "subject" and "body". The body field must contain the complete email starting with "Dear {streamer_name}," and ending with the signature "Christian at SyncStream". Output NOTHING else — no explanation, no reasoning, no thinking, just the JSON.""")
