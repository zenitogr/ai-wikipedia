import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    
    if not GROQ_API_KEY:
        raise ValueError("No GROQ_API_KEY set for Flask application")
    
    # Flask-SQLAlchemy settings (if you decide to use a database later)
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///ai_wikipedia.db'
    # SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Other configuration settings
    DEBUG = True
    TESTING = False