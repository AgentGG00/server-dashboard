import os
import secrets
import hashlib
import base64
import random
import pyotp
import qrcode
import io
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from authlib.integrations.httpx_client import AsyncOAuth2Client
from cryptography.fernet import Fernet

router = APIRouter(prefix="/auth", tags=["auth"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
ALLOWED_EMAIL = os.getenv("ALLOWED_EMAIL")
FRONTEND_URL = os.getenv("FRONTEND_URL")
TOTP_ISSUER = os.getenv("TOTP_ISSUER", "server-dashboard")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")


def _get_fernet() -> Fernet:
    if not ENCRYPTION_KEY:
        raise ValueError("ENCRYPTION_KEY nicht gesetzt")
    return Fernet(ENCRYPTION_KEY.encode())


def _encrypt(value: str) -> str:
    return _get_fernet().encrypt(value.encode()).decode()


def _decrypt(value: str) -> str:
    return _get_fernet().decrypt(value.encode()).decode()


def _send_otp_email(otp: str):
    if not all([SMTP_HOST, SMTP_USER, SMTP_PASSWORD, MAIL_FROM, ALLOWED_EMAIL]):
        raise ValueError("SMTP-Konfiguration unvollständig")
    body = (
        f"Dein Einmalpasswort für die Geräte-Freigabe:\n\n"
        f"  {otp}\n\n"
        f"Gültig für 10 Minuten. Nicht weitergeben."
    )
    msg = MIMEText(body)
    msg["Subject"] = "Server Dashboard – Einmalpasswort"
    msg["From"] = MAIL_FROM
    msg["To"] = ALLOWED_EMAIL

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:  # type: ignore[arg-type]
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASSWORD)  # type: ignore[arg-type]
            smtp.sendmail(MAIL_FROM, ALLOWED_EMAIL, msg.as_string())  # type: ignore[arg-type]
    except Exception as e:
        print(f"OTP Email-Versand fehlgeschlagen: {e}")


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
        await client.fetch_token(
            "https://oauth2.googleapis.com/token",
            code=code,
        )
        userinfo = await client.get("https://www.googleapis.com/oauth2/v3/userinfo")
        userinfo = userinfo.json()

    if userinfo.get("email") != ALLOWED_EMAIL:
        raise HTTPException(status_code=403, detail="Unauthorized email")

    supabase = request.app.state.supabase

    device_token = request.cookies.get("device_token")
    totp_required = True

    if device_token:
        device_token_hash = hashlib.sha512(device_token.encode()).hexdigest()
        now = datetime.now(timezone.utc).isoformat()
        result = supabase.table("trusted_devices").select("*").eq(
            "device_key_hash", device_token_hash
        ).gt("device_key_expires_at", now).execute()

        if result.data:
            totp_required = False

    if totp_required:
        pending_token = secrets.token_hex(32)
        pending_hash = hashlib.sha512(pending_token.encode()).hexdigest()
        expires_at = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()

        supabase.table("sessions").insert({
            "token_hash": pending_hash,
            "expires_at": expires_at,
            "pending_totp": True,
        }).execute()

        response = RedirectResponse(f"{FRONTEND_URL}/login/totp")
        response.set_cookie(
            key="pending_token",
            value=pending_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=60 * 5,
        )
        return response

    return _create_session_response(supabase)


@router.post("/totp/verify")
async def totp_verify(request: Request):
    body = await request.json()
    code = body.get("code", "")

    pending_token = request.cookies.get("pending_token")
    if not pending_token:
        raise HTTPException(status_code=401, detail="Kein pending Token")

    pending_hash = hashlib.sha512(pending_token.encode()).hexdigest()
    now = datetime.now(timezone.utc).isoformat()

    supabase = request.app.state.supabase

    result = supabase.table("sessions").select("*").eq(
        "token_hash", pending_hash
    ).gt("expires_at", now).execute()

    if not result.data:
        raise HTTPException(status_code=401, detail="Token abgelaufen")

    totp_result = supabase.table("totp_secrets").select("secret_encrypted").execute()
    if not totp_result.data:
        raise HTTPException(status_code=500, detail="TOTP nicht eingerichtet")

    secret = _decrypt(totp_result.data[0]["secret_encrypted"])
    totp = pyotp.TOTP(secret)

    if not totp.verify(code, valid_window=1):
        raise HTTPException(status_code=401, detail="Ungültiger TOTP-Code")

    supabase.table("sessions").delete().eq(
        "token_hash", pending_hash
    ).execute()

    device_token = request.cookies.get("device_token")
    if device_token:
        device_token_hash = hashlib.sha512(device_token.encode()).hexdigest()
        new_expires = (datetime.now(timezone.utc) + timedelta(days=90)).isoformat()
        supabase.table("trusted_devices").update({
            "device_key_expires_at": new_expires
        }).eq("device_key_hash", device_token_hash).execute()

    response = _create_session_response(supabase)
    response.delete_cookie("pending_token")
    return response


@router.post("/totp/verify-approve")
async def totp_verify_approve(request: Request):
    body = await request.json()
    code = body.get("code", "")
    approve_token_raw = body.get("approve_token", "")

    if not approve_token_raw:
        raise HTTPException(status_code=400, detail="Kein Approve-Token")

    approve_token_hash = hashlib.sha512(approve_token_raw.encode()).hexdigest()
    now = datetime.now(timezone.utc).isoformat()

    supabase = request.app.state.supabase

    result = supabase.table("approve_tokens").select("*").eq(
        "token", approve_token_hash
    ).eq("used", False).gt("expires_at", now).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Approve-Token ungültig")

    entry = result.data[0]

    totp_result = supabase.table("totp_secrets").select("secret_encrypted").execute()
    if not totp_result.data:
        raise HTTPException(status_code=500, detail="TOTP nicht eingerichtet")

    secret = _decrypt(totp_result.data[0]["secret_encrypted"])
    totp = pyotp.TOTP(secret)

    if not totp.verify(code, valid_window=1):
        raise HTTPException(status_code=401, detail="Ungültiger TOTP-Code")

    otp = str(random.randint(100000, 999999))
    otp_hash = hashlib.sha512(otp.encode()).hexdigest()
    otp_expires = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()

    supabase.table("approve_otp_codes").insert({
        "approve_token_id": entry["id"],
        "code_hash": otp_hash,
        "expires_at": otp_expires,
    }).execute()

    _send_otp_email(otp)

    return JSONResponse(content={"detail": "OTP verschickt"})


@router.get("/totp/setup")
async def totp_setup(request: Request):
    supabase = request.app.state.supabase

    existing = supabase.table("totp_secrets").select("id").execute()
    if existing.data:
        raise HTTPException(status_code=404, detail="Not found")

    secret = pyotp.random_base32()
    secret_encrypted = _encrypt(secret)

    supabase.table("totp_secrets").insert({
        "secret_encrypted": secret_encrypted,
    }).execute()

    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=ALLOWED_EMAIL, issuer_name=TOTP_ISSUER)

    img = qrcode.make(uri)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return {
        "qr_code": f"data:image/png;base64,{qr_base64}",
        "secret": secret,
    }


