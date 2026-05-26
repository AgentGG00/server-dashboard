import os
import secrets
import hashlib
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/settings", tags=["settings"])

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")
ALLOWED_EMAIL = os.getenv("ALLOWED_EMAIL")
FRONTEND_URL = os.getenv("FRONTEND_URL")


def _send_mail(subject: str, body: str):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = MAIL_FROM
    msg["To"] = ALLOWED_EMAIL

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(SMTP_USER, SMTP_PASSWORD)
        smtp.sendmail(MAIL_FROM, ALLOWED_EMAIL, msg.as_string())


# ── Test-Mail ────────────────────────────────────────────────────────────────

@router.post("/test-mail")
async def send_test_mail():
    try:
        _send_mail(
            subject="Server Dashboard – Test-Mail",
            body="Das ist eine Test-Mail vom Server Dashboard.",
        )
        return {"detail": "Test-Mail verschickt"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email-Versand fehlgeschlagen: {e}")


# ── Trusted Devices ──────────────────────────────────────────────────────────

@router.get("/trusted-devices")
async def list_trusted_devices(request: Request):
    supabase = request.app.state.supabase
    result = supabase.table("trusted_devices").select(
        "id, ip, user_agent, device_key_expires_at, created_at"
    ).order("created_at", desc=True).execute()
    return result.data


@router.delete("/trusted-devices/{device_id}")
async def delete_trusted_device(device_id: str, request: Request):
    supabase = request.app.state.supabase
    result = supabase.table("trusted_devices").delete().eq("id", device_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Gerät nicht gefunden")
    return {"detail": "Gerät entfernt"}


# ── Aktive Sessions ──────────────────────────────────────────────────────────

@router.get("/sessions")
async def list_sessions(request: Request):
    supabase = request.app.state.supabase
    now = datetime.now(timezone.utc).isoformat()
    result = supabase.table("sessions").select(
        "id, expires_at, created_at"
    ).eq("pending_totp", False).gt("expires_at", now).order(
        "created_at", desc=True
    ).execute()
    return result.data


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, request: Request):
    supabase = request.app.state.supabase
    result = supabase.table("sessions").delete().eq("id", session_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")
    return {"detail": "Session invalidiert"}


# ── TOTP Reset ───────────────────────────────────────────────────────────────

@router.post("/totp/reset")
async def totp_reset(request: Request):
    supabase = request.app.state.supabase
    supabase.table("totp_secrets").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    return {"detail": "TOTP zurückgesetzt – Setup unter /auth/totp/setup erforderlich"}


# ── Passwort-Reset ───────────────────────────────────────────────────────────

@router.post("/password-reset/request")
async def password_reset_request(request: Request):
    supabase = request.app.state.supabase

    raw_token = secrets.token_hex(64)
    token_hash = hashlib.sha512(raw_token.encode()).hexdigest()
    expires_at = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()

    supabase.table("password_reset_tokens").insert({
        "token": token_hash,
        "expires_at": expires_at,
    }).execute()

    reset_url = f"{FRONTEND_URL}/settings/password-reset/{raw_token}"

    try:
        _send_mail(
            subject="Server Dashboard – Passwort zurücksetzen",
            body=(
                f"Passwort-Reset angefordert.\n\n"
                f"Link (10 Minuten gültig):\n{reset_url}\n\n"
                f"Falls du das nicht angefordert hast, ignoriere diese Email."
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email-Versand fehlgeschlagen: {e}")

    return {"detail": "Reset-Link verschickt"}


@router.post("/password-reset/{token}/confirm")
async def password_reset_confirm(token: str, request: Request):
    supabase = request.app.state.supabase
    token_hash = hashlib.sha512(token.encode()).hexdigest()
    now = datetime.now(timezone.utc).isoformat()

    result = supabase.table("password_reset_tokens").select("*").eq(
        "token", token_hash
    ).eq("used", False).gt("expires_at", now).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Link ungültig oder abgelaufen")

    body = await request.json()
    new_password = body.get("password", "")
    confirm_password = body.get("confirm_password", "")

    if not new_password or new_password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwörter stimmen nicht überein")

    if len(new_password) < 12:
        raise HTTPException(status_code=400, detail="Passwort muss mindestens 12 Zeichen haben")

    password_hash = hashlib.sha512(new_password.encode()).hexdigest()

    existing = supabase.table("admin_credentials").select("id").execute()
    if existing.data:
        supabase.table("admin_credentials").update({
            "password_hash": password_hash,
            "updated_at": now,
        }).eq("id", existing.data[0]["id"]).execute()
    else:
        supabase.table("admin_credentials").insert({
            "password_hash": password_hash,
        }).execute()

    supabase.table("password_reset_tokens").update({
        "used": True
    }).eq("token", token_hash).execute()

    return {"detail": "Passwort erfolgreich gesetzt"}


# ── Agents ───────────────────────────────────────────────────────────────────

@router.get("/agents")
async def list_agents(request: Request):
    supabase = request.app.state.supabase
    result = supabase.table("servers").select(
        "id, name, hostname, ip, priority, last_seen, created_at"
    ).order("priority", desc=False).execute()
    return result.data


@router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str, request: Request):
    supabase = request.app.state.supabase
    result = supabase.table("servers").delete().eq("id", agent_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Agent nicht gefunden")
    return {"detail": "Agent entfernt"}


@router.patch("/agents/{agent_id}/priority")
async def update_agent_priority(agent_id: str, request: Request):
    body = await request.json()
    priority = body.get("priority")

    if priority is None or not isinstance(priority, int):
        raise HTTPException(status_code=400, detail="Ungültige Priorität")

    supabase = request.app.state.supabase
    result = supabase.table("servers").update({
        "priority": priority
    }).eq("id", agent_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Agent nicht gefunden")

    return {"detail": "Priorität aktualisiert"}