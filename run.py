from dotenv import load_dotenv
load_dotenv()  # This line loads the variables from .env file

from app import create_app
from config import ProductionConfig
import logging
from flask import Flask
import markdown

app = create_app(config_class=ProductionConfig)

@app.template_filter('markdown')
def markdown_filter(text):
    return markdown.markdown(text)

if __name__ == '__main__':
    app.logger.debug('Starting the application')
    app.run(debug=False)