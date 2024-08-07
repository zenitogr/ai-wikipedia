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
        model="llama3-8b-8192",
        max_tokens=8192,
    )
    sections = [s.strip() for s in response.choices[0].message.content.split(',')]
    return sections

def generate_article(topic):
    sections = generate_sections(topic)
    prompt = f"""Write a Wikipedia article about {topic}. Here's the sections:

{', '.join(sections)}

Sections should be markdown headers.

Also, suggest around 10 relevant short image search queries (without actually generating images) that could accompany this article. Format the short image suggestions as a list at the end of the article, each prefixed with 'IMAGE:'.

Now, write the article:"""
    
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama3-70b-8192",
        max_tokens=8192,
    )
    article = response.choices[0].message.content
    
    # Split the article and image suggestions
    article_parts = article.split('IMAGE:')
    main_article = article_parts[0].strip()
    image_suggestions = [img.strip() for img in article_parts[1:]]
    
    logger.info(f"Generated article for topic: {topic}")
    logger.info(f"Image suggestions: {image_suggestions}")
    
    return main_article, image_suggestions


def generate_and_validate_article(topic):
    article, image_suggestions = generate_article(topic)
    return article, image_suggestions

def get_similar_terms(topic):
    prompt = f"Say nothing else, only respond with this template: input_title (category - subcategory), realtive_wiki_title_1 (category - subcategory), relative_wiki_title_2 (category - subcategory), relative_wiki_title_N (category - subcategory). relative_wiki_titles are 10 similar wiki titles to the input_title with their category and subcategory. remember dont say anything except the template list!!! the input_title is: {topic}"
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama3-8b-8192",
        temperature=0.5,
        max_tokens=8192,
    )

    response = chat_completion.choices[0].message.content
    similar_terms = [term.strip() for term in response.split(',')]
    return similar_terms