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
- [ ] Login-Page (`/login`)
- [ ] Dashboard-Layout (Sidebar + Topbar)
- [ ] Server-Redirect (`/dashboard` → letzter Server / erster aus DB)
- [ ] Cookie-Handling (last_server)

### Features

#### feat: Auth
- [ ] Google OAuth 2.0 Integration (nur eigene Gmail)
- [ ] TOTP 2FA (pyotp) implementieren
- [ ] Session-Management
- [ ] Token-Validierung für direkten Dashboard-Zugang

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
- [ ] –

### Test / Review
- [ ] –

### Deployment
- [ ] DNS-Eintrag auf Oracle VM IP setzen (Cloudflare)
- [ ] Nginx auf Oracle VM installieren + Grundkonfiguration
- [ ] Docker Compose für Backend + Frontend + Nginx finalisieren
- [ ] Supabase Backup auf VPS einrichten
- [ ] Erstes Deployment (bootstrap)
- [ ] Bootstrap auf false setzen