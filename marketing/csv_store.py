import csv
import os
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional


CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "contacted_streamers.csv")


@dataclass
class ContactedStreamer:
    twitch_user_id: str
    twitch_username: str
    email: Optional[str]
    contacted_at: str
    status: str
    ai_email_subject: str
    ai_email_body: str


def _get_row_dict(row: ContactedStreamer) -> dict:
    return {
        "twitch_user_id": row.twitch_user_id,
        "twitch_username": row.twitch_username,
        "email": row.email or "",
        "contacted_at": row.contacted_at,
        "status": row.status,
        "ai_email_subject": row.ai_email_subject,
        "ai_email_body": row.ai_email_body,
    }


def load_csv() -> list[ContactedStreamer]:
    csv_path = CSV_PATH
    if not os.path.exists(csv_path):
        return []
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(ContactedStreamer(
                twitch_user_id=row["twitch_user_id"],
                twitch_username=row["twitch_username"],
                email=row["email"] or None,
                contacted_at=row["contacted_at"],
                status=row["status"],
                ai_email_subject=row["ai_email_subject"],
                ai_email_body=row["ai_email_body"],
            ))
    return rows


def save_csv(rows: list[ContactedStreamer]) -> None:
    csv_path = CSV_PATH
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    fieldnames = [
        "twitch_user_id",
        "twitch_username",
        "email",
        "contacted_at",
        "status",
        "ai_email_subject",
        "ai_email_body",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(_get_row_dict(row))


def is_contacted(twitch_user_id: str) -> bool:
    rows = load_csv()
    for row in rows:
        if row.twitch_user_id == twitch_user_id and row.status in ("sent", "pending"):
            return True
    return False


def mark_contacted(
    twitch_user_id: str,
    twitch_username: str,
    email: Optional[str],
    status: str,
    ai_email_subject: str,
    ai_email_body: str,
) -> None:
    rows = load_csv()
    now = datetime.now(timezone.utc).isoformat()
    rows.append(ContactedStreamer(
        twitch_user_id=twitch_user_id,
        twitch_username=twitch_username,
        email=email,
        contacted_at=now,
        status=status,
        ai_email_subject=ai_email_subject,
        ai_email_body=ai_email_body,
    ))
    save_csv(rows)
