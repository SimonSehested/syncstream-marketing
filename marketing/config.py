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

EMAIL_PROMPT = os.getenv("EMAIL_PROMPT", """Write a personal email to a Twitch streamer.

CRITICAL STYLE RULES (non-negotiable):
- NEVER use em dashes (—) or en dashes (–) under any circumstances. Not for emphasis, not for breaks, not for anything.
- If you need to separate clauses, use commas, semicolons, or periods. Rewrite the sentence if you must.
- Use only standard hyphens (-) for compound words like "well-being" or "first-time".
- Use active voice.
- Never start a sentence with "Ah the old".
- Be direct and concise. Avoid flowery language.
- Do not use contrastive constructions like "This isn't X, it's Y".
- Do not use value judgments like "great", "amazing", "love" as generic praise.
- Write like a thoughtful person who happens to be reaching out — not a marketer.

WHAT YOU KNOW ABOUT THE STREAMER (use this to personalize):
- Stream title: {stream_title}
- Game: {game_name}
- Stream tags: {tags}
- Bio: {bio}

REQUIREMENTS:
- You MUST reference something specific from the stream title, game, tags, or bio. Always. Do not write generic emails.
- Pick ONE thing from their context and weave it into the email naturally. Example: if they're playing a specific game, reference that game specifically.
- Plain text only (no HTML, no formatting).
- Subject line: max 60 characters.
- Sign from "Christian at SyncStream".
- Mention what SyncStream does in one sentence (sync watchalongs so viewers watch in perfect sync from their own Netflix/Disney+/HBO).
- End with a casual call-to-action.
- Include syncstream.app as plain text at the end.
- Write enough to feel personal and complete — not a bullet list, not a greeting card. A real email.

Output a JSON object with exactly two fields: "subject" and "body". The body must start with "Dear {streamer_name}," and end with "Christian at SyncStream". Output NOTHING else — no explanation, no reasoning, no thinking, just the JSON.""")
