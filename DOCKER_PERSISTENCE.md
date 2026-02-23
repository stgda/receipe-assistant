# Docker Datenpersistenz - Vollständige Anleitung

## Problem: Daten gehen bei Container-Neustart verloren

**Ursache:** SQLite-Datenbank und User-Logs liegen im Container-Filesystem und werden beim Neustart gelöscht.

**Lösung:** Docker Volumes für persistente Datenspeicherung

---

## Schnelllösung (5 Minuten)

### 1. Aktualisiere deine Dateien

Ersetze diese Dateien in deinem Projekt:
- `docker-compose.yml` (NEU - mit Volumes)
- `Dockerfile` (AKTUALISIERT - mit Volume-Pfaden)
- `database.py` (AKTUALISIERT - nutzt Environment Variable)
- `api.py` (AKTUALISIERT - nutzt Environment Variable)
- `.dockerignore` (NEU)

### 2. Stoppe alte Container

```bash
docker-compose down
```

### 3. Baue neu und starte

```bash
# Mit docker-compose
docker-compose up -d --build

# Oder mit docker run
docker build -t recipe-assistant .
docker run -d \
  -p 8000:8000 \
  -e ANTHROPIC_API_KEY='dein-api-key' \
  -v recipe-data:/data \
  --name recipe-assistant \
  recipe-assistant
```

### 4. Teste Persistenz

```bash
# 1. Erstelle einen User und Daten im Browser
# 2. Stoppe Container:
docker-compose down

# 3. Starte neu:
docker-compose up -d

# 4. Öffne Browser - Daten sind noch da! ✓
```

---

## Wie funktioniert es?

### Docker Volumes Konzept

**Problem ohne Volumes:**
```
Container Filesystem
├── /app/recipe_assistant.db  ← Gelöscht bei Neustart!
└── /app/users/                ← Gelöscht bei Neustart!
```

**Lösung mit Volumes:**
```
Docker Host Filesystem
└── /var/lib/docker/volumes/recipe-data/
    ├── recipe_assistant.db    ← Bleibt erhalten!
    └── users/                 ← Bleibt erhalten!

Container Filesystem
└── /data/  → gemountet zu volume
    ├── recipe_assistant.db    ← Zeigt auf Host
    └── users/                 ← Zeigt auf Host
```

### Zwei Arten von Volumes

#### 1. Named Volumes (Empfohlen)
```yaml
volumes:
  - recipe-data:/data
```

**Vorteile:**
- ✅ Docker verwaltet den Speicherort
- ✅ Einfach zu backupen
- ✅ Portabel zwischen Systemen
- ✅ Gute Performance

**Speicherort:**
- Linux: `/var/lib/docker/volumes/recipe-data/_data/`
- Windows (WSL): `\\wsl$\docker-desktop-data\data\docker\volumes\recipe-data\_data`

#### 2. Bind Mounts
```yaml
volumes:
  - ./data:/data
```

**Vorteile:**
- ✅ Direkter Zugriff vom Host
- ✅ Einfacher zu finden

**Nachteile:**
- ❌ Schlechtere Performance
- ❌ Pfad-Probleme zwischen OS

---

## docker-compose.yml erklärt

```yaml
version: '3.8'

services:
  recipe-assistant:
    build: .
    container_name: recipe-assistant
    ports:
      - "8000:8000"
    
    environment:
      # API Key aus .env Datei oder Shell
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    
    volumes:
      # KRITISCH: Hier werden Daten persistent gespeichert
      - recipe-data:/data
      
      # Optional: Logs als Bind Mount
      # - ./logs:/app/logs
    
    # Container automatisch neu starten
    restart: unless-stopped
    
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/api/health')"]
      interval: 30s
      timeout: 3s
      retries: 3

# Named Volume Definition
volumes:
  recipe-data:
    driver: local
```

---

## Umgebungsvariablen

### Option 1: .env Datei (Empfohlen)

