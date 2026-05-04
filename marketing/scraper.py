import re
import httpx
import asyncio
from dataclasses import dataclass
from typing import Optional

from .config import (
    TWITCH_CLIENT_ID,
    TWITCH_CLIENT_SECRET,
    TWITCH_OAUTH_TOKEN_URL,
    TWITCH_API_BASE,
    TWITCH_JUST_CHATTING_GAME_ID,
)


EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")


@dataclass
class Streamer:
    twitch_user_id: str
    username: str
    display_name: str
    bio: str
    profile_image_url: str
    email: Optional[str]


class TwitchScraper:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token: Optional[str] = None

    async def _get_access_token(self) -> str:
        if self._access_token:
            return self._access_token
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                TWITCH_OAUTH_TOKEN_URL,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "client_credentials",
                },
            )
            resp.raise_for_status()
            self._access_token = resp.json()["access_token"]
        return self._access_token

    async def _get_headers(self) -> dict:
        token = await self._get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Client-Id": self.client_id,
        }

    async def get_top_streamers(self, limit: int = 100) -> list[Streamer]:
        async with httpx.AsyncClient() as client:
            headers = await self._get_headers()
            all_streamers: list[Streamer] = []
            cursor: Optional[str] = None

            while len(all_streamers) < limit:
                params = {
                    "game_id": TWITCH_JUST_CHATTING_GAME_ID,
                    "first": min(100, limit - len(all_streamers)),
                    "after": cursor,
                }
                resp = await client.get(
                    f"{TWITCH_API_BASE}/streams",
                    headers=headers,
                    params=params,
                )
                resp.raise_for_status()
                data = resp.json()

                user_ids = [s["user_id"] for s in data.get("data", [])]
                if not user_ids:
                    break

                user_details = await self._get_user_details(client, headers, user_ids)

                for stream in data.get("data", []):
                    user_info = user_details.get(stream["user_id"], {})
                    bio = user_info.get("description", "")
                    email = self._extract_email(bio)

                    all_streamers.append(Streamer(
                        twitch_user_id=stream["user_id"],
                        username=stream["user_login"],
                        display_name=stream["user_name"],
                        bio=bio,
                        profile_image_url=user_info.get("profile_image_url", ""),
                        email=email,
                    ))

                cursor = data.get("pagination", {}).get("cursor")
                if not cursor:
                    break

                await asyncio.sleep(1)

        return all_streamers

    async def _get_user_details(
        self, client: httpx.AsyncClient, headers: dict, user_ids: list[str]
    ) -> dict:
        resp = await client.get(
            f"{TWITCH_API_BASE}/users",
            headers=headers,
            params=[("id", uid) for uid in user_ids],
        )
        resp.raise_for_status()
        data = resp.json()
        return {u["id"]: u for u in data.get("data", [])}

    def _extract_email(self, text: str) -> Optional[str]:
        match = EMAIL_REGEX.search(text)
        return match.group(0) if match else None