@router.get("/verify")
async def verify_session(request: Request):
    token = request.cookies.get("session_token")

    if not token:
        raise HTTPException(status_code=401, detail="No token")

    token_hash = hashlib.sha512(token.encode()).hexdigest()
    now = datetime.now(timezone.utc).isoformat()

    supabase = request.app.state.supabase
    result = supabase.table("sessions").select("*").eq(
        "token_hash", token_hash
    ).eq("pending_totp", False).gt("expires_at", now).execute()

    if not result.data:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return {"valid": True}


@router.get("/approve/{token}")
async def approve_page_open(token: str, request: Request):
    supabase = request.app.state.supabase
    token_hash = hashlib.sha512(token.encode()).hexdigest()
    now = datetime.now(timezone.utc).isoformat()

    result = supabase.table("approve_tokens").select("*").eq(
        "token", token_hash
    ).eq("used", False).gt("expires_at", now).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Link ungültig oder abgelaufen")

    entry = result.data[0]

    if not entry.get("page_opened_at"):
        supabase.table("approve_tokens").update({
            "page_opened_at": now
        }).eq("id", entry["id"]).execute()

    return RedirectResponse(f"{FRONTEND_URL}/approve/{token}")


@router.post("/approve/{token}/confirm")
async def approve_confirm(token: str, request: Request):
    supabase = request.app.state.supabase
    token_hash = hashlib.sha512(token.encode()).hexdigest()
    now = datetime.now(timezone.utc)

    result = supabase.table("approve_tokens").select("*").eq(
        "token", token_hash
    ).eq("used", False).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Link ungültig")

    entry = result.data[0]

    if entry["expires_at"] < now.isoformat():
        raise HTTPException(status_code=410, detail="Link abgelaufen")

    if entry.get("page_opened_at"):
        page_opened = datetime.fromisoformat(entry["page_opened_at"])
        if (now - page_opened) > timedelta(minutes=10):
            raise HTTPException(status_code=408, detail="Session abgelaufen")

    body = await request.json()
    otp_code = body.get("otp_code", "")
    otp_hash = hashlib.sha512(otp_code.encode()).hexdigest()

    otp_result = supabase.table("approve_otp_codes").select("*").eq(
        "approve_token_id", entry["id"]
    ).eq("code_hash", otp_hash).eq("used", False).gt(
        "expires_at", now.isoformat()
    ).execute()

    if not otp_result.data:
        raise HTTPException(status_code=401, detail="Ungültiges oder abgelaufenes OTP")

    supabase.table("approve_otp_codes").update({
        "used": True
    }).eq("id", otp_result.data[0]["id"]).execute()

    raw_device_token = secrets.token_hex(64)
    device_token_hash = hashlib.sha512(raw_device_token.encode()).hexdigest()
    device_key_expires_at = (now + timedelta(days=90)).isoformat()

    supabase.table("trusted_devices").insert({
        "ip": entry["ip"],
        "user_agent": entry["user_agent"],
        "device_key_hash": device_token_hash,
        "device_key_expires_at": device_key_expires_at,
    }).execute()

    supabase.table("approve_tokens").update({
        "used": True
    }).eq("id", entry["id"]).execute()

    response = JSONResponse(content={"detail": "Gerät freigegeben"})
    response.set_cookie(
        key="device_token",
        value=raw_device_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 90,
    )
    return response


def _create_session_response(supabase) -> JSONResponse:
    raw_token = secrets.token_hex(64)
    token_hash = hashlib.sha512(raw_token.encode()).hexdigest()
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=6)).isoformat()

    supabase.table("sessions").insert({
        "token_hash": token_hash,
        "expires_at": expires_at,
    }).execute()

    response = RedirectResponse(f"{os.getenv('FRONTEND_URL')}/dashboard")
    response.set_cookie(
        key="session_token",
        value=raw_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 6,
    )
    return response