Erstelle `.env` im Projektverzeichnis:

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
DATABASE_PATH=/data/recipe_assistant.db
USERS_DATA_PATH=/data/users
```

```bash
docker-compose up -d
```

### Option 2: In Shell setzen

```bash
export ANTHROPIC_API_KEY='sk-ant-xxxxx'
docker-compose up -d
```

### Option 3: Direkt in docker-compose.yml

```yaml
environment:
  - ANTHROPIC_API_KEY=sk-ant-xxxxx  # NICHT für Produktion!
```

---

## Volume Management

### Volumes anzeigen

```bash
# Alle Volumes auflisten
docker volume ls

# Details eines Volumes
docker volume inspect recipe-data
```

**Output:**
```json
[
    {
        "Name": "recipe-data",
        "Driver": "local",
        "Mountpoint": "/var/lib/docker/volumes/recipe-data/_data",
        "Labels": {},
        "Scope": "local"
    }
]
```

### Volume Inhalt ansehen

```bash
# In Linux direkt:
sudo ls -la /var/lib/docker/volumes/recipe-data/_data/

# In WSL/Windows - über Container:
docker run --rm -v recipe-data:/data alpine ls -la /data

# Oder über laufenden Container:
docker exec -it recipe-assistant ls -la /data
```

### Volume Backup

```bash
# Backup erstellen
docker run --rm \
  -v recipe-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/recipe-data-backup.tar.gz -C /data .

# Backup wiederherstellen
docker run --rm \
  -v recipe-data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/recipe-data-backup.tar.gz -C /data
```

### Volume kopieren/migrieren

```bash
# Neues Volume erstellen
docker volume create recipe-data-new

# Daten kopieren
docker run --rm \
  -v recipe-data:/from \
  -v recipe-data-new:/to \
  alpine sh -c "cd /from && cp -av . /to"
```

### Volume löschen

```bash
# ACHTUNG: Löscht ALLE Daten!

# Container stoppen
docker-compose down

# Volume löschen
docker volume rm recipe-data

# ODER alles löschen (Container + Volumes)
docker-compose down -v
```

---

## Daten zwischen Host und Container austauschen

### Daten aus Container exportieren

```bash
# Datenbank exportieren
docker cp recipe-assistant:/data/recipe_assistant.db ./backup.db

# Gesamtes Datenverzeichnis
docker cp recipe-assistant:/data ./backup-data
```

### Daten in Container importieren

```bash
# Datenbank importieren
docker cp ./backup.db recipe-assistant:/data/recipe_assistant.db

# Oder: Container neu starten nach Import
docker-compose restart
```

---

## Verschiedene Deployment-Szenarien

### Szenario 1: Development (Bind Mount)

Für Entwicklung, wenn du direkten Zugriff brauchst:

```yaml
volumes:
  - ./data:/data        # Daten im Projektverzeichnis
  - ./logs:/app/logs    # Logs sichtbar
```

```bash
mkdir -p data logs
docker-compose up
```

**Vorteile:**
- Direkter Zugriff auf Daten
- Einfaches Debugging

### Szenario 2: Production (Named Volume)

Für Produktion:

```yaml
volumes:
  - recipe-data:/data   # Managed by Docker
```

**Vorteile:**
- Bessere Performance
- Automatisches Management

### Szenario 3: Shared Storage (NFS/CIFS)

Für mehrere Server:

```yaml
volumes:
  recipe-data:
    driver: local
    driver_opts:
      type: nfs
      o: addr=192.168.1.100,rw
      device: ":/path/to/share"
```

---

## Troubleshooting

### Problem: Volume ist leer nach Migration

```bash
# Prüfe ob Volume gemounted ist
docker inspect recipe-assistant | grep -A 10 Mounts

# Prüfe Volume-Inhalt
docker exec recipe-assistant ls -la /data

# Falls leer: Datenbank wird neu erstellt
# Importiere Backup (siehe oben)
```

### Problem: Permission Denied

```bash
# Volume-Permissions prüfen
docker exec recipe-assistant ls -la /data

# Ownership ändern (in Dockerfile bereits gesetzt)
docker exec -u root recipe-assistant chown -R appuser:appuser /data
```

### Problem: Datenbank locked

```bash
# Alte Prozesse killen
docker-compose down
docker volume ls  # Prüfe ob Volume existiert

