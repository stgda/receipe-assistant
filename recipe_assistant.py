#!/usr/bin/env python3
"""
Recipe Assistant with Claude API
Suggests lunch based on available ingredients and learns taste preferences
Supports multiple users with individual preferences and logs
Supports multiple languages (English, German)
"""

import os
import json
import anthropic
from datetime import datetime

# User data directory
USERS_DIR = "users"
# Log file for Claude API communication
GLOBAL_LOG_FILE = "claude_api_log.json"

# Language translations
TRANSLATIONS = {
    "en": {
        "welcome": "Welcome to the AI Recipe Assistant!",
        "user_selection": "User Selection",
        "existing_users": "Existing users:",
        "create_new_user": "Create new user",
        "select_user": "Select user",
        "enter_username": "Enter username (letters, numbers, underscore only)",
        "username_empty": "Username cannot be empty",
        "username_invalid": "Username can only contain letters, numbers, underscore and hyphen",
        "username_exists": "Username already exists",
        "select_language": "Select your language:",
        "language_en": "English",
        "language_de": "German",
        "language_saved": "Language preference saved!",
        "logged_in_as": "Logged in as",
        "what_to_do": "What would you like to do?",
        "option_1": "Get recipe suggestions for today",
        "option_2": "Give feedback on a cooked dish",
        "option_3": "View my preferences",
        "option_4": "View API log",
        "your_choice": "Your choice",
        "available_ingredients": "Available Ingredients",
        "list_ingredients": "Please list all ingredients you have in your fridge.",
        "ingredients_example": "(Example: tomatoes, mozzarella, basil, pasta, ground beef)",
        "your_ingredients": "Your ingredients",
        "no_ingredients": "No ingredients provided. Aborting.",
        "thinking": "I'm thinking of suitable recipes for you...",
        "already_cooked": "Have you already cooked one of these dishes? (y/n)",
        "which_dish_cooked": "Which dish did you cook?",
        "recently_suggested": "Recently Suggested Recipes",
        "suggested_on": "Suggested on",
        "ingredients_label": "Ingredients",
        "other_dish": "Other dish (manual entry)",
        "which_recipe_cooked": "Which recipe did you cook?",
        "please_enter_number": "Please enter a number between",
        "please_enter_valid": "Please enter a valid number",
        "no_unrated_recipes": "No unrated recipe suggestions found.",
        "tip_get_suggestions": "Tip: Get new recipe suggestions first (Option 1) before giving feedback.",
        "feedback_for": "Feedback for",
        "how_liked": "How did you like the dish?",
        "rating_1": "Didn't like it at all",
        "rating_2": "Not great",
        "rating_3": "Okay",
        "rating_4": "Good",
        "rating_5": "Very good!",
        "your_rating": "Your rating (1-5)",
        "noted_liked": "Noted: You liked",
        "noted_disliked": "Noted:",
        "not_to_taste": "wasn't to your taste.",
        "what_not_liked": "Would you like to briefly say what you didn't like? (Enter to skip)",
        "thank_feedback": "Thank you for your feedback! I will consider it for future suggestions.",
        "your_preferences": "Your Preferences",
        "num_ratings": "Number of saved ratings",
        "dishes_liked": "Dishes you liked:",
        "dishes_disliked": "Dishes you didn't like:",
        "unrated_suggestions": "Unrated recipe suggestions",
        "api_log": "API Log",
        "entries": "entries",
        "no_api_calls": "No API calls in the log yet.",
        "how_many_entries": "How many entries would you like to see?",
        "last_5": "Last 5 entries",
        "last_10": "Last 10 entries",
        "all_entries": "All entries",
        "entry": "Entry",
        "prompt": "PROMPT",
        "response": "RESPONSE",
        "truncated": "[truncated]",
        "invalid_selection": "Invalid selection.",
        "api_key_error": "Error: ANTHROPIC_API_KEY not found!",
        "api_key_instruction": "Please set your API key as environment variable:",
        "log_saved": "[Log] API call saved",
        "in_log": "entries in log",
        "claude_prompt_ingredients": "You are a helpful cooking assistant. The user wants to cook lunch.\n\nAvailable ingredients: {ingredients}\n{preferences}\n\nPlease suggest 2-3 suitable recipes that can be prepared with these ingredients.\n\nIMPORTANT: Format each recipe name as a Markdown heading with '## Recipe Name' (two hashtags).\n\nFor each recipe, provide:\n- Name of the dish (as ## heading)\n- Required ingredients (mark which ones are available)\n- Brief preparation instructions (3-5 steps)\n- Preparation time\n\nKeep the suggestions concise and practically feasible.",
        "pref_dishes_liked": "Dishes the user liked",
        "pref_dishes_disliked": "Dishes the user disliked",
        "pref_dietary": "Dietary restrictions"
    },
    "de": {
        "welcome": "Willkommen beim KI-Rezept-Assistenten!",
        "user_selection": "Benutzerauswahl",
        "existing_users": "Existierende Benutzer:",
        "create_new_user": "Neuen Benutzer erstellen",
        "select_user": "Benutzer auswählen",
        "enter_username": "Benutzername eingeben (nur Buchstaben, Zahlen, Unterstriche)",
        "username_empty": "Benutzername darf nicht leer sein",
        "username_invalid": "Benutzername darf nur Buchstaben, Zahlen, Unterstriche und Bindestriche enthalten",
        "username_exists": "Benutzername existiert bereits",
        "select_language": "Wähle deine Sprache:",
        "language_en": "Englisch",
        "language_de": "Deutsch",
        "language_saved": "Spracheinstellung gespeichert!",
        "logged_in_as": "Angemeldet als",
        "what_to_do": "Was möchtest du tun?",
        "option_1": "Rezeptvorschlag für heute erhalten",
        "option_2": "Feedback zu einem bereits gekochten Gericht geben",
        "option_3": "Meine Präferenzen ansehen",
        "option_4": "API-Log ansehen",
        "your_choice": "Deine Wahl",
        "available_ingredients": "Verfügbare Zutaten",
        "list_ingredients": "Bitte liste alle Zutaten auf, die du im Kühlschrank hast.",
        "ingredients_example": "(Beispiel: Tomaten, Mozzarella, Basilikum, Pasta, Hackfleisch)",
        "your_ingredients": "Deine Zutaten",
        "no_ingredients": "Keine Zutaten angegeben. Abbruch.",
        "thinking": "Ich überlege mir passende Rezepte für dich...",
        "already_cooked": "Hast du eines dieser Gerichte bereits gekocht? (j/n)",
        "which_dish_cooked": "Welches Gericht hast du gekocht?",
        "recently_suggested": "Zuletzt vorgeschlagene Rezepte",
        "suggested_on": "Vorgeschlagen am",
        "ingredients_label": "Zutaten",
        "other_dish": "Anderes Gericht (manuell eingeben)",
        "which_recipe_cooked": "Welches Rezept hast du gekocht?",
        "please_enter_number": "Bitte gib eine Zahl zwischen",
        "please_enter_valid": "Bitte gib eine gültige Zahl ein",
        "no_unrated_recipes": "Keine unbewerteten Rezeptvorschläge gefunden.",
        "tip_get_suggestions": "Tipp: Lass dir erst neue Rezepte vorschlagen (Option 1), bevor du Feedback gibst.",
        "feedback_for": "Feedback für",
        "how_liked": "Wie hat dir das Gericht geschmeckt?",
        "rating_1": "Überhaupt nicht geschmeckt",
        "rating_2": "Nicht so gut",
        "rating_3": "Okay",
        "rating_4": "Gut",
        "rating_5": "Sehr gut!",
        "your_rating": "Deine Bewertung (1-5)",
        "noted_liked": "Notiert: Dir hat",
        "noted_disliked": "Notiert:",
        "not_to_taste": "war nicht nach deinem Geschmack.",
        "what_not_liked": "Möchtest du kurz sagen, was dir nicht gefallen hat? (Enter zum Überspringen)",
        "thank_feedback": "Danke für dein Feedback! Ich werde das für zukünftige Vorschläge berücksichtigen.",
        "your_preferences": "Deine Präferenzen",
        "num_ratings": "Anzahl gespeicherter Bewertungen",
        "dishes_liked": "Gerichte, die dir geschmeckt haben:",
        "dishes_disliked": "Gerichte, die dir nicht geschmeckt haben:",
        "unrated_suggestions": "Unbewertete Rezeptvorschläge",
        "api_log": "API-Log",
        "entries": "Einträge",
        "no_api_calls": "Noch keine API-Calls im Log.",
        "how_many_entries": "Wie viele Einträge möchtest du sehen?",
        "last_5": "Die letzten 5 Einträge",
        "last_10": "Die letzten 10 Einträge",
        "all_entries": "Alle Einträge",
        "entry": "Eintrag",
        "prompt": "PROMPT",
        "response": "ANTWORT",
        "truncated": "[gekürzt]",
        "invalid_selection": "Ungültige Auswahl.",
        "api_key_error": "Fehler: ANTHROPIC_API_KEY nicht gefunden!",
        "api_key_instruction": "Bitte setze deinen API-Key als Umgebungsvariable:",
        "log_saved": "[Log] API-Call gespeichert",
        "in_log": "Einträge im Log",
        "claude_prompt_ingredients": "Du bist ein hilfreicher Koch-Assistent. Der Nutzer möchte ein Mittagessen kochen.\n\nVerfügbare Zutaten: {ingredients}\n{preferences}\n\nBitte schlage 2-3 passende Rezepte vor, die mit diesen Zutaten zubereitet werden können.\n\nWICHTIG: Formatiere jeden Rezeptnamen als Markdown-Überschrift mit '## Rezeptname' (zwei Hashtags).\n\nGib für jedes Rezept an:\n- Name des Gerichts (als ## Überschrift)\n- Benötigte Zutaten (markiere, welche vorhanden sind)\n- Kurze Zubereitungsanleitung (3-5 Schritte)\n- Zubereitungszeit\n\nHalte die Vorschläge prägnant und praktisch umsetzbar.",
        "pref_dishes_liked": "Gerichte, die dem Nutzer gut geschmeckt haben",
        "pref_dishes_disliked": "Gerichte, die dem Nutzer nicht geschmeckt haben",
        "pref_dietary": "Ernährungseinschränkungen"
    }
}

