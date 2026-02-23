# Tailscale Integration mit Docker - Vollständige Anleitung

## Problem: Tailscale-Zugriff funktioniert nicht mehr

**Ursache:** Docker-Container sind standardmäßig im eigenen Netzwerk isoliert und nicht über Tailscale erreichbar.

**Es gibt 3 Lösungen:**

---

## Lösung 1: Host Network Mode (Einfachste)

**Empfohlen für:** Einzelner Server, einfache Setup

Der Container nutzt das Host-Netzwerk direkt. Tailscale auf dem Host funktioniert dann automatisch.

### docker-compose.yml

```yaml
version: '3.8'

services:
  recipe-assistant:
    build: .
    container_name: recipe-assistant
    
    # WICHTIG: Host network mode
    network_mode: host
    
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    
    volumes:
      - recipe-data:/data
    
    restart: unless-stopped

volumes:
  recipe-data:
    driver: local
```

### Vorteile:
✅ Sehr einfach
✅ Tailscale muss nur auf Host installiert sein
✅ Keine Port-Mappings nötig

### Nachteile:
❌ Port 8000 muss auf Host frei sein
❌ Weniger Isolation

### Zugriff:
```
http://[tailscale-hostname]:8000
# z.B.: http://my-server:8000
```

---

## Lösung 2: Tailscale Sidecar Container (Empfohlen)

**Empfohlen für:** Bessere Isolation, mehrere Container

Der Recipe Assistant läuft in einem eigenen Tailscale-Netzwerk.

### docker-compose.yml

```yaml
version: '3.8'

services:
  # Tailscale Container
  tailscale:
    image: tailscale/tailscale:latest
    container_name: recipe-tailscale
    hostname: recipe-assistant  # Hostname in Tailscale
    environment:
      - TS_AUTHKEY=${TS_AUTHKEY}  # Einmalig für Anmeldung
      - TS_STATE_DIR=/var/lib/tailscale
      - TS_SERVE_CONFIG=/config/serve.json
      - TS_USERSPACE=false
    volumes:
      - tailscale-state:/var/lib/tailscale
      - /dev/net/tun:/dev/net/tun
      - ./tailscale-config:/config
    cap_add:
      - NET_ADMIN
      - SYS_MODULE
    restart: unless-stopped
    network_mode: host

  # Recipe Assistant
  recipe-assistant:
    build: .
    container_name: recipe-assistant
    depends_on:
      - tailscale
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - recipe-data:/data
    restart: unless-stopped
    # Mit Tailscale-Container verbinden
    network_mode: "service:tailscale"

volumes:
  recipe-data:
    driver: local
  tailscale-state:
    driver: local
```

### Tailscale Auth Key erstellen:

1. Gehe zu https://login.tailscale.com/admin/settings/keys
2. Erstelle einen Auth Key:
   - ✅ Reusable
   - ✅ Ephemeral (optional)
   - Expiration: 90 Tage (oder länger)
3. Kopiere den Key

### .env Datei:

```bash
ANTHROPIC_API_KEY=sk-ant-xxxxx
TS_AUTHKEY=tskey-auth-xxxxx  # Dein Tailscale Auth Key
```

### Zugriff:
```
http://recipe-assistant:8000
# Oder über Tailscale IP:
http://100.x.x.x:8000
```

---

## Lösung 3: Tailscale Serve (Modernste Lösung)

**Empfohlen für:** HTTPS, öffentlicher Zugriff innerhalb Tailnet

Nutzt Tailscale's eingebautes Serve/Funnel Feature.

### Schritt 1: docker-compose.yml

```yaml
version: '3.8'

services:
  recipe-assistant:
    build: .
    container_name: recipe-assistant
    network_mode: host
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - recipe-data:/data
    restart: unless-stopped

volumes:
  recipe-data:
    driver: local
```

### Schritt 2: Tailscale auf Host installieren

```bash
# Ubuntu/Debian
curl -fsSL https://tailscale.com/install.sh | sh

# Starten
sudo tailscale up

# Serve konfigurieren (macht Port 8000 über Tailscale verfügbar)
sudo tailscale serve --bg --https 8000 http://localhost:8000
```

### Zugriff:
```
https://[your-tailscale-hostname].ts.net
# z.B.: https://my-server.tail12345.ts.net
```

