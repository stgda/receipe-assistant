"""
Database module for Recipe Assistant
Handles user data storage using SQLite
"""

import sqlite3
import os
from contextlib import contextmanager

# Database file location - configurable for Docker volumes
DB_FILE = os.environ.get('DATABASE_PATH', 'recipe_assistant.db')

# Ensure data directory exists (only if we have permissions)
db_dir = os.path.dirname(DB_FILE)
if db_dir:
    try:
        # Try to create directory if it doesn't exist
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    except (PermissionError, OSError) as e:
        # Fallback to current directory if we can't create the directory
        print(f"Warning: Cannot create directory '{db_dir}': {e}")
        print(f"Falling back to current directory")
        DB_FILE = os.path.basename(DB_FILE)


@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_database():
    """Initialize database schema"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                language TEXT NOT NULL DEFAULT 'en',
                default_servings INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Recipes table - stores all suggested recipes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                ingredients TEXT NOT NULL,
                full_text TEXT,
                servings INTEGER DEFAULT 1,
                suggested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Ratings table - stores user feedback on recipes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                recipe_id INTEGER,
                dish_name TEXT NOT NULL,
                rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
                comment TEXT,
                rated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE SET NULL
            )
        """)
        
        # Indexes for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_username 
            ON users(username)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_recipes_user 
            ON recipes(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ratings_user 
            ON ratings(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ratings_recipe 
            ON ratings(recipe_id)
        """)
        
        conn.commit()
        
        # Add columns to existing tables if they don't exist (migration)
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN default_servings INTEGER NOT NULL DEFAULT 1")
            conn.commit()
        except:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE recipes ADD COLUMN full_text TEXT")
            conn.commit()
        except:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE recipes ADD COLUMN servings INTEGER DEFAULT 1")
            conn.commit()
        except:
            pass  # Column already exists


def create_user(username, language='en'):
    """
    Create a new user
    
    Args:
        username: Username string
        language: Language code (en, de, etc.)
    
    Returns:
        User ID if successful, None if username already exists
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, language) VALUES (?, ?)",
                (username, language)
            )
            return cursor.lastrowid
    except sqlite3.IntegrityError:
        # Username already exists
        return None


def get_user(username):
    """
    Get user data by username
    
    Args:
        username: Username string
    
    Returns:
        Dictionary with user data or None if not found
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, language, default_servings, created_at, last_login FROM users WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()
        
        if row:
            return {
                'id': row['id'],
                'username': row['username'],
                'language': row['language'],
                'default_servings': row['default_servings'],
                'created_at': row['created_at'],
                'last_login': row['last_login']
            }
        return None


def get_user_by_id(user_id):
    """
    Get user data by ID
    
    Args:
        user_id: User ID integer
    
    Returns:
        Dictionary with user data or None if not found
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, language, default_servings, created_at, last_login FROM users WHERE id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        
        if row:
            return {
                'id': row['id'],
                'username': row['username'],
                'language': row['language'],
                'default_servings': row['default_servings'],
                'created_at': row['created_at'],
                'last_login': row['last_login']
            }
        return None


def list_all_users():
    """
    Get list of all users
    
    Returns:
        List of dictionaries with user data
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, language, default_servings, created_at, last_login FROM users ORDER BY username"
        )
        rows = cursor.fetchall()
        
        return [
            {
                'id': row['id'],
                'username': row['username'],
                'language': row['language'],
                'default_servings': row['default_servings'],
                'created_at': row['created_at'],
                'last_login': row['last_login']
            }
            for row in rows
        ]


def update_user_language(username, language):
    """
    Update user's language preference
    
    Args:
        username: Username string
        language: New language code
    
    Returns:
        True if successful, False if user not found
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET language = ? WHERE username = ?",
            (language, username)
        )
        return cursor.rowcount > 0


def update_user_servings(user_id, servings):
    """
    Update user's default servings preference
    
    Args:
        user_id: User ID integer
        servings: Number of servings (default portions)
    
    Returns:
        True if successful, False if user not found
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET default_servings = ? WHERE id = ?",
            (servings, user_id)
        )
        return cursor.rowcount > 0


def update_last_login(username):
    """
    Update user's last login timestamp
    
    Args:
        username: Username string
    
    Returns:
        True if successful, False if user not found
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = ?",
            (username,)
        )
        return cursor.rowcount > 0


def delete_user(username):
    """
    Delete a user (use with caution!)
    
    Args:
        username: Username string
    
    Returns:
        True if successful, False if user not found
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM users WHERE username = ?",
            (username,)
        )
        return cursor.rowcount > 0


def user_exists(username):
    """
    Check if user exists
    
    Args:
        username: Username string
    
    Returns:
        True if user exists, False otherwise
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM users WHERE username = ? LIMIT 1",
            (username,)
        )
        return cursor.fetchone() is not None


