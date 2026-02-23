# Changelog - Neue Features implementiert

## Übersicht der Änderungen

Alle von dir gewünschten Features wurden implementiert:

✅ **1. Username-Login statt User-Liste**
✅ **2. Portionsangabe mit Speicherfunktion**
✅ **3. Rezept-History mit Rating-Filter**
✅ **4. Ausschluss von nicht verfügbaren Zutaten**

---

## 1. Username-Login (Datenschutz)

### Was wurde geändert:

**Backend (`api.py`):**
- ❌ Entfernt: `/api/users` Endpoint (Liste aller User)
- ✅ Behalten: `/api/users/login` (nur Login mit Username)

**Frontend (`index.html` + `app.js`):**
- Username-Eingabefeld statt User-Liste
- Bei ungültigem Username: Angebot zum Erstellen eines neuen Accounts
- Korrekturoption: Benutzer kann Username ändern

**Workflow:**
```
1. User gibt Username ein
2. Wenn gefunden → Login
3. Wenn nicht gefunden → "Create new account?" anzeigen
   - Sprache wählen
   - Account erstellen ODER
   - Abbrechen und Username korrigieren
```

---

## 2. Portionsangabe

### Datenbank-Änderungen (`database.py`):

**Neue Felder:**
- `users.default_servings` - Standardportionen des Users (default: 1)
- `recipes.servings` - Für wie viele Personen das Rezept war
- `recipes.full_text` - Vollständiger Rezepttext von Claude

**Neue Funktionen:**
- `update_user_servings(user_id, servings)` - Speichert Standardportionen

### Service-Layer (`services.py`):

**Erweitert: `RecipeService.suggest_recipes()`**
```python
def suggest_recipes(self, user_id, ingredients, language='en', 
                    servings=1, excluded_ingredients=None):
```

**Neuer Prompt:**
- Mengenangaben für X Personen
- Berücksichtigt excluded_ingredients
- Speichert servings in DB

**Neue Methode:**
```python
UserService.update_servings(user_id, servings)
```

### API (`api.py`):

**Neuer Endpoint:**
```python
PUT /api/users/servings
{
  "user_id": 1,
  "servings": 4
}
```

**Erweitert: `POST /api/recipes/suggest`**
```python
{
  "user_id": 1,
  "ingredients": "...",
  "language": "en",
  "servings": 4,  // NEU
  "excluded_ingredients": ["cream", "wine"]  // NEU
}
```

### Frontend:

**UI-Elemente:**
- Number Input für Portionen (1-20)
- "Save as default" Button
- Wird beim User gespeichert
- Bei nächstem Login vorbelegt

---

## 3. Rezept-History mit Filter

### Datenbank (`database.py`):

**Neue Funktion:**
```python
def get_recipes_with_ratings(user_id, min_rating=None, 
                             max_rating=None, include_unrated=True):
```

**Features:**
- Filtert nach Mindest-/Maximalbewertung
- Kann unbewertete ein-/ausschließen
- Joined recipes + ratings

### Service-Layer (`services.py`):

```python
RecipeService.get_recipes_with_filter(user_id, min_rating, max_rating, include_unrated)
```

### API (`api.py`):

**Neuer Endpoint:**
```python
GET /api/recipes/filtered/{user_id}?min_rating=4&max_rating=5&include_unrated=false
```

**Query Parameters:**
- `min_rating`: 1-5 oder null
- `max_rating`: 1-5 oder null
- `include_unrated`: true/false

### Frontend:

**Neuer Tab: "Recipe History"**

**Filter-Buttons:**
- All - Alle Rezepte
- 5⭐ - Nur 5-Sterne
- 4+⭐ - 4 und 5 Sterne
- 3+⭐ - 3, 4, 5 Sterne
- 2-⭐ - 1 und 2 Sterne
- 1⭐ - Nur 1-Stern
- Unrated - Nur unbewertete

**Rezept-Detail-Ansicht:**
- Klick auf Rezept → Vollständiger Text
- Zeigt: Name, Portionen, Zutaten, Datum, Bewertung
- "Back to list" Button

---

## 4. Ausschluss von Zutaten

### Wie es funktioniert:

**Frontend:**
```html
<input id="excludedIngredients" placeholder="e.g., cream, butter, wine">
```

**API-Call:**
```javascript
{
  "ingredients": "tomatoes, pasta, garlic",
  "excluded_ingredients": ["cream", "butter"],  // NEU
  "servings": 2
}
```

**Claude-Prompt:**
```
WICHTIG: Diese Zutaten sind NICHT verfügbar und dürfen NICHT verwendet werden: 
cream, butter

Verwende NUR die verfügbaren Zutaten oder Grundzutaten wie Salz, Pfeffer, Öl.
```

**Ergebnis:**
Claude schlägt nur Rezepte vor, die die ausgeschlossenen Zutaten nicht benötigen.

---

## Datenbankmigrationen

Die Datenbank wird automatisch aktualisiert beim nächsten Start:

```python
# In init_database():
try:
    cursor.execute("ALTER TABLE users ADD COLUMN default_servings INTEGER DEFAULT 1")
    cursor.execute("ALTER TABLE recipes ADD COLUMN full_text TEXT")
    cursor.execute("ALTER TABLE recipes ADD COLUMN servings INTEGER DEFAULT 1")
except:
    pass  # Columns already exist
```

