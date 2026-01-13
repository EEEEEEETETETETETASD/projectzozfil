import bcrypt
from db import create_user, get_user
from config import OWNER_USERNAME, OWNER_PASSWORD

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def signup(username, password):
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    if get_user(username):
        return False, "Username already exists"
    hashed = hash_password(password)
    create_user(username, hashed)
    return True, "Account created"

def login(username, password):
    if username == OWNER_USERNAME and password == OWNER_PASSWORD:
        return True, {'id': 0, 'username': OWNER_USERNAME, 'currency': 0}  # Special owner user
    user = get_user(username)
    if not user:
        return False, "User not found"
    if check_password(password, user['password_hash']):
        return True, user
    return False, "Invalid password"