# Webdashboard (Visuelles Serververwaltungs Webapp) – Projekt-Stand
---
## Checklist

### Init
- [x] Oracle Cloud Account erstellen + Free Tier aktivieren
- [x] ARM A1 VM provisionieren
- [x] Tailscale auf Oracle VM installieren + ins Tailnet aufnehmen
- [x] Docker + Docker Compose auf Oracle VM installieren
- [x] GitHub Repo `server-dashboard` anlegen
- [x] Grundstruktur nach projekt-plan.md anlegen
- [x] `.env.example` anlegen
- [x] `.gitignore` anlegen
- [x] `LICENSE` (MIT) anlegen
- [x] Codespace einrichten + venv + requirements.txt

### Framework
- [x] GitHub Actions Deployment-Pipeline anlegen
- [x] git-cliff konfigurieren (`docs/cliff.toml`)

### Backend
- [x] FastAPI Grundgerüst (`src/backend/main.py`)
- [x] Supabase Verbindung einrichten
- [x] DB-Verschlüsselung (AES-256) implementieren
- [x] DB-Schema (Migrations) anlegen

### Frontend
- [x] SvelteKit Projekt initialisieren
- [x] Skeleton UI + Tailwind einrichten
- [x] Systemthema als Default konfigurieren
- [x] Layout-Konzept definieren (Seitenstruktur, Navigation, Routing-Schema)
- [x] Routing-Grundstruktur anlegen
- [x] Auth-Guard (`/dashboard` +layout.server.ts)
- [x] Login-Page (`/login`)
- [x] Dashboard-Layout (Sidebar + Topbar)
- [x] Server-Redirect (`/dashboard` → letzter Server / erster aus DB)
- [x] Cookie-Handling (last_server)

### Features

#### feat: Auth
- [x] Geräte-Check Middleware (Tailscale-IP + User-Agent + Device-Token)
- [x] 401-Handler + Email-Benachrichtigung bei unbekanntem Gerät (Brevo SMTP)
- [x] Approve-Flow
- [x] Kryptografische One-Time-URL generieren (64+ Zeichen)
- [x] 10min Gültigkeit ab Email-Versand
- [x] 10min Session-Timeout auf Approve-Page (408)
- [x] Single-Use Invalidierung nach Aufruf (404)
- [x] Google OAuth + TOTP + Einmalpasswort per Email
- [x] Gerät als trusted speichern (IP + User-Agent + Device-Token)
- [x] Google OAuth (nur eigene Email) – `/auth/google` + `/auth/callback`
- [x] TOTP bei neuem Gerät oder 3-Monats-Key abgelaufen
- [x] 3-Monats-Key speichern (TOTP-Skip)
- [x] Session-Management (6h Token)
- [x] Token-Validierung für direkten Dashboard-Zugang (Cookie-basiert)

#### feat: Settings
- [x] Test-Mail verschicken
- [x] Trusted Devices anzeigen + entfernen
- [x] Aktive Sessions anzeigen + invalidieren
- [x] TOTP zurücksetzen
- [x] Passwort-Reset (One-Time-URL Flow, 10min)
- [x] Agent-Liste + entfernen + Priorität sortieren (UI)
- [x] Settings-Modal (Backdrop-Blur, Tab-Navigation)
- [x] Password-Reset-Page (`/password-reset/[token]`)

#### feat: Error-Pages
- [x] Dynamische Error-Page (401, 403, 404, 408, 410, 500)

#### feat: Dashboard/Overview
- [ ] CPU-Auslastung pro Server
- [ ] RAM-Auslastung pro Server
- [ ] Disk-Auslastung pro Server
- [ ] Netzwerk-Statistiken pro Server

#### feat: Docker-Verwaltung
- [ ] Container-Liste
- [ ] Container starten / stoppen / neustarten
- [ ] Container-Logs abrufen

#### feat: Compose-Verwaltung
- [ ] Stack-Liste
- [ ] Stack up / down
- [ ] Neue Compose-Datei deployen

#### feat: Apache-Verwaltung
- [ ] Virtual Hosts auflisten
- [ ] Neuen vHost anlegen
- [ ] vHost aktivieren/deaktivieren
- [ ] Let's Encrypt via Certbot anfordern

#### feat: UFW-Verwaltung
- [ ] Regeln auflisten
- [ ] Regel hinzufügen / löschen

#### feat: Server-Steuerung
- [ ] Reboot
- [ ] Shutdown

#### feat: Contabo-Integration
- [ ] VPS starten über Contabo API
- [ ] Rescue-Modus über Contabo API

### Fix
- [x] `<a` Tag fehlend in Sidebar.svelte
- [x] `return` außerhalb Funktion in supabase_service.py
- [x] `<slot />` → `{@render children()}` in [server]/+layout.svelte
- [x] `process.env.API_URL` → `import.meta.env.VITE_API_URL`
- [x] Ordner `approved/` → `approve/`, `passwort-reset/` → `password-reset/`
- [x] Verwaiste Dateien `26.1.1` und `=1.6.0` im Root entfernt

### Test / Review
- [ ] –

### Deployment
- [x] requirements.txt Patch-Version eingefroren (`~=X.Y.Z`)
- [x] Nginx-Config (Reverse Proxy + Tailscale IP-Whitelist + HTTPS)
- [x] Docker Compose für Backend + Frontend + Nginx finalisieren
- [x] Dockerfile mit Multi-Stage Build + supervisord
- [x] SvelteKit adapter-node eingerichtet
- [x] GitHub Actions Pipeline mit PAT verdrahtet
- [x] DASHBOARD_ENV als Org Secret angelegt
- [ ] DNS-Eintrag auf Oracle VM IP setzen (Cloudflare)
- [ ] Zertifikat via Certbot + Cloudflare DNS-Challenge ausstellen
- [ ] Supabase Migration ausführen (erster Deploy)
- [ ] Erstes Deployment (bootstrap)
- [ ] Bootstrap auf false setzen