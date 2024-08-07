import requests
import logging

# Create a logger for this module
logger = logging.getLogger(__name__)

class ImageFinder:
    def __init__(self):
        self.base_url = "https://commons.wikimedia.org/w/api.php"

    def search_images(self, query):
        params = self._create_search_params(query)
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            return self._process_search_results(data, query)
        except requests.RequestException as e:
            self._handle_request_error(e, "searching Wikimedia Commons")
            return None

    def get_file_url(self, file_name):
        params = self._create_file_url_params(file_name)
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            return self._extract_image_url(data['query']['pages'], file_name)
        except requests.RequestException as e:
            self._handle_request_error(e, "getting file URL")
            return None

    def _create_search_params(self, query):
        return {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": f"{query} filetype:bitmap|drawing|image|jpg|jpeg|png|gif|svg",
            "srnamespace": "6",  # File namespace
            "srlimit": "5",  # Increase the number of results
            "srprop": "snippet"
        }

    def _create_file_url_params(self, file_name):
        return {
            "action": "query",
            "format": "json",
            "prop": "imageinfo",
            "iiprop": "url",
            "titles": file_name
        }

    def _process_search_results(self, data, query):
        if 'query' not in data or 'search' not in data['query'] or not data['query']['search']:
            logger.warning(f"No search results found for query: {query}")
            return "noimage", "noimage"
        return self._find_valid_image(data['query']['search'])

    def _find_valid_image(self, search_results):
        for result in search_results:
            file_name = result['title']
            image_url = self.get_file_url(file_name)
            if image_url:
                logger.debug(f"Found file: {file_name}")
                return image_url, file_name
        logger.warning(f"No valid image found")
        return "noimage", "noimage"

    def _extract_image_url(self, pages, file_name):
        for page in pages.values():
            if 'imageinfo' in page:
                image_url = page['imageinfo'][0]['url']
                logger.debug(f"Found image URL: {image_url}")
                return image_url
        logger.warning(f"No image info found for file: {file_name}")
        return None

    def _handle_request_error(self, e, context):
        logger.error(f"Error {context}: {str(e)}")

# Initialize the Image Finder
image_finder = ImageFinder()

def get_images_for_suggestions(image_suggestions):
    images = []
    if isinstance(image_suggestions, str):
        image_suggestions = [s.strip() for s in image_suggestions.split('\n') if s.strip()]

    for suggestion in image_suggestions:
        logger.info(f"Searching for image: {suggestion}")
        image_url, file_name = image_finder.search_images(suggestion)
        if image_url != "noimage":
            images.append({"description": suggestion, "url": image_url, "file_name": file_name})
            continue

        general_term = suggestion.split(',')[0].strip()  # Take the first part of the suggestion
        logger.info(f"Trying general term: {general_term}")
        image_url, file_name = image_finder.search_images(general_term)
        if image_url != "noimage":
            images.append({"description": suggestion, "url": image_url, "file_name": file_name})
        else:
            logger.warning(f"No image found for suggestion: {suggestion}")

    logger.info(f"Total images found: {len(images)}")
    return images