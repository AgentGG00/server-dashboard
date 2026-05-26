# Übergabe – Server Dashboard

## Kontext

Dieses Dokument fasst alle Entscheidungen, den aktuellen Stand und offene nächste Schritte zusammen. Es dient als Einstiegspunkt für neue Chat-Sessions ohne Vorwissen.

---

## Projekt-Übersicht

Visuelles Serververwaltungs-Dashboard zur terminallosen Steuerung eigener Server-Infrastruktur. Läuft auf Oracle Cloud Free VM (ARM A1), erreichbar nur über Tailscale.

**Repos (GitHub Orga: AgentGG00):**
- `server-dashboard` – Frontend (SvelteKit) + Backend (FastAPI)
- `server-agent` – Agent der auf jedem verwalteten Server läuft (noch nicht begonnen)
- `workflows` – Reusable GitHub Actions Workflows für alle Projekte

---

## Techstack

| Schicht | Technologie |
|---|---|
| Frontend | SvelteKit + Skeleton UI + Tailwind |
| Backend | FastAPI (Python) |
| DB | Supabase (PostgreSQL) |
| DB-Verschlüsselung | AES-256 via `cryptography` |
| Webserver | Nginx (Reverse Proxy + IP-Whitelist) |
| Container | Docker + Docker Compose |
| Hosting | Oracle Cloud Free VM (ARM A1) |
| Tunnel | Tailscale |
| CI/CD | GitHub Actions (Reusable Workflows aus `workflows` Repo) |
| Auth | Google OAuth 2.0 + TOTP (pyotp) + Authlib |
| Email | Brevo SMTP (`dashboard@framenode.net`) |

---

## Projektstruktur

```text
server-dashboard/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
├── pyrightconfig.json
├── scripts/
├── tests/
├── docs/
│   ├── projekt-plan.md
│   ├── projekt-stand.md
│   ├── cliff.toml
│   ├── issues.md
│   └── übergabe.md
├── src/
│   ├── backend/
│   │   ├── main.py
│   │   ├── middleware/
│   │   │   └── device_check.py
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   └── settings.py
│   │   ├── services/
│   │   │   ├── supabase_service.py
│   │   │   └── encryption.py
│   │   ├── models/
│   │   └── schemas/
│   ├── db/
│   │   └── migrations/
│   │       └── 0001_init_tables.sql
│   └── frontend/
│       └── src/
│           ├── app.css
│           ├── app.html
│           ├── app.d.ts
│           ├── lib/
│           │   ├── index.ts
│           │   ├── assets/
│           │   │   └── favicon.svg
│           │   └── components/
│           │       ├── Topbar.svelte
│           │       ├── Sidebar.svelte
│           │       └── SettingsModal.svelte
│           └── routes/
│               ├── +error.svelte
│               ├── +layout.svelte
│               ├── +page.server.ts
│               ├── login/
│               │   ├── +page.svelte
│               │   └── totp/
│               │       └── +page.svelte
│               ├── approve/
│               │   └── [token]/
│               │       ├── +page.server.ts
│               │       └── +page.svelte
│               ├── password-reset/
│               │   └── [token]/
│               │       ├── +page.server.ts
│               │       └── +page.svelte
│               └── dashboard/
│                   ├── +layout.server.ts
│                   ├── +layout.svelte
│                   ├── +page.server.ts
│                   └── [server]/
│                       ├── +layout.svelte
│                       ├── +page.svelte
│                       ├── systemd/
│                       │   └── +page.svelte
│                       ├── firewall/
│                       │   └── +page.svelte
│                       ├── apache/
│                       │   └── +page.svelte
│                       └── docker/
│                           └── +page.svelte
```

---

## DB-Schema

Tabellen in `src/db/migrations/0001_init_tables.sql`:

- `servers` – registrierte Server (hostname, name, ip, api_key_hash, priority)
- `sessions` – Auth-Sessions (token_hash SHA-512, expires_at 6h, pending_totp)
- `totp_secrets` – TOTP Secret AES-256 verschlüsselt
- `admin_credentials` – Passwort für kritische Aktionen
- `trusted_devices` – bekannte Geräte (ip + user_agent, device_key_hash, 3-Monats-Ablauf)
- `approve_tokens` – One-Time Approve-Links (token, used, expires_at, page_opened_at)
- `approve_otp_codes` – Einmalpasswörter für Approve-Flow (code_hash, used, expires_at)
- `password_reset_tokens` – Passwort-Reset Links (token, used, expires_at)

---

## Wichtige Entscheidungen

**Coding-Konventionen:**
- Kein `chore` in Commit-Messages – stattdessen `init`
- CSS/Style-Blöcke gehören in `app.css`, nicht in Pages
- Globale Logik in `app.ts` oder `src/lib/`
- Skeleton-Klassen (`btn`, `card`, `preset-*`) direkt als Tailwind-Klassen auf Elementen
- `Button`, `Card` etc. existieren nicht als Komponenten in `@skeletonlabs/skeleton-svelte` v4.15

**Auth:**
- IP-Whitelist läuft über Nginx – nicht in SvelteKit
- Nginx blockt unbekannte IPs auf connection refused – kein HTTP-Response
- Geräte-Fingerprint: Tailscale-IP + User-Agent + Device-Token (httponly Cookie, 90 Tage)
- Approve-Flow: Google OAuth + TOTP + Einmalpasswort per Email (3 Schritte)
- Approve-Page URL: kryptografisch zufällig, 64+ Zeichen, One-Time-Use
- Session-Token: raw token als httponly Cookie, SHA-512 Hash in DB
- 3-Monats-Key: TOTP-Skip für bekannte Geräte, SHA-512 gehasht in DB
- Passwort-Reset: One-Time-URL, 10min Gültigkeit, eigener GET-Endpunkt zur Validierung
- `/auth/verify` liest `session_token` Cookie, filtert `pending_totp: true`

**Email:**
- Brevo SMTP (`smtp-relay.brevo.com:587` mit STARTTLS)
- Absender: `dashboard@framenode.net`
- Domain `framenode.net` in Cloudflare mit SPF + DKIM für Brevo verifiziert

**Routing:**
- `/` → redirect `/login`
- `/dashboard` → Cookie `last_server` → erster Server aus DB nach Priorität
- `[server]` Parameter kommt aus Agent-Registrierung (Hostname)
- `currentServer` wird im Guard gesetzt und an alle Kind-Pages vererbt
- Settings: Modal in Dashboard-Layout, kein eigener Route

**Sonstiges:**
- SvelteKit Build läuft in GitHub Actions, nicht auf der VM (1GB RAM reicht nicht)
- Supabase Ping alle 3-4 Tage via Cron-Job auf Oracle VM – bereits eingerichtet
- `requirements.txt` im Root, Patch-Version eingefroren (`~=X.Y.Z`)
- `VITE_API_URL` für Frontend-API-Calls (nicht `process.env`)
- Migrations liegen in `src/db/migrations/`

---

## Nächste Schritte

1. Verwaiste Dateien `26.1.1` und `=1.6.0` im Root löschen
2. DNS-Eintrag auf Oracle VM IP setzen (Cloudflare)
3. Nginx-Config schreiben (Reverse Proxy + Tailscale IP-Whitelist)
4. Docker Compose für Backend + Frontend + Nginx finalisieren
5. Supabase Migration ausführen (erster Deploy)
6. Erstes Deployment (bootstrap)
7. Bootstrap auf false setzen