# Clean restart
docker-compose up -d
```

### Problem: Volume nicht gefunden

```bash
# Volume existiert?
docker volume ls | grep recipe

# Neu erstellen
docker volume create recipe-data

# Container neu starten
docker-compose up -d
```

---

## Migration von bestehenden Daten

### Von lokalem System zu Docker

```bash
# 1. Stoppe lokalen Server
Ctrl+C

# 2. Erstelle Volume
docker volume create recipe-data

# 3. Kopiere Datenbank
docker run --rm \
  -v recipe-data:/data \
  -v $(pwd):/source \
  alpine cp /source/recipe_assistant.db /data/

# 4. Kopiere User-Daten
docker run --rm \
  -v recipe-data:/data \
  -v $(pwd):/source \
  alpine sh -c "cp -r /source/users /data/"

# 5. Starte Docker
docker-compose up -d
```

### Von altem Docker-Container zu neuem

```bash
# 1. Stoppe alten Container
docker stop old-recipe-assistant

# 2. Erstelle Backup
docker run --rm \
  -v old-volume:/source \
  -v recipe-data:/target \
  alpine sh -c "cp -r /source/. /target/"

# 3. Starte neuen Container
docker-compose up -d
```

---

## Best Practices

### 1. Regelmäßige Backups

Erstelle ein Backup-Script:

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

docker run --rm \
  -v recipe-data:/data \
  -v $(pwd)/$BACKUP_DIR:/backup \
  alpine tar czf /backup/recipe-data-$TIMESTAMP.tar.gz -C /data .

echo "Backup created: $BACKUP_DIR/recipe-data-$TIMESTAMP.tar.gz"

# Alte Backups löschen (älter als 30 Tage)
find $BACKUP_DIR -name "recipe-data-*.tar.gz" -mtime +30 -delete
```

Automatisieren mit Cron:
```bash
# Täglich um 3 Uhr morgens
0 3 * * * /path/to/backup.sh
```

### 2. Health Monitoring

```bash
# Container-Status prüfen
docker ps

# Logs ansehen
docker logs recipe-assistant

# Health-Status prüfen
docker inspect recipe-assistant | grep -A 5 Health
```

### 3. Volume-Größe überwachen

```bash
# Volume-Größe prüfen
docker system df -v

# Speicherplatz aufräumen (VORSICHT!)
docker system prune -a
```

---

## Cheat Sheet

```bash
# Container starten
docker-compose up -d

# Container stoppen (Daten bleiben!)
docker-compose down

# Container + Volumes löschen (DATEN GEHEN VERLOREN!)
docker-compose down -v

# Logs ansehen
docker-compose logs -f

# Neu bauen
docker-compose up -d --build

# In Container einsteigen
docker exec -it recipe-assistant bash

# Volume-Inhalt ansehen
docker exec recipe-assistant ls -la /data

# Backup erstellen
docker run --rm -v recipe-data:/data -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz -C /data .

# Backup wiederherstellen
docker run --rm -v recipe-data:/data -v $(pwd):/backup alpine tar xzf /backup/backup.tar.gz -C /data

# Volume-Details
docker volume inspect recipe-data

# Alle Volumes auflisten
docker volume ls
```

---

## Zusammenfassung

**Was wurde geändert:**
✅ `docker-compose.yml` - Volume hinzugefügt
✅ `Dockerfile` - Volume-Pfade konfiguriert
✅ `database.py` - Nutzt Environment Variable
✅ `api.py` - Nutzt Environment Variable
✅ `.dockerignore` - Lokale Daten ausschließen

**Ergebnis:**
✅ Daten bleiben nach Container-Neustart erhalten
✅ Datenbank persistiert in `/data/recipe_assistant.db`
✅ User-Daten persistieren in `/data/users/`
✅ Einfache Backups möglich

**Nächste Schritte:**
1. Dateien aktualisieren
2. `docker-compose down`
3. `docker-compose up -d --build`
4. Testen! 🚀
