# VS Code Permission Error Fix

## Problem

```
PermissionError: [Errno 13] Permission denied: '/data'
```

**Ursache:** Der Code nutzt die Environment Variable `DATABASE_PATH=/data/recipe_assistant.db` (für Docker), aber lokal hast du keine Berechtigung für `/data`.

---

## Lösung 1: Environment Variablen in VS Code setzen (Empfohlen)

### Methode A: In launch.json

Aktualisiere `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Recipe Assistant",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/recipe_assistant.py",
            "console": "integratedTerminal",
            "env": {
                "ANTHROPIC_API_KEY": "${env:ANTHROPIC_API_KEY}",
                "DATABASE_PATH": "${workspaceFolder}/recipe_assistant.db",
                "USERS_DATA_PATH": "${workspaceFolder}/users"
            }
        },
        {
            "name": "Python: Web API",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/api.py",
            "console": "integratedTerminal",
            "env": {
                "ANTHROPIC_API_KEY": "${env:ANTHROPIC_API_KEY}",
                "DATABASE_PATH": "${workspaceFolder}/recipe_assistant.db",
                "USERS_DATA_PATH": "${workspaceFolder}/users"
            }
        }
    ]
}
```

### Methode B: In .env Datei

Erstelle `.env` im Projektverzeichnis:

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
DATABASE_PATH=./recipe_assistant.db
USERS_DATA_PATH=./users
```

Dann in VS Code Settings (`.vscode/settings.json`):

```json
{
    "python.envFile": "${workspaceFolder}/.env"
}
```

---

## Lösung 2: Shell Environment Variablen

### Temporär (nur für diese Session):

```bash
# Unset Docker-Pfade
unset DATABASE_PATH
unset USERS_DATA_PATH

# Oder explizit lokale Pfade setzen
export DATABASE_PATH="./recipe_assistant.db"
export USERS_DATA_PATH="./users"

# Dann in VS Code ausführen
code .
```

### Permanent in ~/.bashrc:

```bash
# Füge zu ~/.bashrc hinzu
echo 'export DATABASE_PATH="./recipe_assistant.db"' >> ~/.bashrc
echo 'export USERS_DATA_PATH="./users"' >> ~/.bashrc

# Neu laden
source ~/.bashrc
```

---

## Lösung 3: Code-Anpassung (bereits implementiert)

Die `database.py` wurde bereits angepasst und fällt automatisch auf lokale Pfade zurück wenn `/data` nicht verfügbar ist.

**Neue Logik:**
```python
if db_dir == '/data' and not os.path.exists(db_dir):
    print(f"Warning: Cannot access {db_dir}, using local directory instead")
    DB_FILE = 'recipe_assistant.db'
```

---

## Schnellste Lösung (30 Sekunden)

### Option A: Environment Variable löschen

```bash
# In Terminal (im VS Code)
unset DATABASE_PATH
unset USERS_DATA_PATH

# Python ausführen
python recipe_assistant.py
```

### Option B: Inline setzen

```bash
# In Terminal
DATABASE_PATH=./recipe_assistant.db USERS_DATA_PATH=./users python recipe_assistant.py

# Oder für API:
DATABASE_PATH=./recipe_assistant.db USERS_DATA_PATH=./users python api.py
```

---

## Empfohlene Konfiguration

### 1. Erstelle .env Datei:

```bash
cd ~/recipe-assistant

cat > .env << 'EOF'
# Anthropic API Key
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# Local paths (for VS Code / local development)
DATABASE_PATH=./recipe_assistant.db
USERS_DATA_PATH=./users

# Docker uses these instead (set in docker-compose.yml):
# DATABASE_PATH=/data/recipe_assistant.db
# USERS_DATA_PATH=/data/users
EOF
```

### 2. Aktualisiere .vscode/launch.json:

```bash
mkdir -p .vscode

cat > .vscode/launch.json << 'EOF'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: CLI",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/recipe_assistant.py",
            "console": "integratedTerminal",
            "envFile": "${workspaceFolder}/.env"
        },
        {
            "name": "Python: Web API",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/api.py",
            "console": "integratedTerminal",
            "envFile": "${workspaceFolder}/.env",
            "args": []
        }
    ]
}
EOF
```

### 3. Teste:

```bash
# CLI
python recipe_assistant.py

# API
python api.py
```

---

## Unterschiedliche Pfade: Docker vs. Lokal

### Docker (docker-compose.yml):
```yaml
environment:
  - DATABASE_PATH=/data/recipe_assistant.db
  - USERS_DATA_PATH=/data/users