def t(lang, key):
    """Get translation for a key in specified language"""
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)

def get_user_files(username):
    """Get file paths for a specific user"""
    user_dir = os.path.join(USERS_DIR, username)
    return {
        "dir": user_dir,
        "preferences": os.path.join(user_dir, "preferences.json"),
        "log": os.path.join(user_dir, "api_log.json")
    }

def ensure_user_directory(username):
    """Create user directory if it doesn't exist"""
    user_files = get_user_files(username)
    os.makedirs(user_files["dir"], exist_ok=True)
    return user_files

def list_users():
    """List all existing users"""
    if not os.path.exists(USERS_DIR):
        return []
    return [d for d in os.listdir(USERS_DIR)
            if os.path.isdir(os.path.join(USERS_DIR, d))]

def select_or_create_user():
    """Let user select existing user or create new one"""
    users = list_users()

    print("\n" + "=" * 60)
    print("👤  User Selection / Benutzerauswahl")
    print("=" * 60)

    if users:
        print("\nExisting users / Existierende Benutzer:")
        for i, user in enumerate(users, 1):
            print(f"{i}. {user}")
        print(f"{len(users) + 1}. Create new user / Neuen Benutzer erstellen")

        while True:
            try:
                choice = int(input(f"\nSelect user / Benutzer auswählen (1-{len(users) + 1}): "))
                if 1 <= choice <= len(users):
                    return users[choice - 1]
                elif choice == len(users) + 1:
                    break
                else:
                    print(f"Please enter a number between / Bitte gib eine Zahl zwischen 1 und {len(users) + 1} ein")
            except ValueError:
                print("Please enter a valid number / Bitte gib eine gültige Zahl ein")

    # Create new user
    while True:
        username = input("\nEnter username / Benutzername eingeben (letters, numbers, underscore only / nur Buchstaben, Zahlen, Unterstriche): ").strip()
        if not username:
            print("Username cannot be empty / Benutzername darf nicht leer sein")
            continue
        if not username.replace("_", "").replace("-", "").isalnum():
            print("Username can only contain letters, numbers, underscore and hyphen / Benutzername darf nur Buchstaben, Zahlen, Unterstriche und Bindestriche enthalten")
            continue
        if username in users:
            print("Username already exists / Benutzername existiert bereits")
            continue

        # Language selection for new user
        print("\nSelect your language / Wähle deine Sprache:")
        print("1. English")
        print("2. Deutsch")

        while True:
            try:
                lang_choice = int(input("\nYour choice / Deine Wahl (1-2): "))
                if lang_choice == 1:
                    language = "en"
                    break
                elif lang_choice == 2:
                    language = "de"
                    break
                else:
                    print("Please enter 1 or 2 / Bitte gib 1 oder 2 ein")
            except ValueError:
                print("Please enter a valid number / Bitte gib eine gültige Zahl ein")

        # Create user directory and save initial preferences with language
        user_files = ensure_user_directory(username)
        initial_prefs = {
            "language": language,
            "liked_dishes": [],
            "disliked_dishes": [],
            "ratings": [],
            "dietary_restrictions": [],
            "suggested_recipes": []
        }
        save_preferences(initial_prefs, user_files["preferences"])

        print(f"\n✓ {t(language, 'language_saved')}")

        return username

