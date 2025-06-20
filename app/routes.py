from flask import render_template, request, jsonify, flash, redirect, url_for, g
from flask import current_app as app
from app.ai_generator import ai_generator
from app.image_finder import get_images_for_suggestions
import logging
import json
import sqlite3
from config import Config

# Create a logger for this module
logger = logging.getLogger(__name__)

app.logger.debug('Routes module loaded')

DATABASE = 'articles.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # This allows accessing columns by name
    return db

@app.teardown_appcontext
def close_db(error):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# This will be called when the app starts
with app.app_context():
    init_db()

@app.route('/')
def index():
    app.logger.debug('Index route accessed')
    return render_template('index.html', title='AI Wiki')

@app.route('/about')
def about():
    app.logger.debug('About route accessed')
    return render_template('about.html', title='About AI Wiki')
@app.route('/search', methods=['POST'])
def search():
    topic = request.form.get('topic')
    if not topic:
        flash('Please enter a topic.', 'error')
        return render_template('index.html', title='AI Wiki')

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
        db = get_db()
        articles_cursor = db.execute('SELECT id, title, content, images, image_suggestions FROM articles').fetchall()
        articles = []
        for article_row in articles_cursor:
            article_data = dict(article_row)
            # Deserialize JSON strings back to Python objects
            article_data['images'] = json.loads(article_data['images']) if article_data['images'] else []
            article_data['image_suggestions'] = json.loads(article_data['image_suggestions']) if article_data['image_suggestions'] else []
            articles.append(article_data)
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
        db = get_db()
        cached_article = db.execute('SELECT content, images, image_suggestions FROM articles WHERE id = ?', (decoded_topic,)).fetchone()

        if cached_article:
            return render_cached_article(json.dumps(dict(cached_article)), decoded_topic)

        return generate_and_cache_article(decoded_topic)
    except Exception as e:
        logger.error(f'Error generating article or finding images: {str(e)}')
        flash('An unexpected error occurred. Please try again later.', 'error')
        return render_template('index.html', title='AI Wikipedia')

@app.route('/article/<article_id>')
def view_article(article_id):
    try:
        db = get_db()
        article_row = db.execute('SELECT title, content, images, image_suggestions FROM articles WHERE id = ?', (article_id,)).fetchone()

        if article_row:
            article = dict(article_row)
            article['images'] = json.loads(article['images']) if article['images'] else []
            article['image_suggestions'] = json.loads(article['image_suggestions']) if article['image_suggestions'] else []
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

def generate_and_cache_article(decoded_topic):
    logger.info(f"Generating article for topic: {decoded_topic}")
    article_content, image_suggestions = ai_generator.generate_article(decoded_topic)
    logger.info(f"Article generated. Image suggestions: {image_suggestions}")

    images = get_images_for_suggestions(image_suggestions)
    logger.info(f"Images found: {images}")

    if not images:
        logger.warning(f"No images found for topic: {decoded_topic}")

    db = get_db()
    db.execute('INSERT INTO articles (id, title, content, images, image_suggestions) VALUES (?, ?, ?, ?, ?)',
               (decoded_topic, decoded_topic, article_content, json.dumps(images), json.dumps(image_suggestions)))
    db.commit()

    return render_template('article.html',
                           title=decoded_topic,
                           content=article_content,
                           images=images,
                           image_suggestions=image_suggestions)

@app.route('/clear_cache', methods=['POST'])
def clear_cache():
    token = request.headers.get('Authorization')
    if token != app.config['CLEAR_CACHE_TOKEN']:
        app.logger.warning('Unauthorized attempt to clear cache.')
        return 'Unauthorized.', 401

    try:
        db = get_db()
        db.execute('DELETE FROM articles')
        db.commit()
        app.logger.info('SQLite cache cleared successfully.')
        return 'Cache cleared successfully.', 200
    except Exception as e:
        app.logger.error(f'Error clearing cache: {str(e)}')
        return 'Error clearing cache.', 500