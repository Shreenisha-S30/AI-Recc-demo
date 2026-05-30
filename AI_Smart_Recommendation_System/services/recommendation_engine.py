import random
from database.db import get_db_connection

def calculate_confidence_score(base_score=80.0, user_history_bonus=0.0):
    """
    Simulates a ML-based confidence score generation.
    Returns something like 95% Match.
    """
    final_score = base_score + user_history_bonus + random.uniform(0, 5)
    final_score = min(final_score, 99.0) # Cap at 99%
    return int(final_score)

def get_user_preferences(user_id):
    """
    Fetch all user interactions to extract favorite keywords/genres.
    """
    conn = get_db_connection()
    searches = conn.execute("SELECT category, query FROM search_history WHERE user_id = ?", (user_id,)).fetchall()
    favorites = conn.execute("SELECT item_type, title FROM favorites WHERE user_id = ?", (user_id,)).fetchall()
    ratings = conn.execute("SELECT item_type, item_id, rating FROM ratings WHERE user_id = ? AND rating >= 4", (user_id,)).fetchall()
    conn.close()

    prefs = {
        'searches': [dict(s) for s in searches],
        'favorites': [dict(f) for f in favorites],
        'highly_rated': [dict(r) for r in ratings]
    }
    return prefs

def rerank_recommendations(user_id, raw_items, item_type):
    """
    Hybrid Step: Rerank API similarity results using local user preferences.
    In a full production scenario, this uses word2vec/TFIDF on keywords.
    For this prototype, it adjusts the confidence score and sorts.
    """
    prefs = get_user_preferences(user_id) if user_id else {}
    
    # We will just assign a synthetic score for now based on user data existence.
    user_bonus = 10.0 if user_id and (prefs.get('favorites') or prefs.get('searches')) else 0.0
    
    ranked_results = []
    
    # Process up to 20 raw items
    for item in raw_items[:20]:
        # base score logic depending on API ranking (earlier elements = higher base)
        base = max(70.0, 90.0 - len(ranked_results)) 
        
        score = calculate_confidence_score(base, user_bonus)
        
        ranked_results.append({
            "item": item,
            "match_score": f"{score}% Match",
            "score_val": score
        })
        
    # Sort by the final calculated score
    ranked_results = sorted(ranked_results, key=lambda x: x["score_val"], reverse=True)
    return ranked_results
