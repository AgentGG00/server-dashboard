# Webdashboard (Visuelles Serververwaltungs Webapp) – Projekt-Plan

[![Status](https://img.shields.io/badge/status-WIP-yellow)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

Visuelles Serververwaltungs-Dashboard zur terminallosen Steuerung und Überwachung
eigener Server-Infrastruktur über eine Webapp.

---

## Ziele & Anforderungen

- Zentrale Steuerung aller Server ohne Terminal
- Immer erreichbar – unabhängig vom Status der verwalteten Server
- Sicher: MFA, IP-Whitelist, Root-Aktionen mit Passwort-Bestätigung
- Erweiterbar auf neue Server per Agent-Registrierung

---

## Techstack

| Schicht | Technologie |
|---|---|
| Frontend | SvelteKit + Skeleton UI + Tailwind |
| Backend | FastAPI (Python) |
| DB | Supabase (PostgreSQL) |
| DB-Verschlüsselung | AES-256 via `cryptography` |
| Webserver | Nginx (Reverse Proxy) |
| Container | Docker + Docker Compose |
| Hosting | Oracle Cloud Free VM (ARM A1) |
| Tunnel | Tailscale |
| CI/CD | GitHub Actions (Reusable Workflows) |
| Auth | Google OAuth 2.0 + TOTP (pyotp) |

---

## Umsetzungsreihenfolge

1. Oracle VM + DNS + Tailscale Setup
2. Repo anlegen + Grundstruktur
3. Codespace + venv + FastAPI Grundgerüst
4. Supabase DB-Schema + Verbindung
5. GitHub Actions Deployment-Pipeline
6. Auth-System (Google OAuth + TOTP)
7. Agent-System (Registrierung, API-Key-Validierung)
8. Dashboard Overview (Ressourcen-Monitor)
9. Docker-Verwaltung
10. Compose-Verwaltung
11. Apache-Verwaltung + TLS
12. UFW-Verwaltung
13. Server-Steuerung
14. Contabo API Integration
15. Frontend – parallel zu 8–14

---

## Core Features

- **Auth** – Tailscale-only Zugang, Google OAuth (nur eigene Gmail), TOTP 2FA
- **Dashboard/Overview** – Ressourcen-Monitor pro Server
- **Agent-System** – Server registrieren sich mit API-Key im Backend
- **Docker-Verwaltung** – Container Status, Start/Stop/Restart, Logs
- **Compose-Verwaltung** – Stack Status, Up/Down, neue Compose-Datei deployen
- **Apache-Verwaltung** – Virtual Hosts anzeigen, anlegen, TLS via Certbot
- **UFW-Verwaltung** – Regeln anzeigen, hinzufügen, löschen
- **Server-Steuerung** – Reboot, Shutdown über Agent
- **Contabo-Integration** – VPS starten, Rescue-Modus über Contabo API