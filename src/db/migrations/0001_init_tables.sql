-- Servers (vom Agent registriert)
CREATE TABLE servers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    hostname TEXT NOT NULL,
    ip TEXT NOT NULL,
    api_key_hash TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 0,
    last_seen TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Sessions (6h Login-Token)
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    token_hash TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    pending_totp BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- TOTP Secrets (AES-256 verschlüsselt)
CREATE TABLE totp_secrets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    secret_encrypted TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Admin Credentials (Passwort für kritische Aktionen)
CREATE TABLE admin_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Trusted Devices (IP + User-Agent Kombination)
CREATE TABLE trusted_devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ip TEXT NOT NULL,
    user_agent TEXT NOT NULL,
    device_key_hash TEXT NOT NULL,
    device_key_expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Approve Tokens (One-Time-Use, 10min Gültigkeit)
CREATE TABLE approve_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    token TEXT NOT NULL UNIQUE,
    ip TEXT NOT NULL,
    user_agent TEXT NOT NULL,
    used BOOLEAN NOT NULL DEFAULT FALSE,
    expires_at TIMESTAMPTZ NOT NULL,
    page_opened_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- OTP Codes (6-stellig, Einmalpasswort für Approve-Flow)
CREATE TABLE approve_otp_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    approve_token_id UUID NOT NULL REFERENCES approve_tokens(id),
    code_hash TEXT NOT NULL,
    used BOOLEAN NOT NULL DEFAULT FALSE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);