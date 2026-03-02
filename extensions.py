from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

# SQLite database instance (for users/auth)
db = SQLAlchemy()

# Login session manager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# Password hashing
bcrypt = Bcrypt()

# CSRF protection
csrf = CSRFProtect()

# MongoDB client (for patient records)
def get_mongo_db():
    client = MongoClient(os.environ.get('MONGO_URI'))
    return client['patient_records']

# Tells Flask-Login how to reload a user from the session
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))