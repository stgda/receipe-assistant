# Recipe Assistant: Docker Desktop (Windows) + Tailscale (WSL) Setup

## Übersicht

Diese Anleitung ist speziell für deine Konfiguration:
- ✅ **Docker Desktop** bereits auf Windows 11 installiert
- ✅ **Tailscale** bereits auf Windows 11 installiert
- ✅ **Ubuntu WSL** vorhanden
- 🎯 **Ziel**: Recipe Assistant in Docker laufen lassen und über Tailscale von überall erreichbar machen

---

## Architektur

```
Windows 11
├── Docker Desktop ──────┐
│                        │
├── Tailscale ───────────┤
│                        │
└── WSL (Ubuntu) ────────┤
    ├── Projekt Files    │
    └── docker commands ─┘
         ↓
    Docker Container (Recipe Assistant)
    Zugriff: localhost:8000 oder Tailscale-IP:8000
```

---

## Schritt 1: Docker Desktop Konfiguration prüfen

### 1.1 WSL Integration aktivieren

**In Docker Desktop (Windows):**
1. Öffne Docker Desktop
2. Klicke auf Einstellungen (Zahnrad oben rechts)
3. Gehe zu **Resources → WSL Integration**
4. Aktiviere: **Enable integration with my default WSL distro**
5. Aktiviere: Dein **Ubuntu** (sollte in der Liste sein)
6. Klicke **Apply & Restart**

### 1.2 In WSL testen

```bash
# Öffne WSL Ubuntu
wsl

# Prüfe Docker
docker --version
# Sollte zeigen: Docker version 24.x.x

# Prüfe Docker Compose
docker compose version
# Sollte zeigen: Docker Compose version v2.x.x

# Teste Docker
docker ps
# Sollte leer sein oder laufende Container zeigen
```

✅ Wenn alles funktioniert → **Docker ist bereit!**

❌ Wenn nicht funktioniert:
```bash
# Docker Desktop neu starten (in Windows)
# Dann WSL neu starten:
wsl --shutdown
wsl
```

---

## Schritt 2: Tailscale in WSL installieren

Du hast Tailscale auf Windows, aber wir brauchen es auch in WSL.

### 2.1 Tailscale in WSL installieren

```bash
# In WSL Ubuntu
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/jammy.noarmor.gpg | sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null

curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/jammy.tailscale-keyring.list | sudo tee /etc/apt/sources.list.d/tailscale.list

sudo apt update
sudo apt install tailscale
```

### 2.2 Tailscale in WSL starten

```bash
# Tailscale starten
sudo tailscale up

# Ein Link erscheint - öffne ihn im Browser
# Du wirst aufgefordert, dich anzumelden
# Nutze den GLEICHEN Account wie auf Windows
```

### 2.3 Tailscale-IP herausfinden

```bash
# Deine WSL Tailscale-IP
tailscale ip -4

# Beispiel-Ausgabe: 100.101.102.103
# MERKE DIR DIESE IP!
```

**Wichtig:** WSL bekommt eine **eigene** Tailscale-IP (unterschiedlich von Windows)!

---

## Schritt 3: Projekt vorbereiten

### 3.1 Dateien kopieren

Alle neuen Dateien müssen in dein Projekt:

```bash
# In WSL navigieren
cd /home/stephags/recipe-assistant

# Prüfe, welche Dateien da sind
ls -la

# Du solltest haben:
# - database.py
# - services.py
# - api.py
# - static/
# - requirements.txt
```

### 3.2 Neue Dateien hinzufügen

Kopiere diese Dateien in dein Projekt:
- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore`

**Entweder:**

**Option A: Über Windows Explorer**
```
1. Öffne Explorer: \\wsl$\Ubuntu\home\stephags\recipe-assistant
2. Kopiere Dateien rein
```

**Option B: In WSL erstellen**
```bash
cd /home/stephags/recipe-assistant

# Dockerfile erstellen
nano Dockerfile
# [Inhalt einfügen, Ctrl+O speichern, Ctrl+X beenden]

# docker-compose.yml erstellen
nano docker-compose.yml
# [Inhalt einfügen]

