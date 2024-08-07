import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    REDIS_URL = os.environ.get('REDIS_URL')
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
    CLEAR_CACHE_TOKEN = os.environ.get('CLEAR_CACHE_TOKEN')
    if not REDIS_URL or not REDIS_PASSWORD:
        raise ValueError("REDIS_URL and REDIS_PASSWORD must be set in environment variables")
    if not GROQ_API_KEY:
        raise ValueError("No GROQ_API_KEY set for Flask application")
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for Flask application")

    # Flask-SQLAlchemy settings (if you decide to use a database later)
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///ai_wikipedia.db'
    # SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Other configuration settings
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False