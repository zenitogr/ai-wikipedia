from flask import render_template, request, jsonify, flash, redirect, url_for
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

@app.route('/cached_articles')
def cached_articles():
    try:
        keys = redis_client.keys('article:*')
        articles = []
        for key in keys:
            article = redis_client.get(key)
            if article:
                article_data = json.loads(article)
                if 'title' in article_data and 'content' in article_data:
                    article_data['id'] = key.split(':', 1)[1]  # Use the Redis key as the article ID
                    articles.append(article_data)
                else:
                    app.logger.error(f"Invalid article structure for key: {key}")
        return render_template('cached_articles.html', title='Cached Articles', articles=articles)
    except Exception as e:
        app.logger.error(f'Error fetching cached articles: {str(e)}')
        flash('An unexpected error occurred. Please try again later.', 'error')
        return redirect(url_for('index'))

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

@app.route('/article/<article_id>')
def view_article(article_id):
    try:
        article = redis_client.get(f'article:{article_id}')
        if article:
            article = json.loads(article)
            return render_template('article.html', title=article['title'], content=article['content'], images=article['images'], image_suggestions=article['image_suggestions'])
        else:
            flash('Article not found.', 'error')
            return redirect(url_for('cached_articles'))
    except Exception as e:
        app.logger.error(f'Error fetching article: {str(e)}')
        flash('An unexpected error occurred. Please try again later.', 'error')
        return redirect(url_for('cached_articles'))

def render_cached_article(cached_result, decoded_topic):
    cached_data = json.loads(cached_result)
    logger.info(f"Returning cached article for topic: {decoded_topic}")
    return render_template('article.html', 
                           title=decoded_topic,
                           content=cached_data['content'],
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
        'title': decoded_topic,
        'content': article,  # Ensure 'content' is included
        'images': images,
        'image_suggestions': image_suggestions
    }
    redis_client.set(cache_key, json.dumps(cache_data))  # No expiration time set

    return render_template('article.html', 
                           title=decoded_topic,
                           content=article,
                           images=images,
                           image_suggestions=image_suggestions)

@app.route('/clear_cache', methods=['POST'])
def clear_cache():
    token = request.headers.get('Authorization')
    if token != app.config['CLEAR_CACHE_TOKEN']:
        app.logger.warning('Unauthorized attempt to clear cache.')
        return 'Unauthorized.', 401

    try:
        redis_client.flushdb()
        app.logger.info('Redis cache cleared successfully.')
        return 'Cache cleared successfully.', 200
    except Exception as e:
        app.logger.error(f'Error clearing cache: {str(e)}')
        return 'Error clearing cache.', 500