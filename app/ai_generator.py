from groq import Groq
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from config import Config
import time

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
        model="mixtral-8x7b-32768",
        max_tokens=100,
    )
    sections = [s.strip() for s in response.choices[0].message.content.split(',')]
    return sections

def generate_article(topic):
    sections = generate_sections(topic)
    article = ""
    prompt = f"Write a Wikipedia article about {topic}. Here's the sections:\n\n{', '.join(sections)}\n\nSections should be markdown headers.\n\nNow, write the article:"
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="mixtral-8x7b-32768",
        max_tokens=32768,
    )
    article = response.choices[0].message.content
        
         
    return article

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
    article = generate_article(topic)
    #is_valid = fact_check(topic, article['Introduction'])
    #citation = generate_citation(topic)
    return article

def get_similar_terms(topic):
    prompt = f"Generate a list of 5-10 similar wiki terms or related wiki topics for '{topic}'.include the category and subcategory of the topic in parentheses. Return the result as a comma-separated list. example response: topic (category - subcategory), topic (category - subcategory), topic (category - subcategory)"
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="mixtral-8x7b-32768",
        temperature=0.5,
        max_tokens=32768,
    )

    response = chat_completion.choices[0].message.content
    similar_terms = [term.strip() for term in response.split(',')]
    return similar_terms