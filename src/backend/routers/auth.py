import os
import secrets
import hashlib
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from authlib.integrations.httpx_client import AsyncOAuth2Client

router = APIRouter(prefix="/auth", tags=["auth"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
ALLOWED_EMAIL = os.getenv("ALLOWED_EMAIL")
FRONTEND_URL = os.getenv("FRONTEND_URL")


@router.get("/google")
async def google_login():
    async with AsyncOAuth2Client(
        client_id=GOOGLE_CLIENT_ID,
        redirect_uri=GOOGLE_REDIRECT_URI,
        scope="openid email profile",
    ) as client:
        uri, state = client.create_authorization_url(
            "https://accounts.google.com/o/oauth2/v2/auth",
            access_type="offline",
        )
    return RedirectResponse(uri)


@router.get("/callback")
async def google_callback(request: Request, code: str, state: str):
    async with AsyncOAuth2Client(
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        redirect_uri=GOOGLE_REDIRECT_URI,
    ) as client:
        token = await client.fetch_token(
            "https://oauth2.googleapis.com/token",
            code=code,
        )
        userinfo = await client.get("https://www.googleapis.com/oauth2/v3/userinfo")
        userinfo = userinfo.json()

    if userinfo.get("email") != ALLOWED_EMAIL:
        raise HTTPException(status_code=403, detail="Unauthorized email")

    raw_token = secrets.token_hex(64)
    token_hash = hashlib.sha512(raw_token.encode()).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=6)

    supabase = request.app.state.supabase
    supabase.table("sessions").insert({
        "token_hash": token_hash,
        "expires_at": expires_at.isoformat(),
    }).execute()

    response = RedirectResponse(f"{FRONTEND_URL}/dashboard")
    response.set_cookie(
        key="session_token",
        value=raw_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 6,
    )
    return response


@router.get("/verify")
async def verify_session(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")

    if not token:
        raise HTTPException(status_code=401, detail="No token")

    token_hash = hashlib.sha512(token.encode()).hexdigest()
    now = datetime.now(timezone.utc).isoformat()

    supabase = request.app.state.supabase
    result = supabase.table("sessions").select("*").eq(
        "token_hash", token_hash
    ).gt("expires_at", now).execute()

    if not result.data:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return {"valid": True}