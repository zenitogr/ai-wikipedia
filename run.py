from dotenv import load_dotenv
load_dotenv()  # This line loads the variables from .env file

from app import create_app
import logging
from flask import Flask
import markdown

app = create_app()

@app.template_filter('markdown')
def markdown_filter(text):
    return markdown.markdown(text)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.logger.debug('Starting the application')
    app.run(debug=True)