def load_preferences(preferences_file):
    """Load saved user preferences"""
    if os.path.exists(preferences_file):
        with open(preferences_file, 'r', encoding='utf-8') as f:
            prefs = json.load(f)
            # Ensure language key exists (backward compatibility)
            if "language" not in prefs:
                prefs["language"] = "en"
            return prefs
    return {
        "language": "en",  # Default language
        "liked_dishes": [],
        "disliked_dishes": [],
        "ratings": [],
        "dietary_restrictions": [],
        "suggested_recipes": []
    }

def save_preferences(preferences, preferences_file):
    """Save user preferences"""
    with open(preferences_file, 'w', encoding='utf-8') as f:
        json.dump(preferences, f, indent=2, ensure_ascii=False)

def load_api_log(log_file):
    """Load the API log"""
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_api_log(log_entries, log_file):
    """Save the API log (maximum 100 entries)"""
    # Keep only the last 100 entries
    log_entries = log_entries[-100:]

    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log_entries, f, indent=2, ensure_ascii=False)

def log_api_call(prompt, response, log_file):
    """Add an API call to the log"""
    log_entries = load_api_log(log_file)

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "response": response
    }

    log_entries.append(log_entry)
    save_api_log(log_entries, log_file)

    # Note: Using print without translation for technical log messages
    print(f"[Log] API call saved ({len(log_entries)} entries in log)")

