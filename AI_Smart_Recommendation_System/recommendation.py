import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

movies_path = os.path.join(BASE_DIR, 'datasets', 'movies.csv')
books_path = os.path.join(BASE_DIR, 'datasets', 'books.csv')
food_path = os.path.join(BASE_DIR, 'datasets', 'food.csv')

movies_df = pd.read_csv(movies_path)
books_df = pd.read_csv(books_path)
food_df = pd.read_csv(food_path)

# Prepare models
# Movies
movies_df['combined_features'] = movies_df['genre'] + " " + movies_df['keywords'] + " " + movies_df['overview']
movies_df['combined_features'] = movies_df['combined_features'].fillna('')
cv_movies = CountVectorizer()
movie_matrix = cv_movies.fit_transform(movies_df['combined_features'])
cosine_sim_movies = cosine_similarity(movie_matrix)

# Books
books_df['combined_features'] = books_df['genre'] + " " + books_df['author'] + " " + books_df['description']
books_df['combined_features'] = books_df['combined_features'].fillna('')
tfidf_books = TfidfVectorizer(stop_words='english')
book_matrix = tfidf_books.fit_transform(books_df['combined_features'])
cosine_sim_books = cosine_similarity(book_matrix)

def get_movie_recommendations(title, limit=5):
    try:
        idx = movies_df[movies_df['title'].str.lower() == title.lower()].index[0]
        sim_scores = list(enumerate(cosine_sim_movies[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:limit+1]
        movie_indices = [i[0] for i in sim_scores]
        return movies_df.iloc[movie_indices].to_dict('records')
    except IndexError:
        return []

def get_book_recommendations(title, limit=5):
    try:
        idx = books_df[books_df['title'].str.lower() == title.lower()].index[0]
        sim_scores = list(enumerate(cosine_sim_books[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:limit+1]
        book_indices = [i[0] for i in sim_scores]
        return books_df.iloc[book_indices].to_dict('records')
    except IndexError:
        return []

def get_food_recommendations(cuisine, is_veg, spice_level, meal_type, limit=5):
    filtered = food_df[
        (food_df['cuisine'].str.lower() == cuisine.lower()) &
        (food_df['is_veg'] == int(is_veg)) &
        (food_df['spice_level'].str.lower() == spice_level.lower()) &
        (food_df['meal_type'].str.lower() == meal_type.lower())
    ]
    if filtered.empty:
        filtered = food_df[(food_df['cuisine'].str.lower() == cuisine.lower()) | (food_df['is_veg'] == int(is_veg))]
    
    return filtered.head(limit).to_dict('records')

def get_all_movies():
    return movies_df['title'].tolist()

def get_all_books():
    return books_df['title'].tolist()