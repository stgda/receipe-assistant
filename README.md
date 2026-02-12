# AI Recipe Assistant

A simple prototype of an AI-powered recipe assistant that suggests lunch based on available ingredients and learns your taste preferences.

## Features

✅ **Multi-User Support** - Each user has their own preferences and recipe history
✅ Recipe suggestions based on available ingredients
✅ Feedback system to learn user preferences
✅ Storage of ratings in JSON files
✅ Consideration of previous preferences in new suggestions
✅ API call logging for debugging

## Installation

### 1. Install Python

You need Python 3.8 or newer. Check your version:

```bash
python3 --version
```

### 2. Install Anthropic SDK

```bash
pip install anthropic
```

### 3. Set up API Key

Get an API key from Anthropic:
- Go to https://console.anthropic.com/
- Create an account (if you don't have one)
- Navigate to "API Keys" and create a new key

Set the API key as environment variable:

**Linux/Mac:**
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY='your-api-key-here'
```

**Permanently save (Linux/Mac):**
Add the line to your `~/.bashrc` or `~/.zshrc`:
```bash
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

## Usage

Start the program:

```bash
python3 recipe_assistant.py
```

### Workflow:

1. **User Selection:**
   - On first start, create a new user
   - On subsequent starts, select your existing user or create a new one
   - Each user has their own preferences and history

2. **Get recipe suggestions:**
   - Select option 1
   - Enter your available ingredients (e.g., "tomatoes, mozzarella, basil, pasta")
   - Receive 2-3 suitable recipe suggestions
   - Optional: Give immediate feedback if you've already cooked

3. **Give feedback:**
   - Select option 2 after cooking
   - Choose from recently suggested recipes or enter manually
   - Rate the dish (1-5 stars)
   - Your feedback is saved and used for future suggestions

4. **View preferences:**
   - Select option 3
   - See which dishes you like/dislike
   - View unrated recipe suggestions

5. **View API log:**
   - Select option 4
   - See recent prompts and responses
   - Useful for debugging and optimizing prompts

## File Structure

```
recipe-assistant/
├── recipe_assistant.py     # Main program
├── requirements.txt        # Python dependencies
├── README.md              # Documentation
├── users/                 # User data directory (auto-created)
│   ├── alice/
│   │   ├── preferences.json  # Alice's preferences
│   │   └── api_log.json      # Alice's API log
│   └── bob/
│       ├── preferences.json  # Bob's preferences
│       └── api_log.json      # Bob's API log
└── .gitignore            # Git ignore file
```

## Multi-User Features

- **Separate Preferences:** Each user has their own liked/disliked dishes
- **Individual History:** Recipe suggestions and ratings are stored per user
- **Personal Logs:** API calls are logged separately for each user
- **Easy Switching:** Select different users on each program start

## Example Session

```
🍳  Welcome to the AI Recipe Assistant!

👤  User Selection

Existing users:
1. alice
2. bob
3. Create new user

Select user (1-3): 1

✓ Logged in as: alice

What would you like to do?
1 - Get recipe suggestions for today
2 - Give feedback on a cooked dish
3 - View my preferences
4 - View API log

Your choice (1-4): 1

--- Available Ingredients ---
Please list all ingredients you have in your fridge.

Your ingredients: chicken breast, bell peppers, onions, rice, garlic

🤔 I'm thinking of suitable recipes for you...

[Claude suggests recipes]
```

## Expansion Possibilities

- 🌐 Web interface with Flask/FastAPI
- 📱 Mobile app
- 🗄️ Real database (PostgreSQL, MongoDB)
- 📸 Photo recognition for ingredients
- 🛒 Shopping list generator
- 📊 Statistics about cooked dishes
- 🌍 Multi-language support
- 🍽️ Meal planning for the week

## Costs

Using the Claude API is paid. One recipe suggestion costs approximately €0.001-0.003 (depending on the model). 
A few euros are sufficient for the prototype.

## License

This project is a prototype for learning purposes.
