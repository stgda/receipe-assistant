# Database Integration Documentation

## Overview

The Recipe Assistant now uses SQLite database for storing user data. This replaces the previous file-system-only approach for user management while maintaining backward compatibility with existing user data files.

## Architecture

### Hybrid Storage Model

**Database (SQLite):**
- User accounts (username, language)
- User metadata (created_at, last_login)

**File System (JSON):**
- User preferences (liked/disliked dishes)
- Recipe suggestions history
- Ratings and feedback
- API logs

This hybrid approach provides:
- Structured data for users (database)
- Flexible storage for complex data (JSON files)
- Easy migration path for future enhancements

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    language TEXT NOT NULL DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Columns:**
- `id`: Auto-incrementing primary key
- `username`: Unique username (indexed for fast lookup)
- `language`: Language code (en, de, etc.)
- `created_at`: Account creation timestamp
- `last_login`: Last login timestamp (updated on each login)

**Constraints:**
- `username` is UNIQUE (prevents duplicate usernames)
- `username` is NOT NULL (required field)
- `language` defaults to 'en' if not specified

**Indexes:**
- `idx_username` on username column for fast lookups

## Database Module API

### Initialization

```python
import database as db

# Initialize database (creates tables if they don't exist)
db.init_database()
```

### User Operations

**Create User:**
```python
user_id = db.create_user("alice", "en")
if user_id:
    print(f"User created with ID: {user_id}")
else:
    print("Username already exists")
```

**Get User:**
```python
# By username
user = db.get_user("alice")
print(user['language'])  # Access user data

# By ID
user = db.get_user_by_id(1)
```

**List All Users:**
```python
users = db.list_all_users()
for user in users:
    print(f"{user['username']}: {user['language']}")
```

**Update User:**
```python
# Update language
db.update_user_language("alice", "de")

# Update last login
db.update_last_login("alice")
```

**Check User Exists:**
```python
if db.user_exists("alice"):
    print("User exists")
```

**Delete User:**
```python
success = db.delete_user("alice")
# Note: This only deletes from database, not file system data
```

**User Count:**
```python
count = db.get_user_count()
print(f"Total users: {count}")
```

## Integration with Recipe Assistant

### User Creation Flow

1. User selects "Create new user"
2. Enters username (validated for uniqueness against DB)
3. Selects language
4. **Database**: User record created with username + language
5. **File System**: User directory created with empty preferences.json

### User Login Flow

1. User selects existing username
2. **Database**: User data retrieved, last_login updated
3. **Database**: Language preference loaded from DB
4. **File System**: Preferences loaded from user's JSON file
5. Language synced: DB → JSON (DB is source of truth)

### Language Management

- **Primary Source**: Database stores the language preference
- **Sync on Login**: JSON file updated to match DB on each login
- **Backward Compatibility**: If JSON has language but DB doesn't, DB is updated

## File Structure

```
recipe-assistant/
├── database.py              # Database module
├── recipe_assistant.py      # Main application
├── recipe_assistant.db      # SQLite database file
├── test_database.py         # Database tests
└── users/                   # User data directories
    ├── alice/
    │   ├── preferences.json # User preferences (synced from DB)
    │   └── api_log.json    # API call logs
    └── bob/
        ├── preferences.json
        └── api_log.json
```

## Database File Location

**Location**: `recipe_assistant.db` in project root
**Format**: SQLite 3
**Size**: Small (< 1MB for hundreds of users)

## Testing

Run database tests:
```bash
python3 test_database.py
```

This will:
- Create a test database
- Test all CRUD operations
- Verify constraints and indexes
- Show test results

## Backup and Migration

### Backing Up Database

```bash
# Simple copy
cp recipe_assistant.db recipe_assistant_backup.db

# Or use SQLite dump
sqlite3 recipe_assistant.db .dump > backup.sql
```

### Restoring Database

```bash
# From copy
cp recipe_assistant_backup.db recipe_assistant.db

# From SQL dump
sqlite3 recipe_assistant.db < backup.sql
```

### Inspecting Database

```bash
# Open database in SQLite CLI
sqlite3 recipe_assistant.db

# Useful commands:
.tables              # List tables
.schema users        # Show table schema
SELECT * FROM users; # View all users
.exit                # Exit
```

## Migration from File-Based System

**Automatic Migration:**

The system will automatically migrate existing users:
1. Existing users are listed from file system
2. When a user logs in, if they're not in DB, they're added
3. Language is read from preferences.json and added to DB
4. User directory structure remains unchanged

**Manual Migration Script:**

You can create a migration script to add all existing users at once:

```python
import os
import json
import database as db

db.init_database()

users_dir = "users"
for username in os.listdir(users_dir):
    prefs_file = os.path.join(users_dir, username, "preferences.json")
    if os.path.exists(prefs_file):
        with open(prefs_file) as f:
            prefs = json.load(f)
        language = prefs.get("language", "en")
        if not db.user_exists(username):
            db.create_user(username, language)
            print(f"Migrated: {username} ({language})")
```

## Error Handling

The database module uses context managers for automatic:
- Connection management
- Transaction commit on success
- Rollback on error
- Connection cleanup

All errors are propagated to the caller for appropriate handling.

## Future Extensions

The database schema is designed to be easily extensible:

### Planned Tables

**Recipes:**
```sql
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    name TEXT,
    ingredients TEXT,
    instructions TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
```

**Ratings:**
```sql
CREATE TABLE ratings (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    recipe_id INTEGER,
    rating INTEGER,
    comment TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(id)
)
```

### Adding New Fields

To add fields to the users table:

1. Create migration script:
```python
with db.get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE users ADD COLUMN dietary_prefs TEXT")
```

2. Update `create_user()` and `get_user()` functions
3. Update application logic to use new field

## Performance Considerations

- **Indexes**: Username is indexed for O(log n) lookups
- **Connection Pooling**: Context manager ensures efficient connection use
- **Row Factory**: Enables column access by name (more readable)
- **Small Footprint**: Database file < 1MB for typical usage

## Security Notes

- No passwords stored (authentication not implemented)
- Database file should be backed up regularly
- Sensitive data (API keys) stored in environment variables, not DB
- Username validation prevents SQL injection (parameterized queries)

## Troubleshooting

**Database locked error:**
- Another process has the database open
- Close other connections or wait

**Constraint violation:**
- Attempting to create duplicate username
- Check with `db.user_exists()` first

**File not found:**
- Database not initialized
- Run `db.init_database()` first
