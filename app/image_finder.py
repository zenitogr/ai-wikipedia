import requests
import logging

# Create a logger for this module
logger = logging.getLogger(__name__)

def search_wikimedia_commons(query):
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": f"{query} filetype:bitmap|drawing|image|jpg|jpeg|png|gif|svg",
        "srnamespace": "6",  # File namespace
        "srlimit": "5",  # Increase the number of results
        "srprop": "snippet"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if 'query' in data and 'search' in data['query'] and data['query']['search']:
            for result in data['query']['search']:
                file_name = result['title']
                image_url = get_file_url(file_name)
                if image_url:
                    logger.debug(f"Found file: {file_name}")
                    return image_url
            logger.warning(f"No valid image found for query: {query}")
        else:
            logger.warning(f"No search results found for query: {query}")
    except requests.RequestException as e:
        logger.error(f"Error searching Wikimedia Commons: {str(e)}")
    return None

def get_file_url(file_name):
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "imageinfo",
        "iiprop": "url",
        "titles": file_name
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        pages = data['query']['pages']
        for page in pages.values():
            if 'imageinfo' in page:
                image_url = page['imageinfo'][0]['url']
                logger.debug(f"Found image URL: {image_url}")
                return image_url
        logger.warning(f"No image info found for file: {file_name}")
    except requests.RequestException as e:
        logger.error(f"Error getting file URL: {str(e)}")
    return None

def get_images_for_suggestions(image_suggestions):
    images = []
    if isinstance(image_suggestions, str):
        image_suggestions = [s.strip() for s in image_suggestions.split('*') if s.strip()]
    
    for suggestion in image_suggestions:
        logger.info(f"Searching for image: {suggestion}")
        image_url = search_wikimedia_commons(suggestion)
        if image_url:
            images.append({"description": suggestion, "url": image_url})
        else:
            # If no image found, try searching with a more general term
            general_term = suggestion.split(',')[0].strip()  # Take the first part of the suggestion
            logger.info(f"Trying general term: {general_term}")
            image_url = search_wikimedia_commons(general_term)
            if image_url:
                images.append({"description": suggestion, "url": image_url})
            else:
                logger.warning(f"No image found for suggestion: {suggestion}")
    
    logger.info(f"Total images found: {len(images)}")
    return images