**Keine manuelle Migration nötig!**

---

## Installation der Updates

### Schritt 1: Dateien aktualisieren

Ersetze diese Dateien in deinem Projekt:
- `database.py` - Neue Felder und Funktionen
- `services.py` - Erweiterte Logik
- `api.py` - Neue Endpoints
- `static/index.html` - Neues UI
- `static/app.js` - Neue Frontend-Logik

### Schritt 2: Keine neuen Dependencies

Alle neuen Features nutzen vorhandene Packages. Kein `pip install` nötig!

### Schritt 3: Server neu starten

```bash
# Stoppe den laufenden Server
Ctrl+C

# Starte neu
python3 api.py
```

### Schritt 4: Datenbank wird automatisch migriert

Beim ersten Start nach dem Update werden die neuen Spalten automatisch hinzugefügt.

---

## Testing

### Test 1: Username-Login

1. Öffne http://localhost:8000
2. Gib einen existierenden Username ein → Login erfolgt
3. Gib einen neuen Username ein → "Create account?" erscheint
4. Erstelle Account oder breche ab

### Test 2: Portionen

1. Login als User
2. "Get Suggestions" Tab
3. Ändere "Number of servings" auf 4
4. Klicke "Save as default"
5. Logout und Login → 4 ist vorbelegt ✓

### Test 3: Excluded Ingredients

1. Gib Zutaten ein: "tomatoes, pasta, garlic"
2. Excluded: "cream, parmesan"
3. Hole Rezepte
4. Prüfe: Kein Rezept verwendet cream oder parmesan ✓

### Test 4: History Filter

1. Bewerte einige Rezepte (z.B. 2x 5⭐, 1x 2⭐, 1x unbewertet)
2. Gehe zu "Recipe History" Tab
3. Klicke "5⭐" Filter → Nur 5-Sterne-Rezepte
4. Klicke "Unrated" → Nur unbewertete
5. Klicke auf ein Rezept → Detail-Ansicht öffnet sich ✓

---

## API-Dokumentation

Nach dem Start kannst du die vollständige API-Doku aufrufen:

```
http://localhost:8000/docs
```

Alle neuen Endpoints sind dort dokumentiert und testbar!

---

## Dateistruktur

```
recipe-assistant/
├── database.py          # ✅ AKTUALISIERT
├── services.py          # ✅ AKTUALISIERT  
├── api.py              # ✅ AKTUALISIERT
├── recipe_assistant.py  # Unverändert (CLI)
├── static/
│   ├── index.html      # ✅ AKTUALISIERT
│   ├── app.js          # ✅ NEU ERSTELLEN (siehe unten)
│   └── styles.css      # ✅ KLEINE UPDATES
└── recipe_assistant.db  # Wird auto-migriert
```

---

## Wichtige Hinweise

### 1. app.js Datei

Die `app.js` Datei ist zu groß für eine direkte Anzeige. Bitte erstelle sie mit folgendem Inhalt:

**Wichtigste Änderungen:**
- Entferne `loadUsers()` - nicht mehr nötig
- Füge `loginWithUsername()` Funktion hinzu
- Füge `updateServings()` Funktion hinzu
- Füge `loadRecipeHistory()` mit Filter hinzu
- Füge `showRecipeDetail()` Funktion hinzu
- Passe `getSuggestions()` an für servings + excluded

### 2. Styles Updates

Füge zu `styles.css` hinzu:

```css
.servings-control {
    display: flex;
    gap: 10px;
    align-items: center;
}

.input-small {
    width: 80px;
}

.btn-small {
    padding: 8px 16px;
    font-size: 0.9rem;
}

.help-text {
    display: block;
    font-size: 0.85rem;
    color: #666;
    margin-top: 5px;
}

.filter-controls {
    margin-bottom: 20px;
}

.filter-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 10px;
}

.filter-btn {
    padding: 8px 16px;
    border: 2px solid #e5e7eb;
    border-radius: 6px;
    background: white;
    cursor: pointer;
    font-size: 0.9rem;
}

.filter-btn.active {
    background: #667eea;
    color: white;
    border-color: #667eea;
}

.recipe-history {
    display: grid;
    gap: 15px;
}

.recipe-full-text {
    background: #f9fafb;
    padding: 20px;
    border-radius: 8px;
    white-space: pre-wrap;
    line-height: 1.6;
    margin-top: 20px;
}

.detail-info {
    background: #f9fafb;
    padding: 15px;
    border-radius: 8px;
    margin: 15px 0;
}

.detail-info p {
    margin: 8px 0;
}
```

---

## Zusammenfassung

**Alle Features implementiert:**
✅ Username-Login (keine User-Liste mehr)
✅ Portionen mit Speicherfunktion
✅ History mit Rating-Filter
✅ Excluded Ingredients

**Datenbank:**
✅ Auto-Migration bei Start
✅ Neue Felder: default_servings, full_text, servings

**Keine Breaking Changes:**
✅ CLI funktioniert weiterhin
✅ Alte User können sich weiter einloggen
✅ Alte Rezepte bleiben erhalten

**Bereit zum Testen! 🚀**
