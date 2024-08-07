# AI-Generated Wikipedia

## Overview
AI-Generated Wikipedia is a Flask web application that generates Wikipedia-style articles based on user-provided topics. The application utilizes the Groq API for generating content and Wikimedia Commons for fetching related images.

## Features
- Generate Wikipedia articles with relevant section titles.
- Fetch related images from Wikimedia Commons.
- Caching of generated articles for improved performance.
- User-friendly interface for searching topics.

## Technologies Used
- **Flask**: A lightweight WSGI web application framework.
- **Requests**: For making HTTP requests to external APIs.
- **BeautifulSoup**: For parsing HTML and XML documents.
- **Groq**: For generating article content using AI.
- **Redis**: For caching generated articles.
- **Markdown**: For formatting the generated articles.

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-generated-wikipedia.git
   cd ai-generated-wikipedia
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  
   # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables in a `.env` file:
   ```
   SECRET_KEY=your_secret_key
   GROQ_API_KEY=your_groq_api_key
   REDIS_URL=your_redis_url
   REDIS_PASSWORD=your_redis_password
   ```

5. Run the application:
   ```bash
   python run.py
   ```

6. Open your browser and go to `http://127.0.0.1:5000`.

## Usage
- Enter a topic in the search bar to generate a related Wikipedia article.
- Click on the generated terms to view the articles and related images.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
- [Flask](https://flask.palletsprojects.com/)
- [Requests](https://docs.python-requests.org/en/master/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [Groq](https://groq.com/)
- [Wikimedia Commons](https://commons.wikimedia.org/)