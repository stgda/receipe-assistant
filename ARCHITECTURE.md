# Architecture Documentation

## Overview

The Recipe Assistant follows a **three-layer architecture** designed for easy extension to web and mobile interfaces:

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │     CLI      │  │  Web API     │  │  Mobile App  │      │
│  │ (current)    │  │  (future)    │  │  (future)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     Service Layer                            │
│  ┌────────────────┐  ┌──────────────────┐  ┌─────────────┐ │
│  │  UserService   │  │  RecipeService   │  │RatingService│ │
│  └────────────────┘  └──────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     Data Layer                               │
│  ┌──────────────────┐           ┌────────────────────────┐  │
│  │  Database Module │           │    File System (Logs)  │  │
│  │   (SQLite)       │           │                        │  │
│  └──────────────────┘           └────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Layer Responsibilities

### 1. Presentation Layer (UI/Interface)

**Current: CLI (`recipe_assistant.py`)**
- User interaction
- Input validation
- Display formatting
- Translation (i18n)
- Menu navigation

**Future: Web API (FastAPI/Flask)**
- REST endpoints
- Request/response handling
- Authentication/JWT
- CORS configuration

**Future: Mobile App (React Native/Flutter)**
- Native UI components
- Touch interactions
- Push notifications
- Offline support

### 2. Service Layer (`services.py`)

**Purpose**: Business logic independent of interface

**UserService:**
- User authentication/login
- User creation with validation
- Language preference management
- User listing and retrieval

**RecipeService:**
- Claude API integration
- Recipe suggestion generation
- Recipe name parsing
- Recipe retrieval (all/unrated)

**RatingService:**
- Feedback submission
- Rating statistics
- Liked/disliked dish aggregation
- Rating history retrieval

**Benefits:**
- ✅ Reusable across all interfaces
- ✅ Testable without UI
- ✅ Clear separation of concerns
- ✅ Easy to mock for testing

### 3. Data Layer (`database.py`)

**Purpose**: Data persistence abstraction

**Database Operations:**
- User CRUD operations
- Recipe CRUD operations  
- Rating CRUD operations
- Query optimization (indexes)
- Transaction management

**File System:**
- API call logs (JSON)
- Future: attachments, exports

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

### Recipes Table
```sql
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    ingredients TEXT NOT NULL,
    suggested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
```

### Ratings Table
```sql
CREATE TABLE ratings (
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
```

**Relationships:**
- One User → Many Recipes (one-to-many)
- One User → Many Ratings (one-to-many)
- One Recipe → Zero or One Rating (one-to-one optional)

**Indexes:**
- `idx_username` on users.username
- `idx_recipes_user` on recipes.user_id
- `idx_ratings_user` on ratings.user_id
- `idx_ratings_recipe` on ratings.recipe_id

## Data Flow Examples

### Example 1: Getting Recipe Suggestions

```
CLI → RecipeService.suggest_recipes(user_id, ingredients, language)
      ↓
      RecipeService gets user preferences from database
      ↓
      RecipeService calls Claude API
      ↓
      RecipeService parses recipe names
      ↓
      RecipeService saves recipes to database via db.create_recipe()
      ↓
      RecipeService returns formatted response
      ↓
CLI displays recipes to user
```

### Example 2: Submitting Feedback

```
CLI → RatingService.submit_rating(user_id, dish_name, rating, comment, recipe_id)
      ↓
      RatingService validates rating (1-5)
      ↓
      RatingService saves to database via db.create_rating()
      ↓
      RatingService returns success/failure
      ↓
CLI displays confirmation
```

### Example 3: Viewing Preferences

```
CLI → RatingService.get_liked_dishes(user_id)
CLI → RatingService.get_disliked_dishes(user_id)
CLI → RatingService.get_rating_stats(user_id)
CLI → RecipeService.get_unrated_recipes(user_id)
      ↓
      Services query database
      ↓
      Services return aggregated data
      ↓
CLI formats and displays
```

## Future Extensions

### Web API (FastAPI Example)

```python
from fastapi import FastAPI, Depends
from services import UserService, RecipeService, RatingService

app = FastAPI()

# Services initialized once
user_service = UserService()
recipe_service = RecipeService()
rating_service = RatingService()

@app.post("/api/recipes/suggest")
async def suggest_recipes(
    user_id: int,
    ingredients: str,
    language: str = "en"
):
    result = recipe_service.suggest_recipes(
        user_id, ingredients, language
    )
    return result

@app.post("/api/ratings")
async def submit_rating(
    user_id: int,
    dish_name: str,
    rating: int,
    comment: str = None,
    recipe_id: int = None
):
    result = rating_service.submit_rating(
        user_id, dish_name, rating, comment, recipe_id
    )
    return result

@app.get("/api/users/{user_id}/preferences")
async def get_preferences(user_id: int):
    return {
        "liked": rating_service.get_liked_dishes(user_id),
        "disliked": rating_service.get_disliked_dishes(user_id),
        "stats": rating_service.get_rating_stats(user_id),
        "unrated": recipe_service.get_unrated_recipes(user_id)
    }
```

