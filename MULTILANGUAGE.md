# Multi-Language Support Documentation

## Overview

The Recipe Assistant now supports multiple languages. Currently supported:
- **English** (en)
- **German** (de)

## How It Works

### For Users

1. **New User Creation:**
   - When creating a new user, you'll be asked to select a language
   - Choice: 1 for English, 2 for German
   - This preference is saved with your user profile

2. **Existing Users:**
   - Your language preference is automatically loaded
   - All interactions use your selected language
   - No need to select language again on subsequent runs

3. **Language Consistency:**
   - Recipe suggestions from Claude are in your language
   - All UI messages are in your language
   - API logs preserve the original language used

### Example Flow

```
🍳  Welcome to the AI Recipe Assistant!
🍳  Willkommen beim KI-Rezept-Assistenten!

👤  User Selection / Benutzerauswahl

Existing users / Existierende Benutzer:
1. alice (English)
2. bob (Deutsch)
3. Create new user / Neuen Benutzer erstellen

Select user / Benutzer auswählen (1-3): 3

Enter username: charlie

Select your language / Wähle deine Sprache:
1. English
2. Deutsch

Your choice / Deine Wahl (1-2): 1

✓ Language preference saved!
✓ Logged in as: charlie
```

## For Developers

### Architecture

The multi-language system uses a centralized translation dictionary:

```python
TRANSLATIONS = {
    "en": {
        "welcome": "Welcome to the AI Recipe Assistant!",
        # ... more translations
    },
    "de": {
        "welcome": "Willkommen beim KI-Rezept-Assistenten!",
        # ... more translations
    }
}
```

### Translation Function

```python
def t(lang, key):
    """Get translation for a key in specified language"""
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)
```

Usage in code:
```python
print(t(lang, "welcome"))  # Prints in user's language
```

### Language Storage

Language preference is stored in each user's `preferences.json`:

```json
{
    "language": "de",
    "liked_dishes": [],
    "disliked_dishes": [],
    ...
}
```

### Claude API Prompts

Recipe suggestions use language-specific prompts:
- English users get English prompts → English recipes
- German users get German prompts → German recipes

The prompt template is stored in translations:
```python
"claude_prompt_ingredients": "You are a helpful cooking assistant..."  // English
"claude_prompt_ingredients": "Du bist ein hilfreicher Koch-Assistent..."  // German
```

## Adding New Languages

### Step 1: Add Translation Dictionary

Add a new language code to `TRANSLATIONS`:

```python
TRANSLATIONS = {
    "en": { ... },
    "de": { ... },
    "es": {  # Spanish
        "welcome": "¡Bienvenido al Asistente de Recetas de IA!",
        "user_selection": "Selección de Usuario",
        # ... add all keys from en/de
    }
}
```

### Step 2: Update Language Selection

In `select_or_create_user()`, add the new option:

```python
print("\nSelect your language / Wähle deine Sprache / Selecciona tu idioma:")
print("1. English")
print("2. Deutsch")
print("3. Español")  # Add this

while True:
    lang_choice = int(input("\nYour choice (1-3): "))
    if lang_choice == 1:
        language = "en"
    elif lang_choice == 2:
        language = "de"
    elif lang_choice == 3:  # Add this
        language = "es"
    # ...
```

### Step 3: Test Thoroughly

- Create a new user with the new language
- Test all menu options
- Verify Claude responds in the correct language
- Check that all UI messages display correctly

### Translation Keys Reference

All translation keys can be found in the `TRANSLATIONS` dictionary. Key categories:

- **UI Navigation:** welcome, user_selection, option_1-4, etc.
- **Ingredient Input:** available_ingredients, your_ingredients, etc.
- **Feedback:** feedback_for, rating_1-5, how_liked, etc.
- **Preferences:** your_preferences, dishes_liked, etc.
- **API Log:** api_log, entries, prompt, response, etc.
- **Claude Prompts:** claude_prompt_ingredients, pref_dishes_liked, etc.

### Best Practices

1. **Keep Keys Consistent:** All languages must have the same keys
2. **Test Edge Cases:** Empty responses, special characters, etc.
3. **Cultural Adaptation:** Not just translation - adapt examples to culture
4. **Maintain Parity:** Add new features to all languages simultaneously
5. **Comments in English:** Keep code comments in English for consistency

## Backward Compatibility

Existing user profiles without language preference:
- Automatically default to English (`"language": "en"`)
- No data migration needed
- Users can be migrated by editing their `preferences.json`

## Known Limitations

1. **No Runtime Language Switching:** Users must create new profile to change language
2. **Mixed Logs:** API logs are in the language of the request
3. **Recipe Names:** Original recipe names from past sessions remain in original language

## Future Enhancements

- [ ] Add language switching option in preferences menu
- [ ] Support for French, Italian, Spanish
- [ ] Auto-detect system language as default
- [ ] Translation of existing recipe names in history
- [ ] Language-specific date/time formatting
