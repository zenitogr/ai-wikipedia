from flask import Flask
from config import DevelopmentConfig, ProductionConfig
from app.logging_config import configure_logging

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure logging
    configure_logging()
    
    with app.app_context():
        from app import routes
    
    app.logger.debug('App created and routes registered')
    return app