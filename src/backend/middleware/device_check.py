import os
import hashlib
import secrets
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

TAILSCALE_SUBNET_PREFIX = "100."
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")
ALLOWED_EMAIL = os.getenv("ALLOWED_EMAIL")
FRONTEND_URL = os.getenv("FRONTEND_URL")

BYPASS_PATHS = {"/health", "/auth/google", "/auth/callback", "/auth/approve"}


class DeviceCheckMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if any(path.startswith(p) for p in BYPASS_PATHS):
            return await call_next(request)

        ip = request.client.host
        user_agent = request.headers.get("user-agent", "")

        if not ip.startswith(TAILSCALE_SUBNET_PREFIX):
            return JSONResponse(status_code=403, content={"detail": "Forbidden"})

        supabase = request.app.state.supabase

        device_token = request.cookies.get("device_token")

        if device_token:
            device_token_hash = hashlib.sha512(device_token.encode()).hexdigest()
            now = datetime.now(timezone.utc).isoformat()

            result = supabase.table("trusted_devices").select("*").eq(
                "ip", ip
            ).eq(
                "user_agent", user_agent
            ).eq(
                "device_key_hash", device_token_hash
            ).gt(
                "device_key_expires_at", now
            ).execute()

            if result.data:
                return await call_next(request)

        raw_token = secrets.token_hex(64)
        token_hash = hashlib.sha512(raw_token.encode()).hexdigest()
        expires_at = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()

        supabase.table("approve_tokens").insert({
            "token": token_hash,
            "ip": ip,
            "user_agent": user_agent,
            "expires_at": expires_at,
        }).execute()

        _send_approve_email(raw_token)

        return JSONResponse(
            status_code=401,
            content={"detail": "Unbekanntes Gerät – Approve-Link wurde per Email verschickt"}
        )


def _send_approve_email(raw_token: str):
    approve_url = f"{FRONTEND_URL}/approve/{raw_token}"
    body = f"Neues Gerät möchte Zugang zum Dashboard.\n\nApprove-Link (10 Minuten gültig):\n{approve_url}"

    msg = MIMEText(body)
    msg["Subject"] = "Server Dashboard – Neues Gerät"
    msg["From"] = MAIL_FROM
    msg["To"] = ALLOWED_EMAIL

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASSWORD)
            smtp.sendmail(MAIL_FROM, ALLOWED_EMAIL, msg.as_string())
    except Exception as e:
        print(f"Email-Versand fehlgeschlagen: {e}")