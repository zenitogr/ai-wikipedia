from groq import Groq
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from config import Config
import time
import logging

# Create a logger for this module
logger = logging.getLogger(__name__)

client = Groq(api_key=Config.GROQ_API_KEY)

def generate_sections(topic):
    prompt = f"Generate a list of 4-6 relevant section titles for a Wikipedia article about {topic}. Return only the section titles, separated by commas."
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama-3.1-8b-instant",
        max_tokens=8000,
    )
    sections = [s.strip() for s in response.choices[0].message.content.split(',')]
    return sections

def generate_article(topic):
    sections = generate_sections(topic)
    prompt = f"""Write a Wikipedia article about {topic}. Here's the sections:

{', '.join(sections)}

Sections should be markdown headers.

Also, suggest 3 relevant image descriptions (without actually generating images) that could accompany this article. Format the image suggestions as a list at the end of the article, each prefixed with 'IMAGE:'.

Now, write the article:"""
    
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama-3.1-70b-versatile",
        max_tokens=8000,
    )
    article = response.choices[0].message.content
    
    # Split the article and image suggestions
    article_parts = article.split('IMAGE:')
    main_article = article_parts[0].strip()
    image_suggestions = [img.strip() for img in article_parts[1:]]
    
    logger.info(f"Generated article for topic: {topic}")
    logger.info(f"Image suggestions: {image_suggestions}")
    
    return main_article, image_suggestions

def fact_check(topic, generated_text):
    # This is a simple fact-checking mechanism using Wikipedia API
    url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&exintro=1&explaintext=1&titles={topic}"
    response = requests.get(url)
    data = response.json()
    page = next(iter(data['query']['pages'].values()))
    if 'extract' in page:
        wikipedia_intro = page['extract']
        # Compare the first sentence of generated text with Wikipedia intro
        if generated_text.split('.')[0].lower() in wikipedia_intro.lower():
            return True
    return False

def generate_citation(topic):
    url = f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.find('h1', {'id': 'firstHeading'}).text
    return f"{title}. Wikipedia. Retrieved on {datetime.now().strftime('%Y-%m-%d')} from {url}"

def generate_and_validate_article(topic):
    article, image_suggestions = generate_article(topic)
    return article, image_suggestions

def get_similar_terms(topic):
    prompt = f"say nothing else but a list of comma-separated 10 similar wiki terms or related wiki topics from the term: {topic}.include the category and subcategory of the topic in parentheses. generate a category and subcatory for the input topic also.###response-format-start### OrigitalTopic (category - subcategory), topic2 (category - subcategory), topic3 (category - subcategory), topicN (category - subcategory)###response-format-end###"
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama-3.1-8b-instant",
        temperature=0.5,
        max_tokens=8000,
    )

    response = chat_completion.choices[0].message.content
    similar_terms = [term.strip() for term in response.split(',')]
    return similar_terms