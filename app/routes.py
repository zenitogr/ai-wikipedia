from flask import render_template, request, jsonify, flash
from flask import current_app as app
from app.ai_generator import generate_and_validate_article, get_similar_terms
import requests
from app.image_finder import get_images_for_suggestions
import logging

# Create a logger for this module
logger = logging.getLogger(__name__)

app.logger.debug('Routes module loaded')

@app.route('/')
def index():
    app.logger.debug('Index route accessed')
    return render_template('index.html', title='AI Wikipedia')

@app.route('/search', methods=['POST'])
def search():
    topic = request.form.get('topic')
    if not topic:
        flash('Please enter a topic.', 'error')
        return render_template('index.html', title='AI Wikipedia')

    try:
        similar_terms = get_similar_terms(topic)
        return render_template('search_results.html', 
                               title=f'Search Results for "{topic}"',
                               topic=topic,
                               similar_terms=similar_terms)
    except Exception as e:
        app.logger.error(f'Error searching for similar terms: {str(e)}')
        flash('An unexpected error occurred. Please try again later.', 'error')
        return render_template('index.html', title='AI Wikipedia')

@app.route('/generate/<topic>', methods=['GET'])
def generate(topic):
    decoded_topic = topic.replace('%20', ' ')
    try:
        logger.info(f"Generating article for topic: {decoded_topic}")
        article, image_suggestions = generate_and_validate_article(decoded_topic)
        logger.info(f"Article generated. Image suggestions: {image_suggestions}")
        
        images = get_images_for_suggestions(image_suggestions)
        logger.info(f"Images found: {images}")
        
        if not images:
            logger.warning(f"No images found for topic: {decoded_topic}")
    except Exception as e:
        logger.error(f'Error generating article or finding images: {str(e)}')
        flash('An unexpected error occurred. Please try again later.', 'error')
        return render_template('index.html', title='AI Wikipedia')
    
    return render_template('article.html', 
                           title=decoded_topic,
                           article=article,
                           images=images,
                           image_suggestions=image_suggestions)