# API Logging Feature - Implementierung

## Übersicht

Das API-Logging wurde wieder implementiert! Alle Anfragen an Claude und deren Antworten werden jetzt automatisch protokolliert.

## Was wurde hinzugefügt

### 1. Backend (services.py)

**Neue Funktionen:**

```python
def get_user_log_file(user_id):
    """Gibt den Log-Dateipfad für einen User zurück"""
    # Erstellt: users/{username}/api_log.json

def log_api_call(user_id, prompt, response, model):
    """Speichert API-Call in User's Log-Datei"""
    # Format: JSON mit timestamp, model, prompt, response
```

**Integration in RecipeService:**

```python
# Nach jedem Claude API Call:
response_text = message.content[0].text
log_api_call(user_id, prompt, response_text, model="claude-sonnet-4-20250514")
```

### 2. API Endpoint (api.py)

**Neuer Endpoint:**

```python
GET /api/logs/{user_id}?limit=10
```

**Response:**
```json
{
  "success": true,
  "logs": [
    {
      "timestamp": "2025-02-24T10:30:00",
      "model": "claude-sonnet-4-20250514",
      "prompt": "Du bist ein Koch-Assistent...",
      "response": "## Spaghetti Carbonara\n..."
    }
  ],
  "count": 5
}
```

### 3. Frontend

**Neuer Tab: "API Logs"**

- Zeigt alle API-Calls chronologisch (neueste zuerst)
- Expandable/Collapsible Content
- Refresh-Button
- Monospace-Font für bessere Lesbarkeit

**Features:**
- ✅ Automatisches Logging bei jedem API-Call
- ✅ Timestamp für jeden Call
- ✅ Prompt und Response vollständig anzeigbar
- ✅ Scroll bei langen Texten
- ✅ Expand/Collapse für Übersichtlichkeit

---

## Log-Datei Format

### Speicherort

**Lokal:**
```
users/
├── alice/
│   └── api_log.json
├── bob/
│   └── api_log.json
```

**Docker:**
```
/data/users/
├── alice/
│   └── api_log.json
├── bob/
│   └── api_log.json
```

### JSON-Struktur

```json
[
  {
    "timestamp": "2025-02-24T10:30:00.123456",
    "model": "claude-sonnet-4-20250514",
    "prompt": "Du bist ein hilfreicher Koch-Assistent...",
    "response": "## Spaghetti Carbonara\n\nZutaten:..."
  },
  {
    "timestamp": "2025-02-24T11:00:00.654321",
    "model": "claude-sonnet-4-20250514",
    "prompt": "You are a helpful cooking assistant...",
    "response": "## Tomato Soup\n\nIngredients:..."
  }
]
```

---

## Verwendung

### Im Web-Interface

1. **Logs anzeigen:**
   ```
   Web-App → API Logs Tab
   ```

2. **Log expandieren:**
   ```
   Klicke "Show more" unter Prompt oder Response
   ```

3. **Logs aktualisieren:**
   ```
   Klicke 🔄 Refresh Button
   ```

### Via API

```bash
# Alle Logs für User ID 1
curl http://localhost:8000/api/logs/1

# Nur letzte 5 Logs
curl http://localhost:8000/api/logs/1?limit=5
```

### Log-Datei direkt lesen

```bash
# Lokal
cat users/alice/api_log.json | jq

# Docker
docker exec recipe-assistant cat /data/users/alice/api_log.json | jq
```

---

## Installation / Update

### Dateien ersetzen:

1. ✅ `services.py` - Logging-Funktionen + Integration
2. ✅ `api.py` - Logs-Endpoint
3. ✅ `static/index.html` - Logs Tab
4. ✅ `static/app.js` - Logs-Funktionalität
5. ✅ `static/styles.css` - Logs-Styling

### Schritt 1: Dateien kopieren

```bash
cd ~/recipe-assistant

# Backups erstellen
cp services.py services.py.backup
cp api.py api.py.backup
cp static/index.html static/index.html.backup
cp static/app.js static/app.js.backup
cp static/styles.css static/styles.css.backup

# Neue Dateien kopieren
# (services.py, api.py, static/* aus dem Output)
```

### Schritt 2: Container/App neu starten

**Docker:**
```bash
docker-compose down
docker-compose up -d --build
```

**Lokal:**
```bash
# Stoppe App (Ctrl+C)
python3 api.py
```

### Schritt 3: Testen

```bash
# 1. Öffne Web-App
http://localhost:8000

# 2. Hole Rezeptvorschläge
Get Suggestions → Zutaten eingeben → Get Suggestions

# 3. Prüfe Logs
API Logs Tab → Logs werden angezeigt ✓

# 4. Log-Datei prüfen
cat users/[dein-username]/api_log.json
```

---

## Beispiel-Log

