import os
from config import Config

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False