### Mobile App (Conceptual)

```javascript
// RecipeScreen.js
import { recipeService } from './services';

async function getSuggestions() {
  const userId = await getUserId();
  const ingredients = await getUserInput();
  
  const result = await recipeService.suggestRecipes(
    userId,
    ingredients,
    userLanguage
  );
  
  if (result.success) {
    setRecipes(result.recipes);
  } else {
    showError(result.error);
  }
}
```

## Benefits of This Architecture

### 1. Separation of Concerns
- UI logic separate from business logic
- Business logic separate from data access
- Easy to understand and modify

### 2. Testability
```python
# Test service layer without UI
def test_recipe_suggestion():
    service = RecipeService(mock_client)
    result = service.suggest_recipes(1, "tomatoes, pasta", "en")
    assert result['success'] == True
    assert len(result['recipes']) > 0
```

### 3. Reusability
- Same services used by CLI, Web, and Mobile
- No code duplication
- Consistent business logic

### 4. Maintainability
- Changes to business logic in one place
- Database changes isolated to database module
- UI changes don't affect backend

### 5. Scalability
- Easy to add new interfaces
- Easy to add new features
- Easy to optimize individual layers

## Migration Path

### Phase 1: Current (CLI)
✅ CLI interface
✅ Service layer
✅ Database layer
✅ Multi-user support
✅ Multi-language support

### Phase 2: Web API (Future)
- [ ] FastAPI/Flask REST API
- [ ] JWT authentication
- [ ] API documentation (Swagger)
- [ ] Rate limiting
- [ ] CORS configuration

### Phase 3: Web Frontend (Future)
- [ ] React/Vue.js web app
- [ ] User authentication UI
- [ ] Recipe browsing interface
- [ ] Rating submission forms
- [ ] Responsive design

### Phase 4: Mobile App (Future)
- [ ] React Native/Flutter app
- [ ] Native push notifications
- [ ] Offline support
- [ ] Camera for ingredient scanning
- [ ] App store deployment

## Development Guidelines

### Adding New Features

1. **Add to Data Layer** (if database changes needed)
   - Update schema in `database.py`
   - Add migration script
   - Add CRUD functions

2. **Add to Service Layer**
   - Create/update service methods
   - Implement business logic
   - Return structured responses

3. **Add to Presentation Layer**
   - CLI: Add menu option and UI logic
   - Web: Add REST endpoint
   - Mobile: Add screen/component

### Testing Strategy

**Unit Tests:**
- Test service methods independently
- Mock database layer
- Mock Claude API

**Integration Tests:**
- Test service + database together
- Use test database
- Verify data persistence

**End-to-End Tests:**
- Test complete user flows
- Use test database and mock APIs
- Verify UI correctly uses services

## Current File Structure

```
recipe-assistant/
├── database.py              # Data layer
├── services.py              # Service layer
├── recipe_assistant.py      # Presentation layer (CLI)
├── test_database.py         # Database tests
├── recipe_assistant.db      # SQLite database
├── users/                   # User log files
│   └── {username}/
│       └── api_log.json
├── README.md
├── DATABASE.md
├── ARCHITECTURE.md (this file)
└── requirements.txt
```

## Design Patterns Used

1. **Service Layer Pattern**: Business logic separation
2. **Repository Pattern**: Data access abstraction
3. **Context Manager**: Database connection management
4. **Factory Pattern**: Service initialization
5. **Strategy Pattern**: Multi-language support

## Security Considerations

### Current
- No authentication (CLI assumes local use)
- SQLite file permissions
- API key in environment variable

### Future (Web/Mobile)
- JWT token authentication
- Password hashing (bcrypt)
- Rate limiting
- Input sanitization
- HTTPS only
- CORS restrictions

## Performance Considerations

- Database indexes for fast queries
- Connection pooling (future)
- Caching (future: Redis)
- Pagination for large result sets (future)
- Async/await for API calls (future)

## Conclusion

This architecture provides a solid foundation for:
- ✅ Easy maintenance and updates
- ✅ Adding new interfaces without changing business logic
- ✅ Testing at all levels
- ✅ Scaling to web and mobile
- ✅ Team collaboration (clear module boundaries)

The separation of concerns ensures that the Recipe Assistant can grow from a CLI prototype to a full-fledged multi-platform application.
