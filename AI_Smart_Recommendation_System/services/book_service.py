import requests

BASE_URL = 'https://openlibrary.org'

def get_params(extra_params=None):
    return extra_params or {}

def search_books(query):
    url = f"{BASE_URL}/search.json"
    response = requests.get(url, params={"q": query, "limit": 10})
    if response.status_code == 200:
        docs = response.json().get('docs', [])
        formatted = []
        for d in docs:
            formatted.append({
                'id': d.get('key', '').replace('/works/', ''),
                'volumeInfo': {
                    'title': d.get('title'),
                    'authors': d.get('author_name', []),
                    'description': ', '.join(d.get('subject', [])[:5]) if d.get('subject') else '',
                    'imageLinks': {
                        'thumbnail': f"https://covers.openlibrary.org/b/id/{d.get('cover_i')}-M.jpg" if d.get('cover_i') else None
                    }
                }
            })
        return formatted
    return []

def get_book_details(book_id):
    url = f"{BASE_URL}/works/{book_id}.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def get_similar_books(title, author=""):
    url = f"{BASE_URL}/search.json"
    q = title
    if author:
        q = author
    
    response = requests.get(url, params={"q": q, "limit": 10})
    if response.status_code == 200:
        docs = response.json().get('docs', [])
        formatted = []
        for d in docs:
            formatted.append({
                'id': d.get('key', '').replace('/works/', ''),
                'volumeInfo': {
                    'title': d.get('title'),
                    'authors': d.get('author_name', []),
                    'description': ', '.join(d.get('subject', [])[:5]) if d.get('subject') else '',
                    'imageLinks': {
                        'thumbnail': f"https://covers.openlibrary.org/b/id/{d.get('cover_i')}-M.jpg" if d.get('cover_i') else None
                    }
                }
            })
        return formatted
    return []

def format_book_cover(image_links):
    if image_links and 'thumbnail' in image_links and image_links['thumbnail']:
        return image_links['thumbnail'].replace("http:", "https:")
    return "https://via.placeholder.com/300x450?text=No+Cover"
