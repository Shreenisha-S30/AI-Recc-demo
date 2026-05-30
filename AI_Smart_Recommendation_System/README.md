# AI Smart Recommendation System

A modern full-stack web application that provides AI-based recommendations for movies, books, and food using content-based filtering.

## Tech Stack
- Frontend: HTML5, CSS3, JavaScript, jQuery
- Backend: Python Flask
- Database: SQLite
- AI/ML: Pandas, Scikit-learn (TF-IDF, CountVectorizer, Cosine Similarity)

## Features
- **Movie Recommendations:** Uses genre, keywords, and overview.
- **Book Recommendations:** Uses genre, author, and description.
- **Food Recommendations:** Filters based on cuisine, veg/non-veg, spice level, and meal type.
- Modern responsive dashboard with Dark/Light mode theme.

## Installation Guide
1. Clone this repository or open the project folder.
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python app.py
   ```
5. Open your browser and navigate to `http://127.0.0.1:5000/`.

## Datasets
Dummy datasets for movies, books, and food are included in the `datasets` folder to test the recommendation engine.