def get_user_count():
    """
    Get total number of users
    
    Returns:
        Integer count of users
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM users")
        return cursor.fetchone()['count']


# ============================================================================
# Recipe Management Functions
# ============================================================================

def create_recipe(user_id, name, ingredients, full_text=None, servings=1):
    """
    Create a new recipe suggestion
    
    Args:
        user_id: User ID integer
        name: Recipe name string
        ingredients: Ingredients string (comma-separated or description)
        full_text: Full recipe text from Claude (optional)
        servings: Number of servings this recipe is for
    
    Returns:
        Recipe ID if successful, None otherwise
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO recipes (user_id, name, ingredients, full_text, servings) VALUES (?, ?, ?, ?, ?)",
                (user_id, name, ingredients, full_text, servings)
            )
            return cursor.lastrowid
    except Exception:
        return None


def get_recipe(recipe_id):
    """
    Get recipe by ID
    
    Args:
        recipe_id: Recipe ID integer
    
    Returns:
        Dictionary with recipe data or None if not found
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, user_id, name, ingredients, full_text, servings, suggested_at FROM recipes WHERE id = ?",
            (recipe_id,)
        )
        row = cursor.fetchone()
        
        if row:
            return {
                'id': row['id'],
                'user_id': row['user_id'],
                'name': row['name'],
                'ingredients': row['ingredients'],
                'full_text': row['full_text'],
                'servings': row['servings'],
                'suggested_at': row['suggested_at']
            }
        return None


def get_user_recipes(user_id, limit=None):
    """
    Get all recipes for a user
    
    Args:
        user_id: User ID integer
        limit: Optional limit on number of results
    
    Returns:
        List of dictionaries with recipe data
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if limit:
            cursor.execute(
                "SELECT id, user_id, name, ingredients, full_text, servings, suggested_at FROM recipes "
                "WHERE user_id = ? ORDER BY suggested_at DESC LIMIT ?",
                (user_id, limit)
            )
        else:
            cursor.execute(
                "SELECT id, user_id, name, ingredients, full_text, servings, suggested_at FROM recipes "
                "WHERE user_id = ? ORDER BY suggested_at DESC",
                (user_id,)
            )
        
        rows = cursor.fetchall()
        
        return [
            {
                'id': row['id'],
                'user_id': row['user_id'],
                'name': row['name'],
                'ingredients': row['ingredients'],
                'full_text': row['full_text'],
                'servings': row['servings'],
                'suggested_at': row['suggested_at']
            }
            for row in rows
        ]


def get_unrated_recipes(user_id):
    """
    Get recipes that haven't been rated yet
    
    Args:
        user_id: User ID integer
    
    Returns:
        List of dictionaries with recipe data
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.id, r.user_id, r.name, r.ingredients, r.full_text, r.servings, r.suggested_at 
            FROM recipes r
            LEFT JOIN ratings rt ON r.id = rt.recipe_id
            WHERE r.user_id = ? AND rt.id IS NULL
            ORDER BY r.suggested_at DESC
        """, (user_id,))
        
        rows = cursor.fetchall()
        
        return [
            {
                'id': row['id'],
                'user_id': row['user_id'],
                'name': row['name'],
                'ingredients': row['ingredients'],
                'full_text': row['full_text'],
                'servings': row['servings'],
                'suggested_at': row['suggested_at']
            }
            for row in rows
        ]


def get_recipes_with_ratings(user_id, min_rating=None, max_rating=None, include_unrated=True):
    """
    Get recipes filtered by rating
    
    Args:
        user_id: User ID integer
        min_rating: Minimum rating (1-5), None for no minimum
        max_rating: Maximum rating (1-5), None for no maximum
        include_unrated: Include recipes without ratings
    
    Returns:
        List of dictionaries with recipe and rating data
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        query = """
            SELECT 
                r.id, r.user_id, r.name, r.ingredients, r.full_text, r.servings, r.suggested_at,
                rt.rating, rt.comment, rt.rated_at
            FROM recipes r
            LEFT JOIN ratings rt ON r.id = rt.recipe_id
            WHERE r.user_id = ?
        """
        
        params = [user_id]
        
        if not include_unrated:
            query += " AND rt.id IS NOT NULL"
        
        if min_rating is not None:
            query += " AND (rt.rating >= ? OR rt.rating IS NULL)"
            params.append(min_rating)
        
        if max_rating is not None:
            query += " AND (rt.rating <= ? OR rt.rating IS NULL)"
            params.append(max_rating)
        
        query += " ORDER BY r.suggested_at DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [
            {
                'id': row['id'],
                'user_id': row['user_id'],
                'name': row['name'],
                'ingredients': row['ingredients'],
                'full_text': row['full_text'],
                'servings': row['servings'],
                'suggested_at': row['suggested_at'],
                'rating': row['rating'],
                'comment': row['comment'],
                'rated_at': row['rated_at']
            }
            for row in rows
        ]


def delete_recipe(recipe_id):
    """
    Delete a recipe
    
    Args:
        recipe_id: Recipe ID integer
    
    Returns:
        True if successful, False if recipe not found
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
        return cursor.rowcount > 0


