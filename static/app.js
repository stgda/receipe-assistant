// Global state
let currentUser = null;
let currentLanguage = 'en';
let selectedRating = null;
let selectedRecipeId = null;
let selectedDishName = null;
let currentFilter = 'all';

// API base URL
const API_BASE = '';

// Utility functions
function showLoading() {
    document.getElementById('loading').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

function showError(message) {
    alert('Error: ' + message);
}

function showSuccess(message) {
    alert(message);
}

// API functions
async function apiCall(endpoint, method = 'GET', body = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (body) {
        options.body = JSON.stringify(body);
    }
    
    const response = await fetch(API_BASE + endpoint, options);
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'API request failed');
    }
    
    return response.json();
}

// User management
async function loginUser() {
    const username = document.getElementById('usernameInput').value.trim();
    
    if (!username) {
        showError('Please enter a username');
        return;
    }
    
    try {
        showLoading();
        const user = await apiCall('/api/users/login', 'POST', { username });
        
        currentUser = user;
        currentLanguage = user.language;
        
        // Set default servings
        document.getElementById('servings').value = user.default_servings || 1;
        
        document.getElementById('loginScreen').style.display = 'none';
        document.getElementById('appScreen').style.display = 'block';
        document.getElementById('currentUser').textContent = user.username;
        
        loadUnratedRecipes();
        loadPreferences();
    } catch (error) {
        // User not found - show create account option
        document.getElementById('loginError').style.display = 'none';
        document.getElementById('createUserPrompt').style.display = 'block';
    } finally {
        hideLoading();
    }
}

