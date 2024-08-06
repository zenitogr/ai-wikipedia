import requests

def get_image_url(query):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "pageimages",
        "piprop": "original",
        "titles": query,
        "pithumbsize": 300
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    pages = data['query']['pages']
    for page in pages.values():
        if 'original' in page:
            return page['original']['source']
    return None

def get_images_for_suggestions(image_suggestions):
    images = []
    for suggestion in image_suggestions:
        image_url = get_image_url(suggestion)
        if image_url:
            images.append({"description": suggestion, "url": image_url})
    return images