# ============================================================================
# Rating/Feedback Management Functions
# ============================================================================

def create_rating(user_id, dish_name, rating, comment=None, recipe_id=None):
    """
    Create a new rating
    
    Args:
        user_id: User ID integer
        dish_name: Name of the dish rated
        rating: Rating value (1-5)
        comment: Optional comment text
        recipe_id: Optional recipe ID if rating a suggested recipe
    
    Returns:
        Rating ID if successful, None otherwise
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO ratings (user_id, recipe_id, dish_name, rating, comment) "
                "VALUES (?, ?, ?, ?, ?)",
                (user_id, recipe_id, dish_name, rating, comment)
            )
            return cursor.lastrowid
    except Exception:
        return None


def get_rating(rating_id):
    """
    Get rating by ID
    
    Args:
        rating_id: Rating ID integer
    
    Returns:
        Dictionary with rating data or None if not found
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, user_id, recipe_id, dish_name, rating, comment, rated_at "
            "FROM ratings WHERE id = ?",
            (rating_id,)
        )
        row = cursor.fetchone()
        
        if row:
            return {
                'id': row['id'],
                'user_id': row['user_id'],
                'recipe_id': row['recipe_id'],
                'dish_name': row['dish_name'],
                'rating': row['rating'],
                'comment': row['comment'],
                'rated_at': row['rated_at']
            }
        return None


def get_user_ratings(user_id, limit=None):
    """
    Get all ratings for a user
    
    Args:
        user_id: User ID integer
        limit: Optional limit on number of results
    
    Returns:
        List of dictionaries with rating data
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if limit:
            cursor.execute(
                "SELECT id, user_id, recipe_id, dish_name, rating, comment, rated_at "
                "FROM ratings WHERE user_id = ? ORDER BY rated_at DESC LIMIT ?",
                (user_id, limit)
            )
        else:
            cursor.execute(
                "SELECT id, user_id, recipe_id, dish_name, rating, comment, rated_at "
                "FROM ratings WHERE user_id = ? ORDER BY rated_at DESC",
                (user_id,)
            )
        
        rows = cursor.fetchall()
        
        return [
            {
                'id': row['id'],
                'user_id': row['user_id'],
                'recipe_id': row['recipe_id'],
                'dish_name': row['dish_name'],
                'rating': row['rating'],
                'comment': row['comment'],
                'rated_at': row['rated_at']
            }
            for row in rows
        ]


def get_liked_dishes(user_id, min_rating=4):
    """
    Get dishes the user liked (rating >= min_rating)
    
    Args:
        user_id: User ID integer
        min_rating: Minimum rating to consider as "liked" (default: 4)
    
    Returns:
        List of dish names
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT dish_name FROM ratings WHERE user_id = ? AND rating >= ? "
            "ORDER BY rated_at DESC",
            (user_id, min_rating)
        )
        return [row['dish_name'] for row in cursor.fetchall()]


def get_disliked_dishes(user_id, max_rating=2):
    """
    Get dishes the user disliked (rating <= max_rating)
    
    Args:
        user_id: User ID integer
        max_rating: Maximum rating to consider as "disliked" (default: 2)
    
    Returns:
        List of dish names
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT dish_name FROM ratings WHERE user_id = ? AND rating <= ? "
            "ORDER BY rated_at DESC",
            (user_id, max_rating)
        )
        return [row['dish_name'] for row in cursor.fetchall()]


def get_rating_stats(user_id):
    """
    Get rating statistics for a user
    
    Args:
        user_id: User ID integer
    
    Returns:
        Dictionary with statistics (count, average, etc.)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total_ratings,
                AVG(rating) as avg_rating,
                MIN(rating) as min_rating,
                MAX(rating) as max_rating
            FROM ratings 
            WHERE user_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        
        return {
            'total_ratings': row['total_ratings'],
            'avg_rating': round(row['avg_rating'], 2) if row['avg_rating'] else 0,
            'min_rating': row['min_rating'] if row['min_rating'] else 0,
            'max_rating': row['max_rating'] if row['max_rating'] else 0
        }


def delete_rating(rating_id):
    """
    Delete a rating
    
    Args:
        rating_id: Rating ID integer
    
    Returns:
        True if successful, False if rating not found
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ratings WHERE id = ?", (rating_id,))
        return cursor.rowcount > 0