### Vorteile:
✅ Automatisches HTTPS
✅ Schöne URLs
✅ Einfach zu teilen im Tailnet

---

## Schnellstart: Lösung 1 (Host Network)

### 1. docker-compose.yml aktualisieren

```yaml
version: '3.8'

services:
  recipe-assistant:
    build: .
    container_name: recipe-assistant
    network_mode: host  # <-- HINZUFÜGEN
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - recipe-data:/data
    restart: unless-stopped

volumes:
  recipe-data:
    driver: local
```

### 2. Container neu starten

```bash
docker-compose down
docker-compose up -d --build
```

### 3. Testen

```bash
# Auf dem Server:
curl http://localhost:8000/api/health

# Von anderem Gerät im Tailnet:
curl http://[tailscale-hostname]:8000/api/health
# z.B.: http://my-server:8000/api/health
```

---

## Schnellstart: Lösung 2 (Sidecar - Empfohlen)

### 1. Auth Key erstellen

- Gehe zu: https://login.tailscale.com/admin/settings/keys
- Erstelle "Auth key"
- Kopiere den Key

### 2. .env Datei erstellen

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-xxxxx
TS_AUTHKEY=tskey-auth-xxxxx
```

### 3. docker-compose.yml

```yaml
version: '3.8'

services:
  tailscale:
    image: tailscale/tailscale:latest
    container_name: recipe-tailscale
    hostname: recipe-assistant
    environment:
      - TS_AUTHKEY=${TS_AUTHKEY}
      - TS_STATE_DIR=/var/lib/tailscale
    volumes:
      - tailscale-state:/var/lib/tailscale
      - /dev/net/tun:/dev/net/tun
    cap_add:
      - NET_ADMIN
      - SYS_MODULE
    restart: unless-stopped
    network_mode: host

  recipe-assistant:
    build: .
    container_name: recipe-assistant
    depends_on:
      - tailscale
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - recipe-data:/data
    restart: unless-stopped
    network_mode: "service:tailscale"

volumes:
  recipe-data:
    driver: local
  tailscale-state:
    driver: local
```

### 4. Starten

```bash
docker-compose up -d --build
```

### 5. In Tailscale Admin prüfen

- Gehe zu https://login.tailscale.com/admin/machines
- Du solltest "recipe-assistant" sehen
- Kopiere die Tailscale IP (100.x.x.x)

### 6. Zugriff testen

```bash
# Von jedem Gerät im Tailnet:
http://recipe-assistant:8000
# Oder:
http://100.x.x.x:8000
```

---

## Vergleich der Lösungen

| Feature | Host Network | Sidecar | Serve |
|---------|-------------|---------|-------|
| **Einfachheit** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Isolation** | ❌ | ✅ | ✅ |
| **HTTPS** | ❌ | ❌ | ✅ |
| **Dedizierter Hostname** | Host | ✅ | ✅ |
| **Multi-Container** | ❌ | ✅ | ✅ |
| **Setup-Zeit** | 1 Min | 5 Min | 2 Min |

---

## Troubleshooting

### Problem: "Cannot connect via Tailscale"

**Prüfe Tailscale Status:**
```bash
# Auf dem Host
sudo tailscale status

# Sollte zeigen:
# 100.x.x.x   your-host    youruser@   linux   -
```

**Prüfe Container:**
```bash
# Ist Container erreichbar?
docker exec recipe-assistant curl http://localhost:8000/api/health

# Bei Sidecar: Prüfe Tailscale Container
docker logs recipe-tailscale
```

### Problem: "Auth key expired"

```bash
# Neuen Auth Key erstellen
# https://login.tailscale.com/admin/settings/keys

# In .env aktualisieren
TS_AUTHKEY=tskey-auth-NEUER-KEY

# Container neu starten
docker-compose down
docker-compose up -d
```

### Problem: "Port 8000 already in use" (Host Network)

```bash
# Prüfe welcher Prozess Port 8000 nutzt
sudo lsof -i :8000

# Stoppe anderen Prozess oder ändere Port in api.py:
# uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Problem: "Container kann nicht auf Tailscale zugreifen" (Sidecar)

```bash
# Prüfe /dev/net/tun
ls -la /dev/net/tun

# Falls nicht vorhanden:
sudo mkdir -p /dev/net
sudo mknod /dev/net/tun c 10 200
sudo chmod 666 /dev/net/tun
```

