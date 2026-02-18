# Web Interface Installation Guide

## Schritt-für-Schritt Anleitung für Ubuntu 22.04 (WSL unter Windows 11)

### Übersicht

Du erweiterst dein Recipe Assistant Projekt um ein modernes Web-Interface. Das Interface nutzt:
- **Backend**: FastAPI (Python Web Framework)
- **Frontend**: Vanilla JavaScript, HTML, CSS
- **Architektur**: Bereits vorhandene Service-Layer

---

## Schritt 1: Projekt-Vorbereitung

### 1.1 Öffne dein WSL Terminal

```bash
# In Windows: Öffne PowerShell oder Windows Terminal
wsl

# Navigiere zu deinem Projekt
cd /pfad/zu/deinem/recipe-assistant
```

### 1.2 Prüfe deine aktuelle Projektstruktur

```bash
ls -la
```

Du solltest sehen:
- `database.py`
- `services.py`
- `recipe_assistant.py`
- `requirements.txt`
- `users/` (Verzeichnis)
- `recipe_assistant.db`

---

## Schritt 2: Neue Dateien hinzufügen

### 2.1 Erstelle die API-Datei

```bash
# Kopiere den Inhalt aus der bereitgestellten api.py Datei
nano api.py
```

Füge den kompletten Inhalt von `api.py` ein, speichere mit `Ctrl+O`, `Enter`, `Ctrl+X`.

### 2.2 Erstelle das Static-Verzeichnis

```bash
# Erstelle Verzeichnis für Frontend-Dateien
mkdir -p static
```

### 2.3 Erstelle die Frontend-Dateien

```bash
# HTML-Datei
nano static/index.html
# Füge den Inhalt ein, speichern und schließen

# CSS-Datei
nano static/styles.css
# Füge den Inhalt ein, speichern und schließen

# JavaScript-Datei
nano static/app.js
# Füge den Inhalt ein, speichern und schließen
```

**Alternative (einfacher):**
Wenn du die Dateien bereits auf deinem Windows-System hast:
```bash
# Von Windows aus ins WSL kopieren
# In PowerShell (auf Windows):
cp api.py \\wsl$\Ubuntu\home\DEIN_USERNAME\recipe-assistant\
cp -r static \\wsl$\Ubuntu\home\DEIN_USERNAME\recipe-assistant\
```

### 2.4 Prüfe die neue Projektstruktur

```bash
tree -L 2
```

Sollte jetzt so aussehen:
```
recipe-assistant/
├── api.py                    # NEU: Web API Server
├── database.py
├── services.py
├── recipe_assistant.py
├── requirements.txt
├── recipe_assistant.db
├── users/
└── static/                   # NEU: Frontend
    ├── index.html
    ├── styles.css
    └── app.js
```

---

## Schritt 3: Dependencies installieren

### 3.1 Aktualisiere requirements.txt

```bash
nano requirements.txt
```

Stelle sicher, dass der Inhalt so aussieht:
```
anthropic>=0.18.0
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.0.0
```

### 3.2 Installiere die neuen Packages

```bash
# Installiere FastAPI und Uvicorn
pip install -r requirements.txt --break-system-packages
```

**Wichtig**: Der `--break-system-packages` Flag ist für Ubuntu 22.04 nötig.

### 3.3 Verifiziere die Installation

```bash
# Prüfe ob FastAPI installiert ist
python3 -c "import fastapi; print(f'FastAPI {fastapi.__version__}')"

# Prüfe ob Uvicorn installiert ist
python3 -c "import uvicorn; print(f'Uvicorn {uvicorn.__version__}')"
```

Du solltest die Versionsnummern sehen (z.B. "FastAPI 0.104.1").

---

## Schritt 4: Starte den Web-Server

### 4.1 Stelle sicher, dass dein API-Key gesetzt ist

```bash
# Prüfe ob API-Key vorhanden ist
echo $ANTHROPIC_API_KEY

# Falls nicht gesetzt:
export ANTHROPIC_API_KEY='dein-api-key-hier'
```

### 4.2 Starte den Server

```bash
# Starte den FastAPI Server
python3 api.py
```

Du solltest sehen:
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 4.3 Alternative: Mit Uvicorn direkt starten

```bash
# Mit Auto-Reload (entwickelt wird)
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Ohne Auto-Reload (produktiv)
uvicorn api:app --host 0.0.0.0 --port 8000
```

---

## Schritt 5: Öffne das Web-Interface

### 5.1 Im Browser öffnen

**Vom WSL aus (innerhalb Ubuntu):**
```
http://localhost:8000
```

**Von Windows aus (außerhalb WSL):**
```
http://localhost:8000
```

**Von einem anderen Gerät im Netzwerk:**
```
http://[DEINE-WSL-IP]:8000
```

Um deine WSL IP zu finden:
```bash
# In WSL:
hostname -I
# Oder:
ip addr show eth0 | grep inet
```

### 5.2 Teste das Interface

1. **User Selection**: Du solltest die Login-Seite sehen
2. **Erstelle einen User** oder wähle einen bestehenden
3. **Get Suggestions**: Gib Zutaten ein und klicke "Get Suggestions"
4. **Give Feedback**: Bewerte ein Rezept
5. **Preferences**: Sieh dir deine Statistiken an

---

## Schritt 6: Troubleshooting

### Problem: "Port already in use"

