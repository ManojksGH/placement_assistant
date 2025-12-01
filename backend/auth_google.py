# backend/auth_google.py

import os
import pathlib
from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

# simple in-memory store (replace google_state.py)
tokens: dict[str, object] = {}
emails: dict[str, str] = {}

def set_creds(email: str, creds) -> None:
    tokens[email] = creds

def get_creds(email: str):
    return tokens.get(email)

def set_current_email(email: str) -> None:
    emails["current"] = email

def get_current_email() -> str | None:
    return emails.get("current")


# router + oauth config
router = APIRouter()
BASE_DIR = pathlib.Path(__file__).parent
CLIENT_SECRETS_FILE = os.path.join(BASE_DIR, "credentials.json")

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]


def _flow() -> Flow:
    return Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri="http://localhost:8000/google/callback",
    )


@router.get("/login")
def login():
    flow = _flow()
    auth_url, _ = flow.authorization_url(
        prompt="consent",
        access_type="offline",
        include_granted_scopes="true",
    )
    return RedirectResponse(auth_url)


@router.get("/callback")
def callback(code: str):
    flow = _flow()
    flow.fetch_token(code=code)
    creds = flow.credentials

    # get user email
    service = build("gmail", "v1", credentials=creds)
    me = service.users().getProfile(userId="me").execute()
    email = me["emailAddress"]

    # store creds in-memory
    set_creds(email, creds)
    set_current_email(email)

    # avoid circular imports at module load time
    from .data_store import set_auto_process, scan_inbox

    # enable auto process and trigger immediate scan
    set_auto_process(email, True)
    scan_inbox(email)

    # redirect to frontend with email
    return RedirectResponse(f"http://localhost:5173?email={email}")