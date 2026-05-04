import anthropic
import os

MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY")

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
{{"subject": "Your subject line", "body": "Dear {STREAMER_NAME},\\n\\nEmail body here...\\n\\nChristian at SyncStream"}}

Do not write anything else. Just output the JSON."""

def main():
    client = anthropic.Anthropic(
        base_url="https://api.minimax.io/anthropic",
        api_key=MINIMAX_API_KEY,
    )

    message = client.messages.create(
        model="MiniMax-M2.7",
        max_tokens=1200,
        system="You are a helpful assistant. Output ONLY valid JSON.",
        messages=[
            {
                "role": "user",
                "content": [{"type": "text", "text": PROMPT}]
            }
        ]
    )

    with open("marketing/minimax_raw_output.txt", "w", encoding="utf-8") as f:
        for block in message.content:
            if block.type == "thinking":
                f.write(f"=== THINKING BLOCK ===\n{block.thinking}\n")
            elif block.type == "text":
                f.write(f"=== TEXT BLOCK ===\n{block.text}\n")

    print("Done. Check marketing/minimax_raw_output.txt")

if __name__ == "__main__":
    main()