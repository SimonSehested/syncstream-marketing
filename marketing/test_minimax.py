import httpx
import asyncio
import os
import json
import re

MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY")
MINIMAX_API_BASE = "https://api.minimax.io"
MINIMAX_MODEL = "MiniMax-M2.7"

STREAMER_NAME = "TestStreamer"
BIO = "Just a test bio for testing purposes."
STREAM_TITLE = "Testing the system with a fake stream title"
GAME_NAME = "Just Chatting"
TAGS = "English, Community"

PROMPT = f"""Write a personal email to a Twitch streamer.

CRITICAL: Never use em dashes or en dashes. Use commas, semicolons, or periods instead. Standard hyphens (-) are fine for compound words only.

TONE: Be direct. Write like a thoughtful person reaching out, not a marketer.

STREAMER CONTEXT:
- Stream title: {STREAM_TITLE}
- Game: {GAME_NAME}
- Tags: {TAGS}
- Bio: {BIO}

REQUIREMENTS:
- Reference something specific from the stream title, game, tags, or bio. Pick ONE thing and weave it in naturally.
- Plain text only.
- Subject line: max 60 characters.
- Sign from "Christian at SyncStream".
- Mention SyncStream: sync watchalongs so viewers watch in perfect sync from their own Netflix/Disney+/HBO.
- End with a casual CTA and include syncstream.app as plain text.

OUTPUT FORMAT: Output ONLY valid JSON like this:
{{"subject": "Your subject line", "body": "Dear {STREAMER_NAME},\n\nEmail body here...\n\nChristian at SyncStream"}}

Do not write anything else. Just output the JSON."""

async def main():
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
                    {"role": "system", "content": "You are a helpful assistant. Do NOT use any thinking tags like <think> or </thinking>. Do NOT reason out loud. Output ONLY valid JSON directly."},
                    {"role": "user", "content": PROMPT}
                ],
                "max_completion_tokens": 1200,
                "temperature": 0.8,
            },
            timeout=120.0,
        )
        resp.raise_for_status()
        data = resp.json()

    content = data["choices"][0]["message"]["content"]

    print("=" * 80)
    print("MINIMAX RAW OUTPUT:")
    print("=" * 80)
    print(content)
    print("=" * 80)
    print(f"Response length: {len(content)} characters")
    print("=" * 80)

    print("\nTrying to extract JSON...")

    try:
        parsed = json.loads(content)
        print(f"Direct JSON parse SUCCESS: {parsed}")
        return
    except json.JSONDecodeError as e:
        print(f"Direct JSON parse FAILED: {e}")

    stripped = re.sub(r'<think>.*?</thinking>', '', content, flags=re.DOTALL)
    stripped = stripped.strip()
    print(f"\nAfter stripping thinking tags, length: {len(stripped)}")
    print(f"First 500 chars: {stripped[:500]}")

    try:
        parsed = json.loads(stripped)
        print(f"JSON parse after stripping thinking tags SUCCESS: {parsed}")
        return
    except json.JSONDecodeError as e:
        print(f"JSON parse after stripping thinking tags FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(main())