from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    with app.app_context():
        from app import routes
    
    app.logger.debug('App created and routes registered')
    return app