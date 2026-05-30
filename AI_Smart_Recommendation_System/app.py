from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from dotenv import load_dotenv
import os
from config import Config
from database.db import init_db, create_user, get_user_by_username, get_user_by_id, log_search, add_favorite, get_user_favorites, bcrypt, add_rating, get_user_ratings
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from services.movie_service import search_movies, get_similar_movies, get_trending_movies, format_movie_poster
from services.book_service import search_books, get_similar_books, format_book_cover
from services.food_service import search_meals, recommend_related_meals
from services.recommendation_engine import rerank_recommendations

app = Flask(__name__)
app.config.from_object(Config)
load_dotenv()
app.config['TMDB_API_KEY'] = os.getenv('TMDB_API_KEY', app.config.get('TMDB_API_KEY', ''))

# Init Database and Auth Plugins
init_db()
bcrypt.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # type: ignore

@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)

# ================= AUTH ROUTES ================= 

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = get_user_by_username(username)
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if create_user(username, email, password):
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username or Email already exists.', 'danger')
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    favorites = get_user_favorites(current_user.id)
    return render_template('profile.html', favorites=favorites)

# ================= MAIN PAGE ROUTES ================= 

@app.route('/')
def index():
    # Show some TMDB trending movies by default
    trending = get_trending_movies()[:5]
    return render_template('index.html', trending=trending)

@app.route('/movies')
def movies():
    popular = get_trending_movies()[:10]
    return render_template('movies.html', popular=popular)

@app.route('/books')
def books():
    return render_template('books.html')

@app.route('/food')
def food():
    return render_template('food.html')

# ================= API ENDPOINTS FOR SEARCH / RECOMMEND ================= 

@app.route('/api/movie/search', methods=['POST'])
def api_movie_search():
    query = request.form.get('query')
    if current_user.is_authenticated:
        log_search(current_user.id, query, 'movie')
    
    results = search_movies(query)
    formatted_results = []
    for r in results:
        formatted_results.append({
            'id': r.get('id'),
            'title': r.get('title'),
            'poster': format_movie_poster(r.get('poster_path')),
            'overview': r.get('overview')
        })
    return jsonify(formatted_results)

@app.route('/recommend/movie', methods=['POST'])
def recommend_movie():
    movie_id = request.form.get('movie_id')
    raw_similar = get_similar_movies(movie_id)
    
    user_id = current_user.id if current_user.is_authenticated else None
    ranked = rerank_recommendations(user_id, raw_similar, 'movie')
    
    # Format response
    response_data = []
    for r in ranked:
        m = r['item']
        response_data.append({
            'title': m.get('title'),
            'poster_path': format_movie_poster(m.get('poster_path')),
            'overview': m.get('overview'),
            'match_score': r['match_score'],
            'id': m.get('id')
        })
    return jsonify(response_data)

@app.route('/api/book/search', methods=['POST'])
def api_book_search():
    query = request.form.get('query')
    if current_user.is_authenticated:
        log_search(current_user.id, query, 'book')
        
    results = search_books(query)
    formatted = []
    for r in results:
        vol = r.get('volumeInfo', {})
        formatted.append({
            'id': r.get('id'),
            'title': vol.get('title'),
            'author': ', '.join(vol.get('authors', [])),
            'cover': format_book_cover(vol.get('imageLinks')),
            'description': vol.get('description', '')
        })
    return jsonify(formatted)

@app.route('/recommend/book', methods=['POST'])
def recommend_book():
    title = request.form.get('title')
    author = request.form.get('author', '')
    
    raw_similar = get_similar_books(title, author)
    user_id = current_user.id if current_user.is_authenticated else None
    
    ranked = rerank_recommendations(user_id, raw_similar, 'book')
    
    # Format response
    response_data = []
    for r in ranked:
        b = r['item'].get('volumeInfo', {})
        response_data.append({
            'title': b.get('title'),
            'author': ', '.join(b.get('authors', [])),
            'cover': format_book_cover(b.get('imageLinks')),
            'description': b.get('description', ''),
            'match_score': r['match_score'],
            'id': r['item'].get('id')
        })
    return jsonify(response_data)

@app.route('/api/food/search', methods=['POST'])
def api_food_search():
    query = request.form.get('query')
    if current_user.is_authenticated:
        log_search(current_user.id, query, 'food')
    
    results = search_meals(query)
    # simplified mapping
    formatted = []
    for r in results:
        formatted.append({
            'id': r.get('idMeal'),
            'name': r.get('strMeal'),
            'category': r.get('strCategory'),
            'thumb': r.get('strMealThumb')
        })
    return jsonify(formatted)

@app.route('/recommend/food', methods=['POST'])
def recommend_food():
    category = request.form.get('category')
    raw_similar = recommend_related_meals(category)
    user_id = current_user.id if current_user.is_authenticated else None
    ranked = rerank_recommendations(user_id, raw_similar, 'food')
    
    response_data = []
    for r in ranked:
        f_item = r['item']
        response_data.append({
            'name': f_item.get('strMeal'),
            'thumb': f_item.get('strMealThumb'),
            'category': category,
            'match_score': r['match_score'],
            'id': f_item.get('idMeal')
        })
    return jsonify(response_data)


@app.route('/api/favorite', methods=['POST'])
@login_required
def api_favorite():
    data = request.json
    success = add_favorite(
        user_id=current_user.id,
        item_id=str(data.get('item_id')),
        item_type=data.get('item_type'),
        title=data.get('title'),
        image_url=data.get('image_url')
    )
    if success:
        return jsonify({'message': 'Added to favorites!'})
    return jsonify({'message': 'Already in favorites!'})

@app.route('/api/rate', methods=['POST'])
@login_required
def api_rate():
    data = request.json
    add_rating(
        user_id=current_user.id,
        item_id=str(data.get('item_id')),
        item_type=data.get('item_type'),
        rating=int(data.get('rating'))
    )
    return jsonify({'message': 'Rating saved!'})


if __name__ == '__main__':
    app.run(debug=True)