```bash
# Finde den Prozess auf Port 8000
lsof -i :8000

# Beende den Prozess
kill -9 [PID]

# Oder nutze einen anderen Port
python3 api.py --port 8001
```

### Problem: "ANTHROPIC_API_KEY not found"

```bash
# Setze den Key permanent
echo 'export ANTHROPIC_API_KEY="dein-key"' >> ~/.bashrc
source ~/.bashrc
```

### Problem: "Cannot connect from Windows browser"

```bash
# Prüfe Windows Firewall
# In PowerShell (als Administrator):
New-NetFirewallRule -DisplayName "WSL2 Port 8000" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow

# Oder nutze Port-Forwarding:
netsh interface portproxy add v4tov4 listenport=8000 listenaddress=0.0.0.0 connectport=8000 connectaddress=[WSL-IP]
```

### Problem: "Module not found"

```bash
# Installiere fehlende Module
pip install fastapi uvicorn pydantic --break-system-packages

# Oder nutze Virtual Environment:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Problem: "Database is locked"

```bash
# Stelle sicher, dass die CLI-Version nicht läuft
ps aux | grep recipe_assistant

# Beende alte Prozesse
pkill -f recipe_assistant
```

---

## Schritt 7: Als Service einrichten (Optional)

### 7.1 Erstelle Systemd Service

```bash
sudo nano /etc/systemd/system/recipe-assistant.service
```

Inhalt:
```ini
[Unit]
Description=Recipe Assistant API
After=network.target

[Service]
Type=simple
User=DEIN_USERNAME
WorkingDirectory=/home/DEIN_USERNAME/recipe-assistant
Environment="ANTHROPIC_API_KEY=dein-api-key"
ExecStart=/usr/bin/python3 /home/DEIN_USERNAME/recipe-assistant/api.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 7.2 Aktiviere den Service

```bash
# Lade Systemd neu
sudo systemctl daemon-reload

# Starte den Service
sudo systemctl start recipe-assistant

# Aktiviere Autostart
sudo systemctl enable recipe-assistant

# Prüfe Status
sudo systemctl status recipe-assistant
```

---

## Schritt 8: Produktiv-Deployment (Optional)

### 8.1 Mit Nginx als Reverse Proxy

```bash
# Installiere Nginx
sudo apt update
sudo apt install nginx

# Erstelle Config
sudo nano /etc/nginx/sites-available/recipe-assistant
```

Inhalt:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Aktiviere Site
sudo ln -s /etc/nginx/sites-available/recipe-assistant /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 8.2 Mit SSL (HTTPS)

```bash
# Installiere Certbot
sudo apt install certbot python3-certbot-nginx

# Hole SSL Zertifikat
sudo certbot --nginx -d your-domain.com
```

---

## Schritt 9: Entwicklungs-Workflow

### 9.1 Entwicklung mit Auto-Reload

```bash
# Terminal 1: Starte API mit Reload
uvicorn api:app --reload

# Terminal 2: Öffne Editor
code .  # VS Code
# oder
nano api.py
```

Änderungen werden automatisch neu geladen!

### 9.2 Logs ansehen

```bash
# Server-Logs in Echtzeit
tail -f nohup.out

# Oder wenn als Service:
sudo journalctl -u recipe-assistant -f
```

### 9.3 API-Dokumentation

Öffne im Browser:
```
http://localhost:8000/docs
```

Du siehst die **interaktive API-Dokumentation** (Swagger UI)!

---

## Schritt 10: Beide Interfaces parallel nutzen

### CLI-Version weiterhin nutzen:

```bash
# Terminal 1: Web-Server läuft
python3 api.py

# Terminal 2: CLI nutzen
python3 recipe_assistant.py
```

**Wichtig**: Beide teilen sich die gleiche Datenbank!

---

## Zusammenfassung: Was du jetzt hast

✅ **Web-Interface**: Moderne Browser-basierte UI
✅ **REST API**: FastAPI Backend
✅ **Service Layer**: Wiederverwendbare Business-Logik
✅ **Datenbank**: SQLite mit allen User/Recipe/Rating Daten
✅ **CLI**: Funktioniert weiterhin parallel
✅ **Multi-User**: Mehrere Benutzer gleichzeitig möglich
✅ **Multi-Language**: Deutsch und Englisch

---

## Nächste Schritte (Optional)

1. **Mobile App**: React Native oder Flutter
2. **Authentication**: JWT Tokens für Sicherheit
3. **Cloud Deployment**: AWS, Google Cloud, Heroku
4. **Docker**: Containerisierung für einfaches Deployment
5. **Tests**: Unit Tests und Integration Tests

---

## Cheat Sheet: Wichtige Befehle

```bash
# Server starten
python3 api.py

# Mit Auto-Reload
uvicorn api:app --reload

# Auf anderem Port
uvicorn api:app --port 8080

# Server stoppen
Ctrl+C

# Im Hintergrund starten
nohup python3 api.py &

# Prozess finden
ps aux | grep api.py

# Prozess beenden
pkill -f api.py

# API-Dokumentation öffnen
firefox http://localhost:8000/docs
```

---

## Support & Hilfe

Bei Problemen:
1. Prüfe die Logs: `tail -f nohup.out`
2. Teste die API: `http://localhost:8000/api/health`
3. Öffne die API-Docs: `http://localhost:8000/docs`
4. Prüfe die Browser-Konsole: F12 → Console

**Viel Erfolg mit deinem Web-Interface! 🚀**
