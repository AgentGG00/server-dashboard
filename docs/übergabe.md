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

---

## Projektstruktur

server-dashboard/
- src/
  - backend/
    - main.py
    - routers/
      - auth.py – fertig, noch nicht in main.py registriert
    - services/
      - supabase.py
  - frontend/ – SvelteKit Projekt
    - src/
      - lib/
        - components/
          - Topbar.svelte
          - Sidebar.svelte
      - routes/
        - +page.server.ts – redirect /login
        - login/
          - +page.svelte
        - dashboard/
          - +layout.server.ts – Auth-Guard + Server-Liste
          - +layout.svelte – Hauptlayout
          - +page.server.ts – redirect letzter/erster Server
          - [server]/
            - +layout.svelte
            - +page.svelte – Overview
            - systemd/
            - firewall/
            - apache/
            - docker/
- supabase/
  - migrations/
    - 0001_init_tables.sql
- docs/
  - projekt-plan.md
  - projekt-stand.md
  - cliff.toml
  - übergabe.md

---

## DB-Schema (Supabase)

Tabellen in `0001_init_tables.sql`:

- `servers` – registrierte Server (hostname, name, ip, api_key_hash, priority)
- `sessions` – Auth-Sessions (token_hash SHA-512, expires_at 6h)
- `totp_secrets` – TOTP Secret AES-256 verschlüsselt
- `admin_credentials` – Passwort für kritische Aktionen
- `trusted_devices` – bekannte Geräte (ip + user_agent, device_key_hash, 3-Monats-Ablauf)
- `approve_tokens` – One-Time Approve-Links (token, used, expires_at, page_opened_at)

---

## Wichtige Entscheidungen

**Coding-Konventionen:**
- Kein `chore` in Commit-Messages – stattdessen `init`
- CSS/Style-Blöcke gehören in `app.css`, nicht in Pages
- Globale Logik in `app.ts` oder `src/lib/`
- Skeleton-Klassen (`btn`, `card`, `preset-*`) direkt als Tailwind-Klassen auf Elementen – kein Import nötig
- `Button`, `Card` etc. existieren nicht als Komponenten in `@skeletonlabs/skeleton-svelte` v4.15 – nur komplexe interaktive Komponenten sind dort enthalten

**Auth:**
- IP-Whitelist läuft über Nginx – nicht in SvelteKit
- Nginx blockt unbekannte IPs auf connection refused – kein HTTP-Response
- Geräte-Fingerprint: Tailscale-IP + User-Agent Kombination
- Approve-Page URL: kryptografisch zufällig, 64+ Zeichen, One-Time-Use → 404 nach Aufruf
- Approve-Link Gültigkeit: 10min ab Versand, 10min Session-Timeout auf Page (408)
- Session-Token: raw token als httponly Cookie, SHA-512 Hash in DB
- 3-Monats-Key: TOTP-Skip für bekannte Geräte, SHA-512 gehasht in DB
- Passwort-Reset über Supabase Auth eingebaut

**Routing:**
- / → redirect /login
- /dashboard → Cookie last_server → erster Server aus DB nach Priorität
- [server] Parameter kommt aus Agent-Registrierung (Hostname), kein hartcodierter Default
- currentServer wird im Guard gesetzt und an alle Kind-Pages vererbt

**Sonstiges:**
- SvelteKit Build läuft in GitHub Actions, nicht auf der VM (1GB RAM reicht nicht)
- Supabase Ping alle 3-4 Tage via Cron-Job auf Oracle VM verhindert DB-Pause
- src/lib/ war fälschlicherweise in Root-.gitignore durch lib/ Python-Eintrag – wurde gefixt
- src/backend/routers/, models/, schemas/ waren fälschlicherweise in .gitignore – wurde gefixt

---

## Nächste Schritte

1. `auth.py` Router in `main.py` registrieren
2. Google OAuth Credentials in Google Cloud Console anlegen
3. `.env` mit Google Credentials befüllen
4. Geräte-Check Middleware implementieren (`src/backend/middleware/device_check.py`)
5. Approve-Flow implementieren (Backend + Frontend)
6. TOTP-Flow implementieren
7. Danach: Dashboard Overview (Ressourcen-Monitor)

---

## Offene Fragen / noch nicht entschieden

- Nginx-Config: genaue Tailscale-IP Whitelist Syntax noch nicht geschrieben
- Docker Compose für Backend + Frontend + Nginx: noch nicht finalisiert
- Google Cloud Console: Credentials noch nicht angelegt