# .dockerignore erstellen
nano .dockerignore
# [Inhalt einfügen]
```

### 3.3 Ordner erstellen

```bash
# In deinem Projekt
cd /home/stephags/recipe-assistant

# Ordner für persistente Daten
mkdir -p data
mkdir -p users

# Prüfen
ls -la
# Sollte zeigen: data/ users/
```

### 3.4 .env Datei erstellen

```bash
# .env Datei erstellen
nano .env
```

Inhalt:
```env
ANTHROPIC_API_KEY=dein-api-key-hier
```

**Wichtig:** Ersetze `dein-api-key-hier` mit deinem echten API-Key!

Speichern: `Ctrl+O`, `Enter`, `Ctrl+X`

### 3.5 Berechtigungen setzen

```bash
# Sicherstellen, dass du Owner bist
sudo chown -R $USER:$USER /home/stephags/recipe-assistant

# .env Datei schützen
chmod 600 .env
```

---

## Schritt 4: Docker Image bauen

```bash
# Im Projekt-Verzeichnis
cd /home/stephags/recipe-assistant

# Image bauen (dauert 2-3 Minuten beim ersten Mal)
docker compose build

# Du solltest sehen:
# [+] Building ...
# => [internal] load build definition
# => => transferring dockerfile
# ...
# => exporting to image
# => => writing image sha256:...
```

✅ Wenn erfolgreich: "Successfully built" erscheint

❌ Wenn Fehler:
```bash
# Prüfe Dockerfile Syntax
cat Dockerfile

# Prüfe Docker läuft
docker ps

# Prüfe Logs
docker compose build --no-cache
```

---

## Schritt 5: Container starten

```bash
# Container im Hintergrund starten
docker compose up -d

# Ausgabe sollte sein:
# [+] Running 1/1
# ✔ Container recipe-assistant  Started
```

### 5.1 Prüfen ob läuft

```bash
# Status prüfen
docker compose ps

# Sollte zeigen:
# NAME              STATUS    PORTS
# recipe-assistant  Up        0.0.0.0:8000->8000/tcp
```

### 5.2 Logs ansehen

```bash
# Logs in Echtzeit
docker compose logs -f

# Du solltest sehen:
# INFO:     Started server process
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete.

# Logs beenden: Ctrl+C
```

---

## Schritt 6: Zugriff testen

### 6.1 Lokaler Zugriff (von Windows)

**In deinem Windows-Browser:**
```
http://localhost:8000
```

✅ Du solltest die Login-Seite sehen!

### 6.2 Tailscale-Zugriff (von überall)

**Deine Tailscale-IP finden:**
```bash
# In WSL
tailscale ip -4
# Beispiel: 100.101.102.103
```

**Von einem anderen Gerät im Tailscale-Netzwerk:**
```
http://100.101.102.103:8000
```

**Wichtig:** Das andere Gerät muss:
1. Tailscale installiert haben
2. Mit dem **gleichen Account** angemeldet sein

---

## Schritt 7: Tailscale auf anderen Geräten einrichten

### Auf deinem Handy:
1. Tailscale App installieren (iOS/Android)
2. Mit deinem Account anmelden
3. Browser öffnen: `http://100.101.102.103:8000`

### Auf einem Laptop:
1. Tailscale installieren: https://tailscale.com/download
2. Anmelden mit deinem Account
3. Browser öffnen: `http://100.101.102.103:8000`

### Auf einem Tablet:
Gleicher Prozess wie Handy

---

## Verwaltung

### Container verwalten

```bash
# Status prüfen
docker compose ps

# Logs ansehen
docker compose logs -f recipe-assistant

# Container stoppen
docker compose stop

# Container starten
docker compose start

# Container neu starten
docker compose restart

# Container stoppen und entfernen
docker compose down

# Container mit neuem Build starten
docker compose up -d --build
```

### Mit Docker Desktop (GUI)

1. Öffne Docker Desktop auf Windows
2. Gehe zu **Containers**
3. Du siehst `recipe-assistant`
4. Hier kannst du:
   - Logs ansehen
   - Container stoppen/starten
   - Terminal öffnen
   - Stats ansehen

