"""
Service layer for Recipe Assistant
Separates business logic from UI/interface layer
Designed for easy integration with web/mobile interfaces
"""

import database as db
from datetime import datetime
import anthropic
import os
import json


def get_user_log_file(user_id):
    """
    Get log file path for a specific user
    
    Args:
        user_id: User ID integer
    
    Returns:
        Path to user's log file
    """
    user = db.get_user_by_id(user_id)
    if not user:
        return None
    
    username = user['username']
    users_dir = os.environ.get('USERS_DATA_PATH', 'users')
    user_dir = os.path.join(users_dir, username)
    os.makedirs(user_dir, exist_ok=True)
    
    return os.path.join(user_dir, 'api_log.json')


def log_api_call(user_id, prompt, response, model="claude-sonnet-4-20250514"):
    """
    Log API call to user's log file
    
    Args:
        user_id: User ID integer
        prompt: Prompt sent to Claude
        response: Response from Claude
        model: Model name used
    """
    log_file = get_user_log_file(user_id)
    if not log_file:
        return
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'model': model,
        'prompt': prompt,
        'response': response
    }
    
    # Load existing logs
    logs = []
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except:
            logs = []
    
    # Append new log
    logs.append(log_entry)
    
    # Save logs
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Warning: Could not write log file: {e}")


