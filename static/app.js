// Global state
let currentUser = null;
let currentLanguage = 'en';
let selectedRating = null;
let selectedRecipeId = null;
let selectedDishName = null;

// API base URL
const API_BASE = '';

// Translations
const translations = {
    en: {
        suggestTitle: 'Get Recipe Suggestions',
        suggestSubtitle: 'Tell me what ingredients you have',
        ingredientsLabel: 'Your Ingredients:',
        feedbackTitle: 'Give Feedback',
        preferencesTitle: 'Your Preferences',
        likedTitle: 'Liked Dishes',
        dislikedTitle: 'Disliked Dishes',
        commentLabel: 'Comment (optional):',
        feedbackFormTitle: 'Rate:',
        noUnratedRecipes: 'No unrated recipes found. Get some suggestions first!',
        totalRatings: 'Total Ratings',
        avgRating: 'Average Rating'
    },
    de: {
        suggestTitle: 'Rezeptvorschläge erhalten',
        suggestSubtitle: 'Sag mir, welche Zutaten du hast',
        ingredientsLabel: 'Deine Zutaten:',
        feedbackTitle: 'Feedback geben',
        preferencesTitle: 'Deine Präferenzen',
        likedTitle: 'Gemochte Gerichte',
        dislikedTitle: 'Nicht gemochte Gerichte',
        commentLabel: 'Kommentar (optional):',
        feedbackFormTitle: 'Bewerte:',
        noUnratedRecipes: 'Keine unbewerteten Rezepte gefunden. Hole dir zuerst Vorschläge!',
        totalRatings: 'Anzahl Bewertungen',
        avgRating: 'Durchschnittsbewertung'
    }
};

function t(key) {
    return translations[currentLanguage]?.[key] || translations.en[key] || key;
}

function updateUILanguage() {
    document.getElementById('suggestTitle').textContent = t('suggestTitle');
    document.getElementById('suggestSubtitle').textContent = t('suggestSubtitle');
    document.getElementById('ingredientsLabel').textContent = t('ingredientsLabel');
    document.getElementById('feedbackTitle').textContent = t('feedbackTitle');
    document.getElementById('preferencesTitle').textContent = t('preferencesTitle');
    document.getElementById('likedTitle').textContent = t('likedTitle');
    document.getElementById('dislikedTitle').textContent = t('dislikedTitle');
    document.getElementById('commentLabel').textContent = t('commentLabel');
    document.getElementById('noUnratedRecipes').textContent = t('noUnratedRecipes');
}

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
    alert('Success: ' + message);
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
async function loadUsers() {
    try {
        showLoading();
        const users = await apiCall('/api/users');
        
        const userList = document.getElementById('userList');
        userList.innerHTML = '';
        
        if (users.length === 0) {
            userList.innerHTML = '<p class="info-text">No users yet. Create one to get started!</p>';
        } else {
            users.forEach(user => {
                const userDiv = document.createElement('div');
                userDiv.className = 'user-item';
                userDiv.innerHTML = `
                    <div class="user-info">
                        <div class="user-name">${user.username}</div>
                        <div class="user-language">${user.language === 'en' ? 'English' : 'Deutsch'}</div>
                    </div>
                `;
                userDiv.onclick = () => loginUser(user.username);
                userList.appendChild(userDiv);
            });
        }
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

async function loginUser(username) {
    try {
        showLoading();
        const user = await apiCall('/api/users/login', 'POST', { username });
        
        currentUser = user;
        currentLanguage = user.language;
        
        document.getElementById('loginScreen').style.display = 'none';
        document.getElementById('appScreen').style.display = 'block';
        document.getElementById('currentUser').textContent = user.username;
        
        updateUILanguage();
        loadUnratedRecipes();
        loadPreferences();
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

async function createUser() {
    const username = document.getElementById('newUsername').value.trim();
    const language = document.getElementById('newUserLanguage').value;
    
    if (!username) {
        showError('Username cannot be empty');
        return;
    }
    
    try {
        showLoading();
        const user = await apiCall('/api/users/create', 'POST', { username, language });
        
        showSuccess('User created successfully!');
        document.getElementById('newUserForm').style.display = 'none';
        document.getElementById('newUsername').value = '';
        
        await loadUsers();
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

function logout() {
    currentUser = null;
    currentLanguage = 'en';
    
    document.getElementById('loginScreen').style.display = 'block';
    document.getElementById('appScreen').style.display = 'none';
    
    loadUsers();
}

// Recipe suggestions
async function getSuggestions() {
    const ingredients = document.getElementById('ingredients').value.trim();
    
    if (!ingredients) {
        showError('Please enter some ingredients');
        return;
    }
    
    try {
        showLoading();
        const result = await apiCall('/api/recipes/suggest', 'POST', {
            user_id: currentUser.id,
            ingredients,
            language: currentLanguage
        });
        
        if (result.success) {
            const suggestionsDiv = document.getElementById('recipeSuggestions');
            suggestionsDiv.innerHTML = `
                <div class="suggestion-content">${result.raw_response}</div>
            `;
            
            // Reload unrated recipes
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
                    <div class="recipe-ingredients">${recipe.ingredients.substring(0, 100)}...</div>
                    <div class="recipe-date">${new Date(recipe.suggested_at).toLocaleDateString()}</div>
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
    
    // Clear selected rating buttons
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
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

// Preferences
async function loadPreferences() {
    try {
        const prefs = await apiCall(`/api/preferences/${currentUser.id}`);
        
        // Display stats
        const statsDiv = document.getElementById('statsDisplay');
        statsDiv.innerHTML = `
            <div class="stat-card">
                <div class="stat-value">${prefs.stats.total_ratings}</div>
                <div class="stat-label">${t('totalRatings')}</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${prefs.stats.avg_rating.toFixed(1)}</div>
                <div class="stat-label">${t('avgRating')}</div>
            </div>
        `;
        
        // Display liked dishes
        const likedList = document.getElementById('likedList');
        if (prefs.liked_dishes.length === 0) {
            likedList.innerHTML = '<li style="list-style: none;">No liked dishes yet</li>';
        } else {
            likedList.innerHTML = prefs.liked_dishes.slice(-10).map(dish => 
                `<li>${dish}</li>`
            ).join('');
        }
        
        // Display disliked dishes
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
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName + 'Tab').classList.add('active');
    
    // Activate button
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Load data for the tab
    if (tabName === 'feedback') {
        loadUnratedRecipes();
    } else if (tabName === 'preferences') {
        loadPreferences();
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Login screen
    loadUsers();
    
    document.getElementById('showNewUserBtn').onclick = () => {
        document.getElementById('newUserForm').style.display = 'block';
    };
    
    document.getElementById('cancelNewUserBtn').onclick = () => {
        document.getElementById('newUserForm').style.display = 'none';
    };
    
    document.getElementById('createUserBtn').onclick = createUser;
    
    // App screen
    document.getElementById('logoutBtn').onclick = logout;
    
    // Tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.onclick = () => switchTab(btn.dataset.tab);
    });
    
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
    
    // Enter key support
    document.getElementById('ingredients').onkeypress = (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            getSuggestions();
        }
    };
    
    document.getElementById('newUsername').onkeypress = (e) => {
        if (e.key === 'Enter') {
            createUser();
        }
    };
});