def get_recipe_suggestion(client, ingredients, preferences, preferences_file, log_file, lang):
    """Get recipe suggestion from Claude based on ingredients and preferences"""

    # Build context from preferences
    preference_context = ""
    if preferences["liked_dishes"]:
        preference_context += f"\n\n{t(lang, 'pref_dishes_liked')}: {', '.join(preferences['liked_dishes'][-5:])}"
    if preferences["disliked_dishes"]:
        preference_context += f"\n{t(lang, 'pref_dishes_disliked')}: {', '.join(preferences['disliked_dishes'][-5:])}"
    if preferences["dietary_restrictions"]:
        preference_context += f"\n{t(lang, 'pref_dietary')}: {', '.join(preferences['dietary_restrictions'])}"

    # Use language-specific prompt
    prompt = t(lang, "claude_prompt_ingredients").format(
        ingredients=ingredients,
        preferences=preference_context
    )

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    response_text = message.content[0].text

    # Log prompt and response
    log_api_call(prompt, response_text, log_file)

    # Save the recipe suggestions
    save_suggested_recipes(response_text, ingredients, preferences, preferences_file)

    return response_text

def save_suggested_recipes(response_text, ingredients, preferences, preferences_file):
    """Extract and save recipe names from Claude's response"""
    lines = response_text.split('\n')
    recipe_names = []

    for line in lines:
        line = line.strip()
        # Recognize recipe names: lines starting with ## (Markdown H2)
        if line.startswith('##'):
            name = line.replace('##', '').strip()
            # Remove additional formatting if present
            name = name.strip('#').strip()
            if name and len(name) < 100:  # Prevent too long "names"
                recipe_names.append(name)

    # Save found recipes
    if recipe_names:
        timestamp = datetime.now().isoformat()
        for recipe_name in recipe_names:
            preferences["suggested_recipes"].append({
                "name": recipe_name,
                "ingredients": ingredients,
                "suggested_at": timestamp,
                "rated": False
            })

        # Keep only the last 20 suggestions
        preferences["suggested_recipes"] = preferences["suggested_recipes"][-20:]

        # Save immediately so recipes are preserved even without feedback
        save_preferences(preferences, preferences_file)

