import requests
from config import Config

def get_image_url(query):
    url = f"https://api.unsplash.com/search/photos"
    params = {
        "query": query,
        "per_page": 1,
        "client_id": Config.UNSPLASH_ACCESS_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if data['results']:
        return data['results'][0]['urls']['small']
    return None

def get_images_for_suggestions(image_suggestions):
    images = []
    for suggestion in image_suggestions:
        image_url = get_image_url(suggestion)
        if image_url:
            images.append({"description": suggestion, "url": image_url})
    return images