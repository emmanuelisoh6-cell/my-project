import os
import json
import hashlib

USER_DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")

def load_user_database():
    """Loads existing users from the JSON file."""
    if not os.path.exists(USER_DB_FILE):
        return {}
    with open(USER_DB_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_user_database(data):
    """Saves the user database back to the JSON file."""
    with open(USER_DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def hash_password(password):
    """Hashes passwords using SHA-256 for secure storage."""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    """Registers a new user if the username is unique."""
    db = load_user_database()
    username_clean = username.strip().lower()
    
    if username_clean in db:
        return False, "⚠️ Username already exists!"
    
    db[username_clean] = {
        "password": hash_password(password),
        "display_name": username.strip()
    }
    save_user_database(db)
    return True, "✅ Registration successful! You can now login."

def check_login(username, password):
    """Verifies credentials against the hashed database values."""
    db = load_user_database()
    username_clean = username.strip().lower()
    
    if username_clean not in db:
        return False
        
    return db[username_clean]["password"] == hash_password(password)