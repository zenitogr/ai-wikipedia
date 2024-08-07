from flask import render_template, request, jsonify, flash
from flask import current_app as app
from app.ai_generator import ai_generator
from app.image_finder import get_images_for_suggestions
import logging
import redis
import json
from config import Config

# Create a logger for this module
logger = logging.getLogger(__name__)

app.logger.debug('Routes module loaded')

# Set up Redis connection
redis_client = redis.Redis(
    host=Config.REDIS_URL,
    port=14501,
    password=Config.REDIS_PASSWORD,
    decode_responses=True
)

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
        similar_terms = ai_generator.get_similar_terms(topic)
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
    cache_key = f"article:{decoded_topic}"
    logger.info(f"Cache key: {cache_key} - decoded topic: {decoded_topic}")

    try:
        cached_result = redis_client.get(cache_key)
        if cached_result:
            return render_cached_article(cached_result, decoded_topic)

        return generate_and_cache_article(decoded_topic, cache_key)
    except Exception as e:
        logger.error(f'Error generating article or finding images: {str(e)}')
        flash('An unexpected error occurred. Please try again later.', 'error')
        return render_template('index.html', title='AI Wikipedia')

def render_cached_article(cached_result, decoded_topic):
    cached_data = json.loads(cached_result)
    logger.info(f"Returning cached article for topic: {decoded_topic}")
    return render_template('article.html', 
                           title=decoded_topic,
                           article=cached_data['article'],
                           images=cached_data['images'],
                           image_suggestions=cached_data['image_suggestions'])

def generate_and_cache_article(decoded_topic, cache_key):
    logger.info(f"Generating article for topic: {decoded_topic}")
    article, image_suggestions = ai_generator.generate_article(decoded_topic)
    logger.info(f"Article generated. Image suggestions: {image_suggestions}")

    images = get_images_for_suggestions(image_suggestions)
    logger.info(f"Images found: {images}")

    if not images:
        logger.warning(f"No images found for topic: {decoded_topic}")

    cache_data = {
        'article': article,
        'images': images,
        'image_suggestions': image_suggestions
    }
    redis_client.setex(cache_key, 3600, json.dumps(cache_data))  # Cache for 1 hour

    return render_template('article.html', 
                           title=decoded_topic,
                           article=article,
                           images=images,
                           image_suggestions=image_suggestions)