---

## Backup & Restore

### Backup erstellen

```bash
# In WSL
cd /home/stephags/recipe-assistant

# Datenbank sichern
cp data/recipe_assistant.db data/backup-$(date +%Y%m%d).db

# Oder komplettes Backup
tar -czf recipe-backup-$(date +%Y%m%d).tar.gz data/ users/ .env

# Nach Windows kopieren
cp recipe-backup-*.tar.gz /mnt/c/Users/DEIN-USERNAME/Desktop/
```

### Restore

```bash
# Container stoppen
docker compose down

# Backup wiederherstellen
cp data/backup-20250223.db data/recipe_assistant.db

# Container starten
docker compose up -d
```

---

## Updates durchführen

### Code aktualisieren

```bash
cd /home/stephags/recipe-assistant

# Container stoppen
docker compose down

# Dateien aktualisieren (neue Versionen kopieren)
# Dann:

# Neu bauen
docker compose build

# Starten
docker compose up -d
```

### Dependencies aktualisieren

```bash
# requirements.txt bearbeiten
nano requirements.txt

# Neu bauen ohne Cache
docker compose build --no-cache

# Starten
docker compose up -d
```

---

## Troubleshooting

### Problem: Docker-Befehle funktionieren nicht in WSL

**Lösung:**
```bash
# Docker Desktop neu starten (Windows)
# WSL neu starten:
wsl --shutdown
# WSL wieder öffnen
wsl
```

### Problem: Port 8000 bereits belegt

**Prüfen:**
```bash
# In WSL
sudo lsof -i :8000
```

**Lösung 1:** Anderen Port nutzen
```yaml
# In docker-compose.yml ändern:
ports:
  - "8001:8000"  # Dann über localhost:8001 erreichbar
```

**Lösung 2:** Alten Prozess beenden
```bash
# PID aus lsof Ausgabe nehmen
kill -9 <PID>
```

### Problem: Tailscale verbindet nicht

```bash
# Status prüfen
sudo tailscale status

# Neu starten
sudo tailscale down
sudo tailscale up

# Neu anmelden (mit Link)
sudo tailscale up --reset
```

### Problem: Container startet nicht

```bash
# Logs ansehen
docker compose logs recipe-assistant

# Häufige Fehler:

# 1. API Key fehlt
docker compose exec recipe-assistant env | grep ANTHROPIC
# Lösung: .env Datei prüfen

# 2. Berechtigungen
sudo chown -R $USER:$USER data/ users/

# 3. Image kaputt
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Problem: Kann von anderem Gerät nicht zugreifen

**Prüfen:**
```bash
# 1. Ist Tailscale auf beiden Geräten mit gleichem Account?
tailscale status

# 2. Ist Container erreichbar?
curl http://localhost:8000/api/health

# 3. Firewall?
sudo ufw status
# Falls aktiv: sudo ufw allow 8000
```

### Problem: Datenbank-Fehler

```bash
# Container Terminal öffnen
docker compose exec recipe-assistant bash

# Datenbank prüfen
sqlite3 /data/recipe_assistant.db "PRAGMA integrity_check;"

# Oder: Backup wiederherstellen
exit
docker compose down
cp data/backup-DATE.db data/recipe_assistant.db
docker compose up -d
```

---

## Automatischer Start

### Nach Windows-Neustart

**Docker Desktop:**
- Einstellungen → General → **Start Docker Desktop when you log in** aktivieren

**Container:**
- `restart: unless-stopped` in docker-compose.yml sorgt dafür, dass Container automatisch starten

**Tailscale:**
- In WSL: `sudo systemctl enable tailscaled`

---

## Netzwerk-Übersicht

```
┌─────────────────────────────────────┐
│         Windows 11 Host             │
│                                     │
│  ┌──────────────┐  ┌─────────────┐ │
│  │ Docker       │  │  Tailscale  │ │
│  │ Desktop      │  │  (Windows)  │ │
│  └──────┬───────┘  └──────┬──────┘ │
│         │                  │        │
│  ┌──────▼──────────────────▼──────┐ │
│  │         WSL Ubuntu             │ │
│  │                                │ │
│  │  ┌──────────┐  ┌────────────┐ │ │
│  │  │Tailscale │  │  Docker    │ │ │
│  │  │(100.x.x) │  │  Container │ │ │
│  │  └────┬─────┘  └─────┬──────┘ │ │
│  │       │              │        │ │
│  │       └──────────────┤        │ │
│  │                      │        │ │
│  │       Recipe Assistant        │ │
│  │       :8000                   │ │
│  └──────────────────────────────┘ │
└─────────────────────────────────────┘

