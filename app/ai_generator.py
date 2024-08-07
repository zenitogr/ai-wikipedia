from groq import Groq
from config import Config
import logging

# Create a logger for this module
logger = logging.getLogger(__name__)

class AIGenerator:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)

    def generate_article(self, topic):
        prompt = self._create_article_prompt(topic)
        response = self._get_groq_response(prompt, model="llama3-70b-8192")
        return self._parse_article_response(response, topic)

    def get_similar_terms(self, topic):
        prompt = self._create_similar_terms_prompt(topic)
        response = self._get_groq_response(prompt, model="llama3-8b-8192", temperature=0.5)
        return self._parse_similar_terms_response(response)

    def _create_article_prompt(self, topic):
        return f"""
        Generate a Wikipedia article about {topic}. Include 4-6 relevant section titles.
        Sections should be markdown headers.
        Also, suggest around 10 relevant short image search queries (without actually generating images) that could accompany this article. 
        Format the short image suggestions as a list at the end of the article, each prefixed with 'IMAGE:'.
        Now, write the article:
        """

    def _create_similar_terms_prompt(self, topic):
        return f"Say nothing else, only respond with this template: input_title (category - subcategory), realtive_wiki_title_1 (category - subcategory), relative_wiki_title_2 (category - subcategory), relative_wiki_title_N (category - subcategory). relative_wiki_titles are 10 similar wiki titles to the input_title with their category and subcategory. remember dont say anything except the template list!!! the input_title is: {topic}"

    def _get_groq_response(self, prompt, model, temperature=1.0):
        return self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            max_tokens=8192,
            temperature=temperature
        )

    def _parse_article_response(self, response, topic):
        article = response.choices[0].message.content
        article_parts = article.split('IMAGE:')
        main_article = article_parts[0].strip()
        image_suggestions = [img.strip() for img in article_parts[1:]]
        logger.info(f"Generated article for topic: {topic}")
        logger.info(f"Image suggestions: {image_suggestions}")
        return main_article, image_suggestions

    def _parse_similar_terms_response(self, response):
        return [term.strip() for term in response.choices[0].message.content.split(',')]

# Initialize the AI generator
ai_generator = AIGenerator(api_key=Config.GROQ_API_KEY)