def get_feedback(client, dish_name, preferences, preferences_file, lang):
    """Collect feedback after cooking"""

    print(f"\n--- {t(lang, 'feedback_for')}: {dish_name} ---")
    print(t(lang, "how_liked"))
    print(f"1 - {t(lang, 'rating_1')}")
    print(f"2 - {t(lang, 'rating_2')}")
    print(f"3 - {t(lang, 'rating_3')}")
    print(f"4 - {t(lang, 'rating_4')}")
    print(f"5 - {t(lang, 'rating_5')}")

    while True:
        try:
            rating = int(input(f"\n{t(lang, 'your_rating')}: "))
            if 1 <= rating <= 5:
                break
            print(f"{t(lang, 'please_enter_number')} 1 {t(lang, 'please_enter_number')} 5.")
        except ValueError:
            print(t(lang, "please_enter_valid"))

    # Save feedback
    preferences["ratings"].append({
        "dish": dish_name,
        "rating": rating,
        "date": datetime.now().isoformat()
    })

    if rating >= 4:
        preferences["liked_dishes"].append(dish_name)
        if lang == "de":
            print(f"✓ {t(lang, 'noted_liked')} '{dish_name}' geschmeckt!")
        else:
            print(f"✓ {t(lang, 'noted_liked')} '{dish_name}'!")
    elif rating <= 2:
        preferences["disliked_dishes"].append(dish_name)
        print(f"✓ {t(lang, 'noted_disliked')} '{dish_name}' {t(lang, 'not_to_taste')}")

    # Optional: Ask for details
    if rating <= 2:
        reason = input(f"\n{t(lang, 'what_not_liked')}: ")
        if reason:
            preferences["ratings"][-1]["reason"] = reason

    # Mark recipe as rated
    for recipe in preferences["suggested_recipes"]:
        if recipe["name"].lower() == dish_name.lower():
            recipe["rated"] = True
            break

    save_preferences(preferences, preferences_file)
    print(f"\n{t(lang, 'thank_feedback')}\n")

def select_recipe_from_suggestions(preferences, lang):
    """Let user select from suggested recipes"""
    # Filter unrated recipes
    unrated_recipes = [r for r in preferences["suggested_recipes"] if not r.get("rated", False)]

    if not unrated_recipes:
        print(f"\n{t(lang, 'no_unrated_recipes')}")
        print(t(lang, "tip_get_suggestions"))
        return None

    print(f"\n--- {t(lang, 'recently_suggested')} ---")
    for i, recipe in enumerate(unrated_recipes[-10:], 1):  # Show maximum last 10
        date = datetime.fromisoformat(recipe["suggested_at"]).strftime("%d.%m.%Y %H:%M")
        print(f"{i}. {recipe['name']}")
        print(f"   {t(lang, 'suggested_on')}: {date}")
        print(f"   {t(lang, 'ingredients_label')}: {recipe['ingredients'][:60]}{'...' if len(recipe['ingredients']) > 60 else ''}")
        print()

    print(f"0. {t(lang, 'other_dish')}")

    while True:
        try:
            choice = int(input(f"\n{t(lang, 'which_recipe_cooked')} (0-{len(unrated_recipes[-10:])}): "))
            if 0 <= choice <= len(unrated_recipes[-10:]):
                if choice == 0:
                    return None
                return unrated_recipes[-10:][choice - 1]["name"]
            print(f"{t(lang, 'please_enter_number')} 0 {t(lang, 'please_enter_number')} {len(unrated_recipes[-10:])}.")
        except ValueError:
            print(t(lang, "please_enter_valid"))

