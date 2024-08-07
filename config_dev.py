import os
from config import Config

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False