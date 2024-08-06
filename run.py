from dotenv import load_dotenv
load_dotenv()  # This line loads the variables from .env file

from app import create_app
import markdown

app = create_app()

@app.template_filter('markdown')
def markdown_filter(text):
    return markdown.markdown(text)