from flask import render_template, request, jsonify, flash
from flask import current_app as app
from app.ai_generator import generate_and_validate_article, get_similar_terms
import requests

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
        article = generate_and_validate_article(decoded_topic)

    except requests.RequestException:
        flash('An error occurred while generating the article. Please try again later.', 'error')
        return render_template('index.html', title='AI Wikipedia')
    except Exception as e:
        app.logger.error(f'Error generating article: {str(e)}')
        flash('An unexpected error occurred. Please try again later.', 'error')
        return render_template('index.html', title='AI Wikipedia')
    
    return render_template('article.html', 
                           title=topic,
                           article=article)