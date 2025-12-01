# backend/utils.py
from googleapiclient.discovery import build
from .auth_google import get_creds
from typing import Optional
from datetime import datetime

def create_calendar_event(
    email: str,
    title: str,
    start_iso: str,
    end_iso: str,
    venue: Optional[str] = None
):
    creds = get_creds(email)
    if not creds:
        raise RuntimeError("No credentials")

    service = build("calendar", "v3", credentials=creds)

    event = {
        "summary": title,
        "location": venue or "",
        "description": "Added automatically by AI Placement Assistant",
        "start": {
            "dateTime": start_iso,
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            "dateTime": end_iso,
            "timeZone": "Asia/Kolkata",
        },
    }

    # 🔥 DEBUG LINE (added exactly as requested)
    print("[DEBUG-EVENT]", title, start_iso, end_iso, venue)

    created = service.events().insert(
        calendarId="primary",
        body=event
    ).execute()

    return {
        "id": created.get("id"),
        "link": created.get("htmlLink"),
    }