### Problem: "Tailscale in Admin nicht sichtbar"

```bash
# Prüfe Logs
docker logs recipe-tailscale

# Manuelle Anmeldung (einmalig)
docker exec -it recipe-tailscale tailscale up --authkey=$TS_AUTHKEY
```

---

## Erweiterte Konfiguration

### Tailscale Funnel (Öffentlicher Zugriff)

Mit Funnel kann dein Service sogar öffentlich (außerhalb Tailnet) erreichbar sein:

```bash
# Auf dem Host
sudo tailscale funnel --bg --https 8000 http://localhost:8000

# Service ist jetzt öffentlich unter:
# https://your-tailscale-hostname.ts.net
```

**ACHTUNG:** Nur aktivieren wenn du öffentlichen Zugriff willst!

### Mehrere Services mit Tailscale

```yaml
version: '3.8'

services:
  tailscale:
    image: tailscale/tailscale:latest
    container_name: tailscale
    hostname: myservices
    environment:
      - TS_AUTHKEY=${TS_AUTHKEY}
      - TS_STATE_DIR=/var/lib/tailscale
    volumes:
      - tailscale-state:/var/lib/tailscale
      - /dev/net/tun:/dev/net/tun
    cap_add:
      - NET_ADMIN
      - SYS_MODULE
    restart: unless-stopped
    network_mode: host

  recipe-assistant:
    build: .
    container_name: recipe-assistant
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - recipe-data:/data
    restart: unless-stopped
    network_mode: "service:tailscale"
    # Port 8000

  nginx:
    image: nginx:alpine
    container_name: nginx-proxy
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    network_mode: "service:tailscale"
    # Port 80/443

volumes:
  recipe-data:
  tailscale-state:
```

### ACL für bessere Sicherheit

In Tailscale Admin (https://login.tailscale.com/admin/acls):

```json
{
  "acls": [
    {
      "action": "accept",
      "src": ["tag:mobile", "your-email@example.com"],
      "dst": ["tag:recipe-assistant:8000"]
    }
  ],
  "tagOwners": {
    "tag:recipe-assistant": ["your-email@example.com"]
  }
}
```

---

## Monitoring

### Healthcheck mit Tailscale

```yaml
recipe-assistant:
  # ...
  healthcheck:
    test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/api/health')"]
    interval: 30s
    timeout: 3s
    retries: 3
    start_period: 10s
```

### Logs überwachen

```bash
# Recipe Assistant Logs
docker logs -f recipe-assistant

# Tailscale Logs
docker logs -f recipe-tailscale

# Beide gleichzeitig
docker-compose logs -f
```

---

## Backup mit Tailscale

### Remote Backup über Tailscale

```bash
# Von lokalem Computer (im Tailnet)
scp user@tailscale-hostname:/pfad/zu/backup.tar.gz ./

# Oder mit Docker direkt:
ssh user@tailscale-hostname 'docker run --rm -v recipe-data:/data alpine tar czf - -C /data .' > backup.tar.gz
```

---

## Empfehlung

**Für dich empfehle ich Lösung 1 (Host Network):**

```yaml
version: '3.8'

services:
  recipe-assistant:
    build: .
    container_name: recipe-assistant
    network_mode: host
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - recipe-data:/data
    restart: unless-stopped

volumes:
  recipe-data:
    driver: local
```

**Warum?**
- ✅ Sehr einfach
- ✅ Tailscale läuft bereits auf deinem Host
- ✅ Kein zusätzlicher Container nötig
- ✅ Funktioniert sofort

**Nächste Schritte:**
1. Füge `network_mode: host` zur docker-compose.yml hinzu
2. Entferne `ports: - "8000:8000"` (nicht mehr nötig)
3. `docker-compose up -d --build`
4. Zugriff über `http://[dein-tailscale-hostname]:8000`

---

## Cheat Sheet

```bash
# Container mit Host Network starten
docker-compose up -d

# Tailscale Status prüfen
sudo tailscale status

# Von anderem Gerät testen
curl http://[tailscale-hostname]:8000/api/health

# Tailscale IP herausfinden
tailscale ip -4

# Logs ansehen
docker logs -f recipe-assistant

# Container neu starten
docker-compose restart
```

**Fertig! Tailscale funktioniert wieder! 🎉**
