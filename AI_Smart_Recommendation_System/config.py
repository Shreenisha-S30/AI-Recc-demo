import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-key-for-dev')
    TMDB_API_KEY = os.environ.get('TMDB_API_KEY', '')
    GOOGLE_BOOKS_API_KEY = os.environ.get('GOOGLE_BOOKS_API_KEY', '')
    DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'app.db')
