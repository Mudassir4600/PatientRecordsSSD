from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pymongo import MongoClient
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

load_dotenv()

# SQLite database instance for users/auth
db = SQLAlchemy()

# for managing login sessions
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# Password hashing using bcrypt
bcrypt = Bcrypt()

# CSRF protection on all forms
csrf = CSRFProtect()

# Limits number of attempts to prevent brute force attacks
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[]
)

# MongoDB client (for patient records)
def get_mongo_db():
    client = MongoClient(os.environ.get('MONGO_URI'))
    return client['patient_records']


# Encryption helper for sensitive patient fields (STRIDE: Information Disclosure)
def get_encryption_key():
    key = os.environ.get('ENCRYPTION_KEY')
    if not key:
        raise ValueError("ENCRYPTION_KEY not set in .env")
    return key.encode()


def encrypt_field(value: str) -> str:
    """Encrypt a sensitive string field before storing in database."""
    if not value:
        return value
    f = Fernet(get_encryption_key())
    return f.encrypt(value.encode()).decode()


def decrypt_field(value: str) -> str:
    """Decrypt a sensitive string field when retrieving from database."""
    if not value:
        return value
    try:
        f = Fernet(get_encryption_key())
        return f.decrypt(value.encode()).decode()
    except Exception:
        return value


# Tells Flask Login how to reload a user from the session
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))