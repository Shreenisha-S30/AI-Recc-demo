import requests

BASE_URL = 'https://www.themealdb.com/api/json/v1/1'

def search_meals(query):
    url = f"{BASE_URL}/search.php?s={query}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('meals') or []
    return []

def get_meal_details(meal_id):
    url = f"{BASE_URL}/lookup.php?i={meal_id}"
    response = requests.get(url)
    if response.status_code == 200:
        meals = response.json().get('meals')
        if meals:
            return meals[0]
    return None

def get_meals_by_category(category):
    url = f"{BASE_URL}/filter.php?c={category}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('meals', [])
    return []

def get_meals_by_area(area):
    url = f"{BASE_URL}/filter.php?a={area}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('meals', [])
    return []

def recommend_related_meals(category):
    return get_meals_by_category(category)[:10]

def extract_ingredients(meal_dict):
    ingredients = []
    for i in range(1, 21):
        ingredient = meal_dict.get(f'strIngredient{i}')
        measure = meal_dict.get(f'strMeasure{i}')
        if ingredient and ingredient.strip():
            ingredients.append(f"{measure.strip()} {ingredient.strip()}" if measure else ingredient)
    return ingredients
