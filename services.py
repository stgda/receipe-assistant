"""
Service layer for Recipe Assistant
Separates business logic from UI/interface layer
Designed for easy integration with web/mobile interfaces
"""

import database as db
from datetime import datetime
import anthropic
import os


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
    
    def suggest_recipes(self, user_id, ingredients, language='en'):
        """
        Get recipe suggestions from Claude API
        
        Args:
            user_id: User ID integer
            ingredients: String of available ingredients
            language: Language code for responses
        
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
            
            # Create language-specific prompt
            if language == "de":
                prompt = f"""Du bist ein hilfreicher Koch-Assistent. Der Nutzer möchte ein Mittagessen kochen.

Verfügbare Zutaten: {ingredients}
{preference_context}

Bitte schlage 2-3 passende Rezepte vor, die mit diesen Zutaten zubereitet werden können.

WICHTIG: Formatiere jeden Rezeptnamen als Markdown-Überschrift mit '## Rezeptname' (zwei Hashtags).

Gib für jedes Rezept an:
- Name des Gerichts (als ## Überschrift)
- Benötigte Zutaten (markiere, welche vorhanden sind)
- Kurze Zubereitungsanleitung (3-5 Schritte)
- Zubereitungszeit

Halte die Vorschläge prägnant und praktisch umsetzbar."""
            else:
                prompt = f"""You are a helpful cooking assistant. The user wants to cook lunch.

Available ingredients: {ingredients}
{preference_context}

Please suggest 2-3 suitable recipes that can be prepared with these ingredients.

IMPORTANT: Format each recipe name as a Markdown heading with '## Recipe Name' (two hashtags).

For each recipe, provide:
- Name of the dish (as ## heading)
- Required ingredients (mark which ones are available)
- Brief preparation instructions (3-5 steps)
- Preparation time

Keep the suggestions concise and practically feasible."""
            
            # Call Claude API
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            
            # Parse recipe names
            recipe_names = self._parse_recipe_names(response_text)
            
            # Save recipes to database
            recipe_ids = []
            for name in recipe_names:
                recipe_id = db.create_recipe(user_id, name, ingredients)
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