class RecipeService:
    """
    Service for recipe-related operations
    Business logic layer between database and UI
    """
    
    def __init__(self, client=None):
        """
        Initialize service
        
        Args:
            client: Anthropic client (optional, can be set later)
        """
        self.client = client
    
    def set_client(self, client):
        """Set Anthropic client"""
        self.client = client
    
    def suggest_recipes(self, user_id, ingredients, language='en', servings=1, excluded_ingredients=None):
        """
        Get recipe suggestions from Claude API
        
        Args:
            user_id: User ID integer
            ingredients: String of available ingredients
            language: Language code for responses
            servings: Number of servings/persons
            excluded_ingredients: List of ingredients to exclude
        
        Returns:
            Dictionary with:
                - success: Boolean
                - recipes: List of suggested recipes (name, ingredients)
                - raw_response: Raw Claude response text
                - error: Error message if failed
        """
        if not self.client:
            return {
                'success': False,
                'error': 'Anthropic client not initialized'
            }
        
        try:
            # Get user preferences for context
            liked = db.get_liked_dishes(user_id)
            disliked = db.get_disliked_dishes(user_id)
            
            # Build preference context
            preference_context = ""
            if liked:
                pref_label = "Gerichte, die dem Nutzer gut geschmeckt haben" if language == "de" else "Dishes the user liked"
                preference_context += f"\n\n{pref_label}: {', '.join(liked[-5:])}"
            if disliked:
                pref_label = "Gerichte, die dem Nutzer nicht geschmeckt haben" if language == "de" else "Dishes the user disliked"
                preference_context += f"\n{pref_label}: {', '.join(disliked[-5:])}"
            
            # Add excluded ingredients context
            if excluded_ingredients:
                if language == "de":
                    preference_context += f"\n\nWICHTIG: Diese Zutaten sind NICHT verfügbar und dürfen NICHT verwendet werden: {', '.join(excluded_ingredients)}"
                else:
                    preference_context += f"\n\nIMPORTANT: These ingredients are NOT available and must NOT be used: {', '.join(excluded_ingredients)}"
            
            # Create language-specific prompt
            if language == "de":
                servings_text = f"{servings} Person" if servings == 1 else f"{servings} Personen"
                prompt = f"""Du bist ein hilfreicher Koch-Assistent. Der Nutzer möchte ein Mittagessen kochen.

Verfügbare Zutaten: {ingredients}
Anzahl Personen: {servings_text}
{preference_context}

Bitte schlage 2-3 passende Rezepte vor, die mit diesen Zutaten für {servings_text} zubereitet werden können.

WICHTIG: 
- Formatiere jeden Rezeptnamen als Markdown-Überschrift mit '## Rezeptname' (zwei Hashtags).
- Alle Mengenangaben müssen für {servings_text} sein.
- Verwende NUR die verfügbaren Zutaten oder Grundzutaten wie Salz, Pfeffer, Öl.

Gib für jedes Rezept an:
- Name des Gerichts (als ## Überschrift)
- Benötigte Zutaten mit genauen Mengen für {servings_text}
- Kurze Zubereitungsanleitung (3-5 Schritte)
- Zubereitungszeit

Halte die Vorschläge prägnant und praktisch umsetzbar."""
            else:
                servings_text = f"{servings} person" if servings == 1 else f"{servings} people"
                prompt = f"""You are a helpful cooking assistant. The user wants to cook lunch.

Available ingredients: {ingredients}
Number of servings: {servings_text}
{preference_context}

Please suggest 2-3 suitable recipes that can be prepared with these ingredients for {servings_text}.

IMPORTANT: 
- Format each recipe name as a Markdown heading with '## Recipe Name' (two hashtags).
- All quantities must be for {servings_text}.
- Use ONLY the available ingredients or basic ingredients like salt, pepper, oil.

For each recipe, provide:
- Name of the dish (as ## heading)
- Required ingredients with exact quantities for {servings_text}
- Brief preparation instructions (3-5 steps)
- Preparation time

Keep the suggestions concise and practically feasible."""
            
            # Call Claude API
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            
            # Log API call
            log_api_call(user_id, prompt, response_text, model="claude-sonnet-4-20250514")
            
            # Parse recipe names
            recipe_names = self._parse_recipe_names(response_text)
            
            # Split recipes into individual texts
            individual_recipes = self._split_recipes(response_text)
            
            # Save recipes to database with individual text and servings
            recipe_ids = []
            for name in recipe_names:
                # Get individual recipe text, fallback to full text if not found
                recipe_text = individual_recipes.get(name, response_text)
                recipe_id = db.create_recipe(user_id, name, ingredients, recipe_text, servings)
                if recipe_id:
                    recipe_ids.append(recipe_id)
            
            return {
                'success': True,
                'recipes': recipe_names,
                'recipe_ids': recipe_ids,
                'raw_response': response_text,
                'prompt': prompt
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _parse_recipe_names(self, response_text):
        """
        Parse recipe names from Claude response
        
        Args:
            response_text: Raw response from Claude
        
        Returns:
            List of recipe names
        """
        lines = response_text.split('\n')
        recipe_names = []
        
        for line in lines:
            line = line.strip()
            # Recognize recipe names: lines starting with ## (Markdown H2)
            if line.startswith('##'):
                name = line.replace('##', '').strip()
                name = name.strip('#').strip()
                if name and len(name) < 100:
                    recipe_names.append(name)
        
        return recipe_names
    
    def _split_recipes(self, response_text):
        """
        Split combined recipe text into individual recipes
        
        Args:
            response_text: Raw response text with multiple recipes separated by ## headers
        
        Returns:
            Dictionary mapping recipe names to their individual text
        """
        import re
        
        # Split text by ## headers (recipe names)
        # Use lookahead to keep the ## in the split
        parts = re.split(r'(?=^## )', response_text, flags=re.MULTILINE)
        
        recipes = {}
        for part in parts:
            part = part.strip()
            if part.startswith('##'):
                # Extract recipe name from first line
                lines = part.split('\n', 1)
                recipe_name = lines[0].replace('##', '').strip()
                
                # Full recipe text includes header and content
                recipe_text = part
                
                recipes[recipe_name] = recipe_text
        
        return recipes
    
    def get_unrated_recipes(self, user_id):
        """
        Get recipes that haven't been rated
        
        Args:
            user_id: User ID integer
        
        Returns:
            List of recipe dictionaries
        """
        return db.get_unrated_recipes(user_id)
    
    def get_user_recipes(self, user_id, limit=None):
        """
        Get all recipes for a user
        
        Args:
            user_id: User ID integer
            limit: Optional limit
        
        Returns:
            List of recipe dictionaries
        """
        return db.get_user_recipes(user_id, limit)
    
    def get_recipes_with_filter(self, user_id, min_rating=None, max_rating=None, include_unrated=True):
        """
        Get recipes filtered by rating
        
        Args:
            user_id: User ID integer
            min_rating: Minimum rating (1-5)
            max_rating: Maximum rating (1-5)
            include_unrated: Include unrated recipes
        
        Returns:
            List of recipe dictionaries with rating info
        """
        return db.get_recipes_with_ratings(user_id, min_rating, max_rating, include_unrated)


class RatingService:
    """
    Service for rating/feedback operations
    Business logic layer between database and UI
    """
    
    def submit_rating(self, user_id, dish_name, rating, comment=None, recipe_id=None):
        """
        Submit a rating for a dish
        
        Args:
            user_id: User ID integer
            dish_name: Name of the dish
            rating: Rating value (1-5)
            comment: Optional comment
            recipe_id: Optional recipe ID if rating a suggested recipe
        
        Returns:
            Dictionary with:
                - success: Boolean
                - rating_id: ID of created rating
                - error: Error message if failed
        """
        if not 1 <= rating <= 5:
            return {
                'success': False,
                'error': 'Rating must be between 1 and 5'
            }
        
        try:
            rating_id = db.create_rating(user_id, dish_name, rating, comment, recipe_id)
            
            if rating_id:
                return {
                    'success': True,
                    'rating_id': rating_id
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to create rating'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_user_ratings(self, user_id, limit=None):
        """
        Get all ratings for a user
        
        Args:
            user_id: User ID integer
            limit: Optional limit
        
        Returns:
            List of rating dictionaries
        """
        return db.get_user_ratings(user_id, limit)
    
    def get_rating_stats(self, user_id):
        """
        Get rating statistics
        
        Args:
            user_id: User ID integer
        
        Returns:
            Dictionary with statistics
        """
        return db.get_rating_stats(user_id)
    
    def get_liked_dishes(self, user_id, min_rating=4):
        """
        Get dishes the user liked
        
        Args:
            user_id: User ID integer
            min_rating: Minimum rating threshold
        
        Returns:
            List of dish names
        """
        return db.get_liked_dishes(user_id, min_rating)
    
    def get_disliked_dishes(self, user_id, max_rating=2):
        """
        Get dishes the user disliked
        
        Args:
            user_id: User ID integer
            max_rating: Maximum rating threshold
        
        Returns:
            List of dish names
        """
        return db.get_disliked_dishes(user_id, max_rating)


class UserService:
    """
    Service for user-related operations
    Business logic layer between database and UI
    """
    
    def authenticate_user(self, username):
        """
        Authenticate/login a user
        
        Args:
            username: Username string
        
        Returns:
            Dictionary with:
                - success: Boolean
                - user: User data dictionary
                - error: Error message if failed
        """
        user = db.get_user(username)
        
        if user:
            # Update last login
            db.update_last_login(username)
            return {
                'success': True,
                'user': user
            }
        else:
            return {
                'success': False,
                'error': 'User not found'
            }
    
    def create_user(self, username, language='en'):
        """
        Create a new user
        
        Args:
            username: Username string
            language: Language code
        
        Returns:
            Dictionary with:
                - success: Boolean
                - user_id: ID of created user
                - user: User data dictionary
                - error: Error message if failed
        """
        # Validate username
        if not username or not username.strip():
            return {
                'success': False,
                'error': 'Username cannot be empty'
            }
        
        if not username.replace("_", "").replace("-", "").isalnum():
            return {
                'success': False,
                'error': 'Username can only contain letters, numbers, underscore and hyphen'
            }
        
        # Check if exists
        if db.user_exists(username):
            return {
                'success': False,
                'error': 'Username already exists'
            }
        
        # Create user
        user_id = db.create_user(username, language)
        
        if user_id:
            user = db.get_user(username)
            return {
                'success': True,
                'user_id': user_id,
                'user': user
            }
        else:
            return {
                'success': False,
                'error': 'Failed to create user'
            }
    
    def list_users(self):
        """
        List all users
        
        Returns:
            List of user dictionaries
        """
        return db.list_all_users()
    
    def get_user(self, username):
        """
        Get user by username
        
        Args:
            username: Username string
        
        Returns:
            User dictionary or None
        """
        return db.get_user(username)
    
    def get_user_by_id(self, user_id):
        """
        Get user by ID
        
        Args:
            user_id: User ID integer
        
        Returns:
            User dictionary or None
        """
        return db.get_user_by_id(user_id)
    
    def update_language(self, username, language):
        """
        Update user's language preference
        
        Args:
            username: Username string
            language: New language code
        
        Returns:
            Dictionary with:
                - success: Boolean
                - error: Error message if failed
        """
        success = db.update_user_language(username, language)
        
        if success:
            return {'success': True}
        else:
            return {
                'success': False,
                'error': 'Failed to update language'
            }
    
    def update_servings(self, user_id, servings):
        """
        Update user's default servings preference
        
        Args:
            user_id: User ID integer
            servings: Number of servings
        
        Returns:
            Dictionary with:
                - success: Boolean
                - error: Error message if failed
        """
        if servings < 1 or servings > 20:
            return {
                'success': False,
                'error': 'Servings must be between 1 and 20'
            }
        
        success = db.update_user_servings(user_id, servings)
        
        if success:
            return {'success': True}
        else:
            return {
                'success': False,
                'error': 'Failed to update servings'
            }
