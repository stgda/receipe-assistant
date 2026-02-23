# Dockerfile für Recipe Assistant

FROM python:3.11-slim

# Arbeitsverzeichnis erstellen
WORKDIR /app

# System-Dependencies installieren
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Python-Dependencies installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendungscode kopieren
COPY database.py .
COPY services.py .
COPY api.py .
COPY recipe_assistant.py .

# Static files kopieren
COPY static/ ./static/

# Verzeichnisse für persistente Daten erstellen
RUN mkdir -p /data/users

# Umgebungsvariablen für Datenpfade setzen
ENV DATABASE_PATH=/data/recipe_assistant.db
ENV USERS_DATA_PATH=/data/users

# Container als non-root user ausführen (best practice)
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app /data
USER appuser

# Port freigeben
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health')" || exit 1

# Server starten
CMD ["python", "api.py"]
