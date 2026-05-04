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
