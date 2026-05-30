import requests
from config import Config

BASE_URL = 'https://api.themoviedb.org/3'

def get_headers():
    return {
        "accept": "application/json",
        "Authorization": f"Bearer {Config.TMDB_API_KEY}" # if using raw API key as Bearer, else append as ?api_key=...
    }
    
# Or append to params
def get_params(extra_params=None):
    params = {"api_key": Config.TMDB_API_KEY, "language": "en-US"}
    if extra_params:
        params.update(extra_params)
    return params

def search_movies(query):
    url = f"{BASE_URL}/search/movie"
    response = requests.get(url, params=get_params({"query": query}))
    if response.status_code == 200:
        return response.json().get('results', [])
    return []

def get_movie_details(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}"
    response = requests.get(url, params=get_params())
    if response.status_code == 200:
        return response.json()
    return None

def get_similar_movies(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/similar"
    response = requests.get(url, params=get_params())
    if response.status_code == 200:
        return response.json().get('results', [])
    return []

def get_trending_movies():
    url = f"{BASE_URL}/trending/movie/week"
    try:
        response = requests.get(url, params=get_params())
        if response.status_code == 200:
            return response.json().get('results', [])
    except Exception:
        pass
    return []

def get_popular_movies():
    url = f"{BASE_URL}/movie/popular"
    response = requests.get(url, params=get_params())
    if response.status_code == 200:
        return response.json().get('results', [])
    return []

def format_movie_poster(poster_path):
    if poster_path:
        return f"https://image.tmdb.org/t/p/w500{poster_path}"
    return "https://via.placeholder.com/500x750?text=No+Poster"