Zugriff:
1. Lokal (Windows): http://localhost:8000
2. Tailscale: http://100.x.x.x:8000
```

---

## Performance-Tipps für WSL

### WSL2 Speicher begrenzen

Erstelle: `C:\Users\DEIN-NAME\.wslconfig`

```ini
[wsl2]
memory=4GB
processors=2
swap=2GB
```

Dann WSL neu starten:
```powershell
# In PowerShell (Windows)
wsl --shutdown
wsl
```

### Docker Desktop Ressourcen

**In Docker Desktop:**
1. Settings → Resources
2. CPUs: 2-4
3. Memory: 4-6 GB
4. Swap: 1-2 GB

---

## Monitoring

### Simple Health-Check

```bash
# health-check.sh erstellen
nano ~/health-check.sh
```

```bash
#!/bin/bash
if curl -f -s http://localhost:8000/api/health > /dev/null; then
    echo "$(date): ✓ Recipe Assistant running"
else
    echo "$(date): ✗ Recipe Assistant down - restarting"
    cd /home/stephags/recipe-assistant
    docker compose restart
fi
```

```bash
# Ausführbar machen
chmod +x ~/health-check.sh

# Als Cronjob (alle 5 Minuten)
crontab -e
```

Füge hinzu:
```
*/5 * * * * /home/stephags/health-check.sh >> /tmp/recipe-health.log
```

---

## Cheat Sheet

```bash
# === Container Management ===
docker compose up -d          # Starten
docker compose down           # Stoppen
docker compose restart        # Neu starten
docker compose logs -f        # Logs ansehen
docker compose ps             # Status
docker compose exec recipe-assistant bash  # Shell

# === Tailscale ===
tailscale status              # Status
tailscale ip -4              # IP anzeigen
sudo tailscale up            # Starten
sudo tailscale down          # Stoppen

# === Backup ===
cp data/recipe_assistant.db data/backup-$(date +%Y%m%d).db

# === Updates ===
docker compose down
docker compose build --no-cache
docker compose up -d

# === Cleanup ===
docker system prune -a        # Alte Images löschen
docker volume prune          # Volumes löschen

# === WSL ===
wsl --shutdown               # WSL komplett neu starten
wsl                          # WSL öffnen
```

---

## Sicherheit

### 1. Firewall (optional)

```bash
# In WSL
sudo ufw enable
sudo ufw allow 8000
sudo ufw allow 41641/udp  # Tailscale
```

### 2. Nur Tailscale-Zugriff

```yaml
# In docker-compose.yml ändern:
ports:
  - "127.0.0.1:8000:8000"  # Nur localhost
```

Dann nur über Tailscale-IP erreichbar, nicht über localhost von anderen Geräten.

### 3. API-Key schützen

```bash
chmod 600 .env
echo ".env" >> .gitignore
```

---

## Zusammenfassung

**Was du gemacht hast:**
1. ✅ Docker Desktop nutzt WSL Integration
2. ✅ Tailscale in WSL installiert
3. ✅ Container läuft in Docker Desktop
4. ✅ Zugriff über localhost und Tailscale-IP

**Zugriff:**
- **Lokal**: http://localhost:8000
- **Remote**: http://100.x.x.x:8000 (Tailscale-IP)

**Verwaltung:**
- **CLI**: In WSL mit `docker compose`
- **GUI**: Docker Desktop auf Windows

**Das war's! 🎉**

Bei Fragen oder Problemen, schau in den Troubleshooting-Bereich oder die Logs:
```bash
docker compose logs -f
```
