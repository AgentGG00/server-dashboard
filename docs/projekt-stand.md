# Webdashboard (Visuelles Serververwaltungs Webapp) – Projekt-Stand

---

## Checklist

### Init
- [x] Oracle Cloud Account erstellen + Free Tier aktivieren
- [x] ARM A1 VM provisionieren
- [ ] Tailscale auf Oracle VM installieren + ins Tailnet aufnehmen
- [ ] DNS-Eintrag auf Oracle VM IP setzen (Cloudflare)
- [ ] Nginx auf Oracle VM installieren + Grundkonfiguration
- [x] Docker + Docker Compose auf Oracle VM installieren
- [x] GitHub Repo `server-dashboard` anlegen
- [ ] Grundstruktur nach projekt-plan.md anlegen
- [ ] `.env.example` anlegen
- [x] `.gitignore` anlegen
- [x] `LICENSE` (MIT) anlegen
- [ ] Codespace einrichten + venv + requirements.txt

### Framework
- [x] GitHub Actions Deployment-Pipeline anlegen
- [x] git-cliff konfigurieren (`docs/cliff.toml`)
- [ ] Docker Compose für Backend + Frontend + Nginx

### Backend
- [ ] FastAPI Grundgerüst (`src/backend/main.py`)
- [ ] Supabase Verbindung einrichten
- [ ] DB-Verschlüsselung (AES-256) implementieren
- [ ] DB-Schema (Migrations) anlegen

### Frontend
- [ ] SvelteKit Projekt initialisieren
- [ ] Skeleton UI + Tailwind einrichten
- [ ] Dark Mode als Default konfigurieren
- [ ] Routing-Grundstruktur anlegen

### Features

#### feat: Auth
- [ ] Google OAuth 2.0 Integration (nur eigene Gmail)
- [ ] TOTP 2FA (pyotp) implementieren
- [ ] Tailscale IP-Whitelist (Middleware)
- [ ] Session-Management

#### feat: Agent-System
- [ ] Agent-Registrierung im Backend
- [ ] API-Key-Validierung
- [ ] Heartbeat-Monitoring

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
- [ ] Erstes Deployment (bootstrap)
- [ ] Bootstrap auf false setzen