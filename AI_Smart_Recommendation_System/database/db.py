import sqlite3
from config import Config
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

class User(UserMixin):
    def __init__(self, id, username, email, password=None):
        self.id = id
        self.username = username
        self.email = email
        self.password = password

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Create Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Favorites
    c.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_id TEXT,
            item_type TEXT,
            title TEXT,
            image_url TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Ratings
    c.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_id TEXT,
            item_type TEXT,
            rating INTEGER CHECK(rating >= 1 AND rating <= 5),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Search history
    c.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            query TEXT,
            category TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Recommendation history
    c.execute('''
        CREATE TABLE IF NOT EXISTS recommendation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_id TEXT,
            item_type TEXT,
            confidence_score REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()

def create_user(username, email, password):
    conn = get_db_connection()
    c = conn.cursor()
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    try:
        c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                  (username, email, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        return False # Username or email exists
    finally:
        conn.close()
    return True

def get_user_by_id(user_id):
    conn = get_db_connection()
    user_row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if user_row:
        return User(id=user_row['id'], username=user_row['username'], email=user_row['email'])
    return None

def get_user_by_username(username):
    conn = get_db_connection()
    user_row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    if user_row:
        user = User(id=user_row['id'], username=user_row['username'], email=user_row['email'])
        user.password = user_row['password']
        return user
    return None

def add_favorite(user_id, item_id, item_type, title, image_url):
    conn = get_db_connection()
    c = conn.cursor()
    # verify if already favorite
    existing = c.execute("SELECT * FROM favorites WHERE user_id = ? AND item_id = ? AND item_type = ?", (user_id, item_id, item_type)).fetchone()
    if existing:
        conn.close()
        return False
    c.execute("INSERT INTO favorites (user_id, item_id, item_type, title, image_url) VALUES (?, ?, ?, ?, ?)",
              (user_id, item_id, item_type, title, image_url))
    conn.commit()
    conn.close()
    return True

def add_rating(user_id, item_id, item_type, rating):
    conn = get_db_connection()
    c = conn.cursor()
    # update if exists
    existing = c.execute("SELECT * FROM ratings WHERE user_id = ? AND item_id = ? AND item_type = ?", (user_id, item_id, item_type)).fetchone()
    if existing:
        c.execute("UPDATE ratings SET rating = ? WHERE user_id = ? AND item_id = ? AND item_type = ?", (rating, user_id, item_id, item_type))
    else:
        c.execute("INSERT INTO ratings (user_id, item_id, item_type, rating) VALUES (?, ?, ?, ?)",
                  (user_id, item_id, item_type, rating))
    conn.commit()
    conn.close()

def get_user_ratings(user_id):
    conn = get_db_connection()
    ratings = conn.execute("SELECT * FROM ratings WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in ratings]

def get_user_favorites(user_id):
    conn = get_db_connection()
    favs = conn.execute("SELECT * FROM favorites WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    return [dict(f) for f in favs]

def log_search(user_id, query, category):
    if not user_id:
        return
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO search_history (user_id, query, category) VALUES (?, ?, ?)",
              (user_id, query, category))
    conn.commit()
    conn.close()