volumes:
  - recipe-data:/data
```

### Lokal (.env):
```bash
DATABASE_PATH=./recipe_assistant.db
USERS_DATA_PATH=./users
```

### Automatische Erkennung:

Die Anwendung erkennt automatisch:
- Wenn `/data` verfügbar → Docker-Modus
- Wenn `/data` nicht verfügbar → Lokaler Modus (Fallback)

---

## .gitignore aktualisieren

Stelle sicher, dass `.env` nicht committed wird:

```bash
# .gitignore
.env
recipe_assistant.db
recipe_assistant.db-journal
users/
```

Erstelle `.env.example` für andere Entwickler:

```bash
# .env.example
ANTHROPIC_API_KEY=your-api-key-here
DATABASE_PATH=./recipe_assistant.db
USERS_DATA_PATH=./users
```

---

## Debugging in VS Code

### Mit .env Datei:

1. Drücke `F5` oder klicke auf "Run and Debug"
2. Wähle "Python: CLI" oder "Python: Web API"
3. Breakpoints werden beachtet
4. Environment Variablen aus `.env` werden geladen

### Ohne .env Datei (manuell):

Terminal in VS Code:
```bash
export DATABASE_PATH=./recipe_assistant.db
export USERS_DATA_PATH=./users
python recipe_assistant.py
```

---

## Troubleshooting

### Problem: "Still getting Permission denied"

```bash
# Prüfe aktuelle Environment Variablen
env | grep DATABASE
env | grep USERS

# Falls noch /data gesetzt ist:
unset DATABASE_PATH
unset USERS_DATA_PATH

# Oder überschreibe in Shell:
export DATABASE_PATH="$PWD/recipe_assistant.db"
export USERS_DATA_PATH="$PWD/users"
```

### Problem: ".env wird nicht geladen"

```bash
# Prüfe ob python-dotenv installiert ist
pip install python-dotenv

# In VS Code: Prüfe ob envFile in launch.json gesetzt ist
# "envFile": "${workspaceFolder}/.env"
```

### Problem: "Daten sind unterschiedlich in Docker vs. Lokal"

Das ist normal und gewollt:
- **Docker:** Daten in `/data` (via Volume)
- **Lokal:** Daten im Projektverzeichnis

Wenn du die gleichen Daten nutzen willst:

```bash
# Export aus Docker
docker cp recipe-assistant:/data/recipe_assistant.db ./recipe_assistant.db
docker cp recipe-assistant:/data/users ./users

# Oder umgekehrt - Import in Docker
docker cp ./recipe_assistant.db recipe-assistant:/data/
docker cp -r ./users recipe-assistant:/data/
```

---

## Best Practice Setup

### Dateistruktur:

```
recipe-assistant/
├── .env                    # Lokale Konfiguration (nicht in Git!)
├── .env.example           # Template für andere Entwickler
├── .gitignore             # .env ausschließen
├── database.py            # ✅ Bereits angepasst
├── api.py                 # ✅ Bereits angepasst
├── recipe_assistant.py    # ✅ Bereits angepasst
├── recipe_assistant.db    # Lokale Datenbank
├── users/                 # Lokale User-Daten
├── .vscode/
│   ├── launch.json       # Debug-Konfiguration mit .env
│   └── settings.json     # envFile aktiviert
└── docker-compose.yml    # Docker nutzt /data
```

### Workflow:

**Lokal entwickeln:**
```bash
# .env nutzt lokale Pfade
code .
# F5 drücken → Läuft lokal mit lokaler DB
```

**In Docker testen:**
```bash
# docker-compose.yml nutzt /data
docker-compose up -d
# Läuft in Docker mit Volume-DB
```

---

## Zusammenfassung

**Problem:** `/data` Verzeichnis nicht verfügbar außerhalb Docker

**Lösung:**
1. ✅ `database.py` angepasst (automatischer Fallback)
2. ✅ `.env` Datei mit lokalen Pfaden erstellen
3. ✅ VS Code `launch.json` auf `.env` verweisen

**Schnellste Fix:**
```bash
# Terminal in VS Code:
unset DATABASE_PATH
python recipe_assistant.py
```

**Nachhaltige Lösung:**
```bash
# .env erstellen
echo "DATABASE_PATH=./recipe_assistant.db" > .env
echo "USERS_DATA_PATH=./users" >> .env
echo "ANTHROPIC_API_KEY=dein-key" >> .env

# Fertig! F5 drücken in VS Code
```

**Jetzt sollte es funktionieren! 🚀**