def main():
    """Main program"""
    print("=" * 60)
    print("🍳  Welcome to the AI Recipe Assistant!")
    print("🍳  Willkommen beim KI-Rezept-Assistenten!")
    print("=" * 60)

    # API key check
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n❌ Error / Fehler: ANTHROPIC_API_KEY not found / nicht gefunden!")
        print("Please set your API key as environment variable:")
        print("Bitte setze deinen API-Key als Umgebungsvariable:")
        print("  export ANTHROPIC_API_KEY='your-api-key'")
        return

    client = anthropic.Anthropic(api_key=api_key)

    # Select or create user
    username = select_or_create_user()
    user_files = ensure_user_directory(username)

    preferences = load_preferences(user_files["preferences"])
    lang = preferences.get("language", "en")

    print(f"\n✓ {t(lang, 'logged_in_as')}: {username}")

    # Select mode
    print(f"\n{t(lang, 'what_to_do')}")
    print(f"1 - {t(lang, 'option_1')}")
    print(f"2 - {t(lang, 'option_2')}")
    print(f"3 - {t(lang, 'option_3')}")
    print(f"4 - {t(lang, 'option_4')}")

    choice = input(f"\n{t(lang, 'your_choice')} (1-4): ").strip()

    if choice == "1":
        # Request ingredients
        print(f"\n--- {t(lang, 'available_ingredients')} ---")
        print(t(lang, "list_ingredients"))
        print(t(lang, "ingredients_example"))

        ingredients = input(f"\n{t(lang, 'your_ingredients')}: ").strip()

        if not ingredients:
            print(t(lang, "no_ingredients"))
            return

        print(f"\n🤔 {t(lang, 'thinking')}\n")

        # Get recipe suggestion
        suggestion = get_recipe_suggestion(client, ingredients, preferences,
                                          user_files["preferences"], user_files["log"], lang)
        print("=" * 60)
        print(suggestion)
        print("=" * 60)

        # Ask if feedback should be given
        yes_no = "y/n" if lang == "en" else "j/n"
        cook_now = input(f"\n{t(lang, 'already_cooked')} ({yes_no}): ").lower()
        cooked = cook_now in ['y', 'j']

        if cooked:
            dish_name = input(f"{t(lang, 'which_dish_cooked')} ")
            get_feedback(client, dish_name, preferences, user_files["preferences"], lang)

    elif choice == "2":
        # Direct feedback - with selection from suggested recipes
        dish_name = select_recipe_from_suggestions(preferences, lang)

        if dish_name is None:
            # Manual entry
            dish_name = input(f"\n{t(lang, 'which_dish_cooked')} ")

        if dish_name:
            get_feedback(client, dish_name, preferences, user_files["preferences"], lang)

    elif choice == "3":
        # Show preferences
        print(f"\n--- {t(lang, 'your_preferences')} ---")
        print(f"{t(lang, 'num_ratings')}: {len(preferences['ratings'])}")

        if preferences["liked_dishes"]:
            print(f"\n{t(lang, 'dishes_liked')}")
            for dish in preferences["liked_dishes"][-10:]:
                print(f"  ✓ {dish}")

        if preferences["disliked_dishes"]:
            print(f"\n{t(lang, 'dishes_disliked')}")
            for dish in preferences["disliked_dishes"][-10:]:
                print(f"  ✗ {dish}")

        # Show suggested recipes
        unrated = [r for r in preferences["suggested_recipes"] if not r.get("rated", False)]
        if unrated:
            print(f"\n{t(lang, 'unrated_suggestions')}: {len(unrated)}")
            for recipe in unrated[-5:]:
                date = datetime.fromisoformat(recipe["suggested_at"]).strftime("%d.%m.%Y")
                suggested_label = t(lang, "suggested_on").lower() if lang == "de" else "suggested on"
                print(f"  • {recipe['name']} ({suggested_label} {date})")

    elif choice == "4":
        # Show API log
        log_entries = load_api_log(user_files["log"])

        if not log_entries:
            print(f"\n{t(lang, 'no_api_calls')}")
        else:
            print(f"\n--- {t(lang, 'api_log')} ({len(log_entries)} {t(lang, 'entries')}) ---")
            print(f"\n{t(lang, 'how_many_entries')}")
            print(f"1 - {t(lang, 'last_5')}")
            print(f"2 - {t(lang, 'last_10')}")
            print(f"3 - {t(lang, 'all_entries')}")

            log_choice = input(f"\n{t(lang, 'your_choice')} (1-3): ").strip()

            if log_choice == "1":
                entries_to_show = log_entries[-5:]
            elif log_choice == "2":
                entries_to_show = log_entries[-10:]
            else:
                entries_to_show = log_entries

            for i, entry in enumerate(entries_to_show, 1):
                timestamp = datetime.fromisoformat(entry["timestamp"]).strftime("%d.%m.%Y %H:%M:%S")
                print(f"\n{'='*60}")
                print(f"{t(lang, 'entry')} {i} - {timestamp}")
                print(f"{'='*60}")
                print(f"\n--- {t(lang, 'prompt')} ---")
                print(entry["prompt"])
                print(f"\n--- {t(lang, 'response')} ---")
                # Show only first 500 characters in overview
                if len(entry["response"]) > 500:
                    print(entry["response"][:500] + f"...\n{t(lang, 'truncated')}")
                else:
                    print(entry["response"])

    else:
        print(t(lang, "invalid_selection"))


if __name__ == "__main__":
    main()
