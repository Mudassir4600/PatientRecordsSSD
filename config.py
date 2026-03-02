import os
from dotenv import load_dotenv

#loading environment variables
load_dotenv()

class Config:
    #session signing and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret-key')

    # MongoDB URI for patient records database
    MONGO_URI = os.environ.get('MONGO_URI')

    # SQLite database path for authentication/user data
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        os.environ.get('SQLITE_DB', 'instance/auth.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session cookie security settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    #enabling CSRF protection 
    WTF_CSRF_ENABLED = True