```json
[
  {
    "timestamp": "2025-02-24T15:30:45.123456",
    "model": "claude-sonnet-4-20250514",
    "prompt": "Du bist ein hilfreicher Koch-Assistent. Der Nutzer möchte ein Mittagessen kochen.\n\nVerfügbare Zutaten: Tomaten, Zwiebeln, Knoblauch, Pasta\nAnzahl Personen: 2 Personen\n\nBitte schlage 2-3 passende Rezepte vor...",
    "response": "## Spaghetti Aglio e Olio\n\n**Zutaten (für 2 Personen):**\n- 200g Spaghetti\n- 4 Knoblauchzehen\n- 4 EL Olivenöl\n- Salz, Pfeffer\n\n**Zubereitung:**\n1. Spaghetti kochen\n2. Knoblauch in Öl anbraten\n3. Pasta dazugeben\n4. Würzen und servieren\n\n**Zubereitungszeit:** 15 Minuten\n\n## Tomatensuppe\n\n**Zutaten (für 2 Personen):**\n- 500g Tomaten\n- 1 Zwiebel\n- 2 Knoblauchzehen\n- 400ml Gemüsebrühe\n\n**Zubereitung:**\n1. Zwiebel und Knoblauch andünsten\n2. Tomaten hinzufügen\n3. Mit Brühe ablöschen\n4. Pürieren\n\n**Zubereitungszeit:** 25 Minuten"
  }
]
```

---

## Features im Detail

### Automatisches Logging

**Wann wird geloggt:**
- ✅ Bei jedem Recipe Suggestion Request
- ✅ Bei jeder Claude API-Anfrage
- ✅ Unabhängig von Erfolg/Fehler

**Was wird geloggt:**
- ✅ Timestamp (ISO 8601 Format)
- ✅ Model Name
- ✅ Kompletter Prompt
- ✅ Komplette Response

### UI Features

**Log Entry:**
```
┌─────────────────────────────────────────┐
│ 24.02.2025, 15:30:45  claude-sonnet-4  │
├─────────────────────────────────────────┤
│ PROMPT                                  │
│ [Collapsed Text Preview]               │
│ [Show more]                            │
├─────────────────────────────────────────┤
│ RESPONSE                                │
│ [Collapsed Text Preview]               │
│ [Show more]                            │
└─────────────────────────────────────────┘
```

**Expand/Collapse:**
- Initial: Collapsed (erste 100px)
- Click "Show more": Expanded (full text, scrollable)
- Click "Show less": Collapsed wieder

---

## API-Dokumentation

### GET /api/logs/{user_id}

**Parameter:**
- `user_id` (path): User ID
- `limit` (query, optional): Max. Anzahl Logs

**Response:**
```json
{
  "success": true,
  "logs": [
    {
      "timestamp": "string (ISO 8601)",
      "model": "string",
      "prompt": "string",
      "response": "string"
    }
  ],
  "count": 5
}
```

**Beispiele:**
```bash
# Alle Logs
curl http://localhost:8000/api/logs/1

# Letzte 10 Logs
curl http://localhost:8000/api/logs/1?limit=10

# Via Tailscale
curl http://[hostname]:8000/api/logs/1
```

---

## Troubleshooting

### Problem: "Keine Logs sichtbar"

```bash
# Prüfe ob Log-Datei existiert
ls -la users/[username]/api_log.json

# Oder in Docker:
docker exec recipe-assistant ls -la /data/users/[username]/

# Falls nicht vorhanden:
# 1. Hole neue Rezeptvorschläge
# 2. Datei wird automatisch erstellt
```

### Problem: "Log-Datei leer"

```bash
# Prüfe Berechtigungen
ls -la users/[username]/

# Sollte lesbar/schreibbar sein
# Falls nicht:
chmod 755 users/[username]/
chmod 644 users/[username]/api_log.json
```

### Problem: "Fehler beim Laden der Logs"

```bash
# Prüfe Log-Datei Format
cat users/[username]/api_log.json | jq

# Bei JSON-Fehler: Datei reparieren oder löschen
mv users/[username]/api_log.json users/[username]/api_log.json.corrupt
# Neue Datei wird beim nächsten API-Call erstellt
```

### Problem: "Logs werden nicht angezeigt in UI"

1. **Browser Console öffnen** (F12)
2. **Fehler prüfen:**
   ```
   Failed to load logs: ...
   ```
3. **API direkt testen:**
   ```bash
   curl http://localhost:8000/api/logs/1
   ```

---

## Log-Rotation (Optional)

Für sehr lange Logs kannst du eine Rotation implementieren:

```bash
# backup-logs.sh
#!/bin/bash

USER_DIR="users"

for user in $USER_DIR/*; do
    LOG_FILE="$user/api_log.json"
    
    if [ -f "$LOG_FILE" ]; then
        # Größe prüfen (>5MB)
        SIZE=$(du -m "$LOG_FILE" | cut -f1)
        
        if [ $SIZE -gt 5 ]; then
            # Archivieren
            mv "$LOG_FILE" "$LOG_FILE.$(date +%Y%m%d)"
            # Neue Datei wird automatisch erstellt
        fi
    fi
done
```

---

## Zusammenfassung

**Was funktioniert:**
✅ Automatisches Logging bei jedem Claude API-Call
✅ User-spezifische Log-Dateien
✅ Web-UI mit expandable Logs
✅ API-Endpoint zum Abrufen
✅ Docker-kompatibel (persistente Volumes)

**Geänderte Dateien:**
- ✅ `services.py` - Logging-Funktionen
- ✅ `api.py` - Logs-Endpoint
- ✅ `static/index.html` - Logs Tab UI
- ✅ `static/app.js` - Logs-Funktionalität
- ✅ `static/styles.css` - Logs-Styling

**Installation:**
1. Dateien ersetzen
2. App/Container neu starten
3. Logs erscheinen automatisch bei API-Calls

**API-Logging ist wieder da! 📝**
