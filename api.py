"""
Web API Server for Recipe Assistant
FastAPI REST API that uses the service layer
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import anthropic
import os
import database as db
from services import UserService, RecipeService, RatingService

# Initialize FastAPI app
app = FastAPI(
    title="Recipe Assistant API",
    description="AI-powered recipe suggestion system",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
user_service = UserService()
recipe_service = RecipeService()
rating_service = RatingService()

# Initialize Anthropic client
api_key = os.environ.get("ANTHROPIC_API_KEY")
if api_key:
    client = anthropic.Anthropic(api_key=api_key)
    recipe_service.set_client(client)

# Initialize database
db.init_database()


# ============================================================================
# Pydantic Models (Request/Response schemas)
# ============================================================================

class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    language: str = Field(default="en", pattern="^(en|de)$")

class UserLogin(BaseModel):
    username: str

class UserResponse(BaseModel):
    id: int
    username: str
    language: str
    created_at: str
    last_login: str

class RecipeSuggestRequest(BaseModel):
    user_id: int
    ingredients: str = Field(..., min_length=1)
    language: str = Field(default="en", pattern="^(en|de)$")

class RecipeSuggestResponse(BaseModel):
    success: bool
    recipes: Optional[List[str]] = None
    recipe_ids: Optional[List[int]] = None
    raw_response: Optional[str] = None
    error: Optional[str] = None

class RecipeResponse(BaseModel):
    id: int
    user_id: int
    name: str
    ingredients: str
    suggested_at: str

class RatingCreate(BaseModel):
    user_id: int
    dish_name: str = Field(..., min_length=1)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    recipe_id: Optional[int] = None

class RatingResponse(BaseModel):
    id: int
    user_id: int
    recipe_id: Optional[int]
    dish_name: str
    rating: int
    comment: Optional[str]
    rated_at: str

class RatingStatsResponse(BaseModel):
    total_ratings: int
    avg_rating: float
    min_rating: int
    max_rating: int

class PreferencesResponse(BaseModel):
    liked_dishes: List[str]
    disliked_dishes: List[str]
    stats: RatingStatsResponse
    unrated_recipes: List[RecipeResponse]


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Serve the main web interface"""
    return FileResponse("static/index.html")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "api_key_configured": api_key is not None
    }


# ============================================================================
# User Endpoints
# ============================================================================

@app.post("/api/users/create", response_model=UserResponse)
async def create_user(user: UserCreate):
    """Create a new user"""
    result = user_service.create_user(user.username, user.language)
    
    if result['success']:
        return result['user']
    else:
        raise HTTPException(status_code=400, detail=result['error'])

@app.post("/api/users/login", response_model=UserResponse)
async def login_user(login: UserLogin):
    """Login/authenticate a user"""
    result = user_service.authenticate_user(login.username)
    
    if result['success']:
        return result['user']
    else:
        raise HTTPException(status_code=404, detail=result['error'])

@app.get("/api/users", response_model=List[UserResponse])
async def list_users():
    """Get list of all users"""
    users = user_service.list_users()
    return users

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Get user by ID"""
    user = user_service.get_user_by_id(user_id)
    
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")


# ============================================================================
# Recipe Endpoints
# ============================================================================

@app.post("/api/recipes/suggest", response_model=RecipeSuggestResponse)
async def suggest_recipes(request: RecipeSuggestRequest):
    """Get recipe suggestions from Claude"""
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="ANTHROPIC_API_KEY not configured"
        )
    
    result = recipe_service.suggest_recipes(
        request.user_id,
        request.ingredients,
        request.language
    )
    
    return result

@app.get("/api/recipes/user/{user_id}", response_model=List[RecipeResponse])
async def get_user_recipes(user_id: int, limit: Optional[int] = None):
    """Get all recipes for a user"""
    recipes = recipe_service.get_user_recipes(user_id, limit)
    return recipes

@app.get("/api/recipes/unrated/{user_id}", response_model=List[RecipeResponse])
async def get_unrated_recipes(user_id: int):
    """Get unrated recipes for a user"""
    recipes = recipe_service.get_unrated_recipes(user_id)
    return recipes


# ============================================================================
# Rating Endpoints
# ============================================================================

@app.post("/api/ratings/create", response_model=RatingResponse)
async def create_rating(rating: RatingCreate):
    """Submit a rating for a dish"""
    result = rating_service.submit_rating(
        rating.user_id,
        rating.dish_name,
        rating.rating,
        rating.comment,
        rating.recipe_id
    )
    
    if result['success']:
        # Fetch and return the created rating
        rating_data = db.get_rating(result['rating_id'])
        return rating_data
    else:
        raise HTTPException(status_code=400, detail=result['error'])

@app.get("/api/ratings/user/{user_id}", response_model=List[RatingResponse])
async def get_user_ratings(user_id: int, limit: Optional[int] = None):
    """Get all ratings for a user"""
    ratings = rating_service.get_user_ratings(user_id, limit)
    return ratings

@app.get("/api/ratings/stats/{user_id}", response_model=RatingStatsResponse)
async def get_rating_stats(user_id: int):
    """Get rating statistics for a user"""
    stats = rating_service.get_rating_stats(user_id)
    return stats


# ============================================================================
# Preferences Endpoint
# ============================================================================

@app.get("/api/preferences/{user_id}", response_model=PreferencesResponse)
async def get_preferences(user_id: int):
    """Get all user preferences (liked/disliked dishes, stats, unrated recipes)"""
    liked = rating_service.get_liked_dishes(user_id)
    disliked = rating_service.get_disliked_dishes(user_id)
    stats = rating_service.get_rating_stats(user_id)
    unrated = recipe_service.get_unrated_recipes(user_id)
    
    return {
        "liked_dishes": liked,
        "disliked_dishes": disliked,
        "stats": stats,
        "unrated_recipes": unrated
    }


# Mount static files (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