async function createUser() {
    const username = document.getElementById('usernameInput').value.trim();
    const language = document.getElementById('newUserLanguage').value;
    
    if (!username) {
        showError('Username cannot be empty');
        return;
    }
    
    try {
        showLoading();
        const user = await apiCall('/api/users/create', 'POST', { username, language });
        
        showSuccess('User created successfully!');
        
        // Auto-login
        currentUser = user;
        currentLanguage = user.language;
        
        document.getElementById('servings').value = user.default_servings || 1;
        
        document.getElementById('loginScreen').style.display = 'none';
        document.getElementById('appScreen').style.display = 'block';
        document.getElementById('currentUser').textContent = user.username;
        
        loadUnratedRecipes();
        loadPreferences();
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

function cancelCreate() {
    document.getElementById('createUserPrompt').style.display = 'none';
    document.getElementById('usernameInput').value = '';
    document.getElementById('usernameInput').focus();
}

function logout() {
    currentUser = null;
    currentLanguage = 'en';
    
    document.getElementById('loginScreen').style.display = 'block';
    document.getElementById('appScreen').style.display = 'none';
    document.getElementById('usernameInput').value = '';
    document.getElementById('createUserPrompt').style.display = 'none';
}

// Servings management
async function saveServings() {
    const servings = parseInt(document.getElementById('servings').value);
    
    if (servings < 1 || servings > 20) {
        showError('Servings must be between 1 and 20');
        return;
    }
    
    try {
        showLoading();
        await apiCall('/api/users/servings', 'PUT', {
            user_id: currentUser.id,
            servings: servings
        });
        
        currentUser.default_servings = servings;
        showSuccess('Default servings saved!');
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

// Recipe suggestions
async function getSuggestions() {
    const ingredients = document.getElementById('ingredients').value.trim();
    const servings = parseInt(document.getElementById('servings').value);
    const excludedInput = document.getElementById('excludedIngredients').value.trim();
    
    if (!ingredients) {
        showError('Please enter some ingredients');
        return;
    }
    
    const excludedIngredients = excludedInput 
        ? excludedInput.split(',').map(i => i.trim()).filter(i => i)
        : null;
    
    try {
        showLoading();
        const result = await apiCall('/api/recipes/suggest', 'POST', {
            user_id: currentUser.id,
            ingredients,
            language: currentLanguage,
            servings,
            excluded_ingredients: excludedIngredients
        });
        
        if (result.success) {
            const suggestionsDiv = document.getElementById('recipeSuggestions');
            suggestionsDiv.innerHTML = `
                <div class="suggestion-content">${result.raw_response}</div>
            `;
            
            loadUnratedRecipes();
        } else {
            showError(result.error || 'Failed to get suggestions');
        }
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

// Unrated recipes
async function loadUnratedRecipes() {
    try {
        const recipes = await apiCall(`/api/recipes/unrated/${currentUser.id}`);
        
        const container = document.getElementById('unratedRecipes');
        const noRecipesMsg = document.getElementById('noUnratedRecipes');
        
        if (recipes.length === 0) {
            container.innerHTML = '';
            noRecipesMsg.style.display = 'block';
        } else {
            noRecipesMsg.style.display = 'none';
            container.innerHTML = recipes.map(recipe => `
                <div class="recipe-item" onclick="selectRecipeForRating(${recipe.id}, '${recipe.name.replace(/'/g, "\\'")}')">
                    <div class="recipe-name">${recipe.name}</div>
                    <div class="recipe-ingredients">${recipe.ingredients.substring(0, 100)}${recipe.ingredients.length > 100 ? '...' : ''}</div>
                    <div class="recipe-date">
                        ${recipe.servings} servings • ${new Date(recipe.suggested_at).toLocaleDateString()}
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Failed to load unrated recipes:', error);
    }
}

function selectRecipeForRating(recipeId, dishName) {
    selectedRecipeId = recipeId;
    selectedDishName = dishName;
    selectedRating = null;
    
    document.getElementById('dishNameDisplay').textContent = dishName;
    document.getElementById('feedbackForm').style.display = 'block';
    document.getElementById('comment').value = '';
    
    document.querySelectorAll('.rating-btn').forEach(btn => {
        btn.classList.remove('selected');
    });
}

function cancelFeedback() {
    selectedRecipeId = null;
    selectedDishName = null;
    selectedRating = null;
    document.getElementById('feedbackForm').style.display = 'none';
}

async function submitFeedback() {
    if (!selectedRating) {
        showError('Please select a rating');
        return;
    }
    
    const comment = document.getElementById('comment').value.trim() || null;
    
    try {
        showLoading();
        await apiCall('/api/ratings/create', 'POST', {
            user_id: currentUser.id,
            recipe_id: selectedRecipeId,
            dish_name: selectedDishName,
            rating: selectedRating,
            comment
        });
        
        showSuccess('Feedback submitted!');
        cancelFeedback();
        loadUnratedRecipes();
        loadPreferences();
        
        if (document.getElementById('historyTab').classList.contains('active')) {
            loadRecipeHistory();
        }
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

// Recipe history with filtering
async function loadRecipeHistory() {
    try {
        showLoading();
        let recipes;
        
        if (currentFilter === 'all') {
            recipes = await apiCall(`/api/recipes/filtered/${currentUser.id}?include_unrated=true`);
        } else if (currentFilter === 'unrated') {
            recipes = await apiCall(`/api/recipes/unrated/${currentUser.id}`);
        } else {
            const rating = parseInt(currentFilter);
            let min_rating, max_rating;
            
            if (rating === 5) {
                min_rating = 5;
                max_rating = 5;
            } else if (rating === 4) {
                min_rating = 4;
                max_rating = 5;
            } else if (rating === 3) {
                min_rating = 3;
                max_rating = 5;
            } else if (rating === 2) {
                min_rating = 1;
                max_rating = 2;
            } else if (rating === 1) {
                min_rating = 1;
                max_rating = 1;
            }
            
            recipes = await apiCall(
                `/api/recipes/filtered/${currentUser.id}?min_rating=${min_rating}&max_rating=${max_rating}&include_unrated=false`
            );
        }
        
        const container = document.getElementById('recipeHistory');
        
        if (recipes.length === 0) {
            container.innerHTML = '<p class="info-text">No recipes match the selected filter.</p>';
        } else {
            container.innerHTML = recipes.map(recipe => {
                const ratingText = recipe.rating 
                    ? `${'⭐'.repeat(recipe.rating)}` 
                    : 'Not rated';
                
                return `
                    <div class="recipe-item" onclick="showRecipeDetail(${recipe.id})">
                        <div class="recipe-name">${recipe.name}</div>
                        <div class="recipe-ingredients">
                            ${recipe.servings} servings • ${recipe.ingredients.substring(0, 80)}${recipe.ingredients.length > 80 ? '...' : ''}
                        </div>
                        <div class="recipe-date">
                            ${ratingText} • ${new Date(recipe.suggested_at).toLocaleDateString()}
                        </div>
                    </div>
                `;
            }).join('');
        }
    } catch (error) {
        console.error('Failed to load recipe history:', error);
    } finally {
        hideLoading();
    }
}

async function showRecipeDetail(recipeId) {
    try {
        showLoading();
        const recipe = await apiCall(`/api/recipes/user/${currentUser.id}`);
        const selectedRecipe = recipe.find(r => r.id === recipeId);
        
        if (!selectedRecipe) {
            showError('Recipe not found');
            return;
        }
        
        document.getElementById('recipeHistory').style.display = 'none';
        document.querySelector('.filter-controls').style.display = 'none';
        document.getElementById('recipeDetail').style.display = 'block';
        
        document.getElementById('detailName').textContent = selectedRecipe.name;
        document.getElementById('detailServings').textContent = selectedRecipe.servings;
        document.getElementById('detailIngredients').textContent = selectedRecipe.ingredients;
        document.getElementById('detailDate').textContent = new Date(selectedRecipe.suggested_at).toLocaleString();
        
        if (selectedRecipe.rating) {
            document.getElementById('detailRating').style.display = 'block';
            document.getElementById('detailRatingValue').textContent = '⭐'.repeat(selectedRecipe.rating);
        } else {
            document.getElementById('detailRating').style.display = 'none';
        }
        
        document.getElementById('detailFullText').textContent = selectedRecipe.full_text || 'No details available';
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

function closeRecipeDetail() {
    document.getElementById('recipeHistory').style.display = 'block';
    document.querySelector('.filter-controls').style.display = 'block';
    document.getElementById('recipeDetail').style.display = 'none';
}

// Preferences
async function loadPreferences() {
    try {
        const prefs = await apiCall(`/api/preferences/${currentUser.id}`);
        
        const statsDiv = document.getElementById('statsDisplay');
        statsDiv.innerHTML = `
            <div class="stat-card">
                <div class="stat-value">${prefs.stats.total_ratings}</div>
                <div class="stat-label">Total Ratings</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${prefs.stats.avg_rating.toFixed(1)}</div>
                <div class="stat-label">Average Rating</div>
            </div>
        `;
        
        const likedList = document.getElementById('likedList');
        if (prefs.liked_dishes.length === 0) {
            likedList.innerHTML = '<li style="list-style: none;">No liked dishes yet</li>';
        } else {
            likedList.innerHTML = prefs.liked_dishes.slice(-10).map(dish => 
                `<li>${dish}</li>`
            ).join('');
        }
        
        const dislikedList = document.getElementById('dislikedList');
        dislikedList.parentElement.className = 'dish-list disliked';
        if (prefs.disliked_dishes.length === 0) {
            dislikedList.innerHTML = '<li style="list-style: none;">No disliked dishes yet</li>';
        } else {
            dislikedList.innerHTML = prefs.disliked_dishes.slice(-10).map(dish => 
                `<li>${dish}</li>`
            ).join('');
        }
    } catch (error) {
        console.error('Failed to load preferences:', error);
    }
}

// Tab switching
function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    document.getElementById(tabName + 'Tab').classList.add('active');
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    if (tabName === 'feedback') {
        loadUnratedRecipes();
    } else if (tabName === 'preferences') {
        loadPreferences();
    } else if (tabName === 'history') {
        loadRecipeHistory();
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Login screen
    document.getElementById('loginBtn').onclick = loginUser;
    document.getElementById('createUserBtn').onclick = createUser;
    document.getElementById('cancelCreateBtn').onclick = cancelCreate;
    
    document.getElementById('usernameInput').onkeypress = (e) => {
        if (e.key === 'Enter') {
            loginUser();
        }
    };
    
    // App screen
    document.getElementById('logoutBtn').onclick = logout;
    
    // Tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.onclick = () => switchTab(btn.dataset.tab);
    });
    
    // Servings
    document.getElementById('saveServingsBtn').onclick = saveServings;
    
    // Suggest tab
    document.getElementById('getSuggestionsBtn').onclick = getSuggestions;
    
    // Feedback tab
    document.querySelectorAll('.rating-btn').forEach(btn => {
        btn.onclick = () => {
            selectedRating = parseInt(btn.dataset.rating);
            document.querySelectorAll('.rating-btn').forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
        };
    });
    
    document.getElementById('submitFeedbackBtn').onclick = submitFeedback;
    document.getElementById('cancelFeedbackBtn').onclick = cancelFeedback;
    
    // History tab filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.onclick = () => {
            currentFilter = btn.dataset.filter;
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            loadRecipeHistory();
        };
    });
    
    document.getElementById('closeDetailBtn').onclick = closeRecipeDetail;
    
    // Keyboard shortcuts
    document.getElementById('ingredients').onkeypress = (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            getSuggestions();
        }
    };
});
