# server-dashboard

[![Build Status](https://img.shields.io/github/actions/workflow/status/AgentGG00/server-dashboard/cd-deploy.yml?label=deploy)](https://github.com/AgentGG00/server-dashboard/actions)
[![Version](https://img.shields.io/github/v/release/AgentGG00/server-dashboard)](https://github.com/AgentGG00/server-dashboard/releases)
[![Status](https://img.shields.io/badge/status-WIP-yellow)]()
[![License](https://img.shields.io/github/license/AgentGG00/server-dashboard)](https://github.com/AgentGG00/server-dashboard/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org)
[![Node](https://img.shields.io/badge/Node-20-green)](https://nodejs.org)

Webdashboard (Visuelles Serververwaltungs Webapp) – zentrale Steuerung und Überwachung eigener Server-Infrastruktur ohne Terminal.

## Features

- Google OAuth 2.0 + TOTP 2FA + Tailscale IP-Whitelist
- Ressourcen-Monitor pro Server (CPU, RAM, Disk, Netzwerk)
- Docker & Compose Verwaltung
- Apache vHost + TLS via Certbot
- UFW Firewall-Verwaltung
- Server-Steuerung (Reboot, Shutdown)
- Contabo API Integration

## Local Development

1. Clone the repo
2. Copy `.env.example` to `.env` and fill in real values
3. Create venv: `python -m venv .venv && source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Start backend: `python src/backend/main.py`

## License

MIT
