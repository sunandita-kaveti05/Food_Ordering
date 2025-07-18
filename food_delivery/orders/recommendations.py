from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import FoodItem, BrowseHistory, CartItem, OrderItem
from django.utils import timezone
from datetime import timedelta
import numpy as np
import pandas as pd
from collections import defaultdict

def get_dynamic_recommendations(user, num_recs=6, prefer_same_restaurant=True):
    if not user.is_authenticated:
        return []

    recent_days = 7
    recent_threshold = timezone.now() - timedelta(days=recent_days)

    cart_items = CartItem.objects.filter(user=user)
    order_items = OrderItem.objects.filter(order__user=user, order__is_paid=True)
    browse_items = BrowseHistory.objects.filter(user=user, timestamp__gte=recent_threshold)

    cart_ids = list(cart_items.values_list('food_item__id', flat=True))
    purchased_ids = list(order_items.values_list('food_item__id', flat=True))
    browsed_ids = list(browse_items.values_list('food_item__id', flat=True))

    weights = defaultdict(float)
    for fid in browsed_ids:
        weights[fid] += 0.2
    for fid in purchased_ids:
        weights[fid] += 0.6
    for fid in cart_ids:
        weights[fid] += 1.0

    if cart_ids:
        interacted_ids = cart_ids
    elif purchased_ids:
        interacted_ids = purchased_ids
    elif browsed_ids:
        interacted_ids = browsed_ids
    else:
        return []

    interacted_ids = list(set(interacted_ids))
    interacted_items = FoodItem.objects.filter(id__in=interacted_ids)
    if not interacted_items.exists():
        return []

    interacted_df = pd.DataFrame([{
        'id': item.id,
        'text': f"{item.name} {item.description} {item.category} {item.food_type}",
        'weight': weights[item.id]
    } for item in interacted_items])

    candidate_qs = FoodItem.objects.exclude(id__in=interacted_ids).filter(is_available=True)
    
    # Filter by same restaurant (if cart exists and flag is on)
    if prefer_same_restaurant and cart_items.exists():
        restaurant = cart_items.first().food_item.restaurant
        candidate_qs = candidate_qs.filter(restaurant=restaurant)

    candidates = list(candidate_qs)
    if not candidates:
        return []

    candidates_df = pd.DataFrame([{
        'id': item.id,
        'text': f"{item.name} {item.description} {item.category} {item.food_type}",
        'item': item
    } for item in candidates])

    combined = pd.concat([interacted_df['text'], candidates_df['text']], ignore_index=True)
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(combined)

    interacted_vecs = tfidf_matrix[:len(interacted_df)]
    candidate_vecs = tfidf_matrix[len(interacted_df):]

    weights_matrix = np.array(interacted_df['weight']).reshape(-1, 1)
    weighted_interacted_vecs = interacted_vecs.multiply(weights_matrix)

    similarities = cosine_similarity(candidate_vecs, weighted_interacted_vecs)
    scores = similarities.sum(axis=1)

    candidates_df['score'] = scores
    candidates_df = candidates_df.sort_values(by='score', ascending=False)

    # Optional: filter out same-named items from cart
    cart_names = set(i.food_item.name.lower() for i in cart_items)
    candidates_df = candidates_df[candidates_df['item'].apply(lambda x: x.name.lower() not in cart_names)]

    top_items = candidates_df.head(num_recs)['item']

    return list(top_items)
