# Alternative Installation für ältere pip-Versionen

## Problem: `--break-system-packages` wird nicht erkannt

Das bedeutet, du hast eine ältere pip-Version. Hier sind mehrere Lösungen:

---

## Lösung 1: Ohne den Flag installieren (Einfachste Lösung)

```bash
pip install -r requirements.txt
```

Falls das funktioniert, bist du fertig! Falls du eine Fehlermeldung bekommst wie "externally-managed-environment", gehe zu Lösung 2.

---

## Lösung 2: Mit pip3 installieren

```bash
pip3 install -r requirements.txt
```

---

## Lösung 3: Mit --user Flag (Empfohlen für Ubuntu 22.04)

Installiert die Packages nur für deinen User, nicht systemweit:

```bash
pip install --user -r requirements.txt
```

oder

```bash
pip3 install --user -r requirements.txt
```

---

## Lösung 4: Virtual Environment nutzen (Beste Praxis!)

Das ist die professionellste Lösung und vermeidet alle Konflikte:

### 4.1 Virtual Environment erstellen

```bash
# Navigiere zu deinem Projekt
cd /pfad/zu/deinem/recipe-assistant

# Erstelle Virtual Environment
python3 -m venv venv
```

### 4.2 Virtual Environment aktivieren

```bash
# Aktivieren
source venv/bin/activate

# Dein Prompt sollte jetzt (venv) am Anfang zeigen
```

### 4.3 Packages installieren

```bash
# Jetzt ohne Flags installieren
pip install -r requirements.txt
```

### 4.4 Server starten

```bash
# Im aktivierten venv
python3 api.py
```

### 4.5 Virtual Environment deaktivieren (später)

```bash
deactivate
```

### 4.6 Bei jedem neuen Terminal

Immer zuerst aktivieren:
```bash
cd /pfad/zu/deinem/recipe-assistant
source venv/bin/activate
python3 api.py
```

---

## Lösung 5: Einzeln installieren

Falls nichts anderes funktioniert:

```bash
pip3 install anthropic
pip3 install fastapi
pip3 install uvicorn
pip3 install pydantic
```

oder mit --user:

```bash
pip3 install --user anthropic fastapi uvicorn pydantic
```

---

## Empfehlung für dein System (Ubuntu 22.04 in WSL)

**Ich empfehle Lösung 4 (Virtual Environment)**, weil:

✅ Keine Konflikte mit System-Packages
✅ Saubere Projektverwaltung
✅ Einfach zu löschen (einfach venv-Ordner löschen)
✅ Best Practice in der Python-Entwicklung

---

## Schnellanleitung: Virtual Environment Setup

```bash
# 1. Virtual Environment erstellen
cd ~/recipe-assistant
python3 -m venv venv

# 2. Aktivieren
source venv/bin/activate

# 3. pip upgraden (optional, aber gut)
pip install --upgrade pip

# 4. Requirements installieren
pip install -r requirements.txt

# 5. Prüfen
pip list

# 6. Server starten
python3 api.py

# Fertig! Browser öffnen: http://localhost:8000
```

---

## Virtual Environment in VS Code nutzen

Falls du VS Code nutzt:

1. Öffne VS Code im Projektordner: `code .`
2. `Ctrl+Shift+P` → "Python: Select Interpreter"
3. Wähle `./venv/bin/python`
4. Das integrierte Terminal nutzt jetzt automatisch dein venv!

---

## .gitignore aktualisieren

Wenn du das Virtual Environment nutzt, füge zu deiner `.gitignore` hinzu:

```bash
echo "venv/" >> .gitignore
```

---

## Troubleshooting

### "python3-venv is not installed"

```bash
sudo apt update
sudo apt install python3-venv
```

### "pip: command not found"

```bash
sudo apt install python3-pip
```

### Virtual Environment funktioniert nicht

```bash
# Lösche venv und erstelle neu
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Nach der Installation prüfen

```bash
# Prüfe ob alles installiert ist
python3 -c "import fastapi; print('FastAPI OK')"
python3 -c "import uvicorn; print('Uvicorn OK')"
python3 -c "import anthropic; print('Anthropic OK')"

# Wenn alle "OK" ausgeben, bist du ready!
```

---

## Zusammenfassung

**Probiere in dieser Reihenfolge:**

1. `pip install -r requirements.txt` (ohne Flags)
2. `pip3 install --user -r requirements.txt` (mit --user)
3. **Virtual Environment** (empfohlen, siehe oben)

Wähle die Methode, die bei dir funktioniert. Virtual Environment ist die beste langfristige Lösung!
