from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Sum , Min , Max 
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.middleware.csrf import get_token
from django.views.decorators.http import require_POST

from .models import ( Restaurant, FoodItem, CartItem, Order, OrderItem, BrowseHistory)

from .models import FoodItem, Restaurant

def home(request):
    search = request.GET.get('search', '').strip()
    budget = request.GET.get('budget', '').strip()
    food_type = request.GET.get('food_type', '').strip()
    sort_by = request.GET.get('sort_by', '').strip()
    selected_categories = request.GET.getlist('category')

    categories = [choice[0] for choice in FoodItem.CATEGORY_CHOICES]

    # If no filters/search → return all restaurants normally
    is_filter_applied = search or budget or food_type or selected_categories or sort_by

    if is_filter_applied:
        # Filter food items
        food_items = FoodItem.objects.filter(is_available=True)

        if search:
            food_items = food_items.filter(name__icontains=search)
        if selected_categories:
            food_items = food_items.filter(category__in=selected_categories)
        if budget:
            food_items = food_items.filter(restaurant__budget_range__iexact=budget)
        if food_type:
            food_items = food_items.filter(food_type__iexact=food_type)

        if sort_by == "rating":
            food_items = food_items.order_by('-rating')
        elif sort_by == "price_asc":
            food_items = food_items.order_by('price')
        elif sort_by == "price_desc":
            food_items = food_items.order_by('-price')

        # Map items to restaurants
        restaurant_map = {}
        for item in food_items.select_related('restaurant'):
            rid = item.restaurant.id
            if rid not in restaurant_map:
                restaurant_map[rid] = {
                    "restaurant": item.restaurant,
                    "items": []
                }
            restaurant_map[rid]["items"].append(item)

        # Attach filtered items
        restaurants = []
        for rid, data in restaurant_map.items():
            rest = data["restaurant"]
            rest.filtered_items = data["items"]
            restaurants.append(rest)

    else:
        # No filters → show all active restaurants (no food filtering)
        restaurants = Restaurant.objects.filter(is_active=True)

    return render(request, 'home.html', {
        'search': search,
        'budget': budget,
        'food_type': food_type,
        'sort_by': sort_by,
        'categories': categories,
        'selected_categories': selected_categories,
        'restaurants': restaurants,
    })



# Signup
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest

@require_POST
def ajax_login(request):
    form = AuthenticationForm(request, data=request.POST)
    if form.is_valid():
        login(request, form.get_user())
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid credentials'})


@require_POST
def ajax_signup(request):
    form = UserCreationForm(request.POST)
    if form.is_valid():
        user = form.save()
        # Do NOT log in the user
        return JsonResponse({'success': True, 'message': 'Signup successful. Please log in.'})
    else:
        errors = [str(err[0]) for err in form.errors.values()]
        return JsonResponse({'success': False, 'error': ' '.join(errors)})



# Restaurant list (optional: direct page)
@login_required
def restaurant_list(request):
    restaurants = Restaurant.objects.filter(is_active=True)
    return render(request, 'restaurant_list.html', {'restaurants': restaurants})


@login_required
def restaurant_detail(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    
    # Existing filtering logic for food items within the restaurant
    search_query = request.GET.get('food_search', '')
    food_type_filter = request.GET.get('type', '')
    category_list = request.GET.getlist('category')
    sort_by = request.GET.get('sort', '')
    price_min = request.GET.get('min_price')
    price_max = request.GET.get('max_price')

    food_items = restaurant.food_items.all().order_by('name')

    if search_query:
        food_items = food_items.filter(name__icontains=search_query)
    if food_type_filter:
        food_items = food_items.filter(food_type=food_type_filter)
    if category_list:
        food_items = food_items.filter(category__in=category_list)
    if price_min and price_max:
        try:
            food_items = food_items.filter(price__gte=int(price_min), price__lte=int(price_max))
        except ValueError:
            pass

    if sort_by == 'price':
        food_items = food_items.order_by('price')
    elif sort_by == 'rating':
        food_items = food_items.order_by('-rating')


    # All unique categories for the filter dropdown (using FoodItem.CATEGORY_CHOICES as source)
    all_categories = FoodItem.CATEGORY_CHOICES
    all_categories_values = [choice[0] for choice in all_categories]

    # --- NEW: Browse History Tracking ---
    for item in food_items:
        BrowseHistory.objects.update_or_create(
            user=request.user,
            food_item=item,
            defaults={'timestamp': timezone.now()}
        )
    # --- END NEW ---

    context = {
        'restaurant': restaurant,
        'food_items': food_items,
        'search_query': search_query,
        'food_type': food_type_filter,
        'selected_categories': category_list,
        'sort_by': sort_by,
        'price_min': price_min,
        'price_max': price_max,
        'categories': all_categories_values,
    }
    # IMPORTANT: Corrected template path
    return render(request, 'restaurant_detail.html', context)


# Function to get CSRF token (can be removed if not directly used in JS via this view, but good to have)
def csrf_input(request):
    token = get_token(request)
    return f'<input type="hidden" name="csrfmiddlewaretoken" value="{token}">'

@login_required
def add_to_cart(request, item_id):
    food_item = get_object_or_404(FoodItem, id=item_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, food_item=food_item)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    # 🍟 Keep existing combo rules for immediate suggestions (pop-up style)
    combo_rules = {
        "Chicken Burger": ["Fries", "Coke"],
        "Chicken Pizza": ["Garlic Bread", "Pepsi"],
        "Biryani": ["Raita", "Gulab Jamun"],
    }

    suggestion_names = combo_rules.get(food_item.name, [])
    
    # Exclude items already in cart from immediate suggestions
    items_in_cart_ids = CartItem.objects.filter(user=request.user).values_list('food_item__id', flat=True)

    suggestions = FoodItem.objects.filter(
        name__in=suggestion_names,
        restaurant=food_item.restaurant,
        is_available=True
    ).exclude(id__in=list(items_in_cart_ids))

    if suggestions:
        html = f'<strong>Recommended with {food_item.name}:</strong><ul style="list-style: none; padding: 0;">'
        for item in suggestions:
            html += f'''
                <li style="margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                    <span>{item.name} – ₹{item.price}</span>
                    <button onclick="addToCartAjax({item.id})" style="
                        padding: 5px 10px;
                        background-color: #0077cc;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                        margin-left: 10px;">Add</button>
                </li>
            '''
        html += '</ul><button onclick="document.getElementById(\'recommendation-box\').remove();" style="float:right; background: none; border: none; font-size: 1.2em; cursor: pointer;">❌</button>'
        messages.info(request, html)

    return redirect('restaurant_detail', pk=food_item.restaurant.id)



from django.db.models import Count

from collections import Counter
from .models import FoodItem, CartItem
from django.db.models import Q

def get_cart_based_recommendations(user, num_recs=6):
    if not user.is_authenticated:
        return []

    cart_items = CartItem.objects.filter(user=user).select_related('food_item', 'food_item__restaurant')

    if not cart_items.exists():
        return []

    seen_ids = list(cart_items.values_list('food_item__id', flat=True))

    # ❗ Fix: Use only the first restaurant
    restaurant = cart_items.first().food_item.restaurant

    # Ensure all cart items are from same restaurant
    if not all(item.food_item.restaurant == restaurant for item in cart_items):
        return []

    is_cart_veg = all(item.food_item.food_type == "Veg" for item in cart_items)

    category_counter = Counter(item.food_item.category for item in cart_items)
    top_categories = [cat for cat, _ in category_counter.most_common(1)]

    complementary_map = {
        'Main Course': ['Dessert', 'Drink', 'Side Dish'],
        'Starter': ['Drink', 'Main Course'],
        'Dessert': ['Drink'],
        'Drink': ['Snacks'],
        'Side Dish': ['Drink', 'Dessert'],
        'Snacks': ['Drink'],
    }

    target_categories = set()
    for cat in top_categories:
        target_categories.update(complementary_map.get(cat, []))

    suggestions = FoodItem.objects.filter(
        restaurant=restaurant,
        category__in=target_categories,
        is_available=True
    ).exclude(id__in=seen_ids)

    if is_cart_veg:
        suggestions = suggestions.filter(food_type='Veg')

    return list(suggestions.order_by('?')[:num_recs])


# @login_required
# def view_cart(request):
#     cart_items = CartItem.objects.filter(user=request.user).order_by('food_item__restaurant', 'food_item__name')
#     total_price = sum(item.total_price() for item in cart_items)

#     recommended_items = get_cart_based_recommendations(request.user)

#     return render(request, 'cart.html', {
#         'cart_items': cart_items,
#         'total_price': total_price,
#         'recommended_items': recommended_items,
#     })

from .recommendations import get_dynamic_recommendations

@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user).order_by('food_item__restaurant', 'food_item__name')
    total_price = sum(item.total_price() for item in cart_items)

    if cart_items.exists():
        recommended_items = get_dynamic_recommendations(request.user)
    else:
        recommended_items = []

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'recommended_items': recommended_items,
    })



@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    return redirect('view_cart')


@login_required
def place_order(request):
    cart_items = CartItem.objects.filter(user=request.user)

    if not cart_items.exists():
        return redirect('view_cart')

    order = Order.objects.create(user=request.user)
    total = 0

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            food_item=item.food_item,
            quantity=item.quantity,
            price=item.food_item.price
        )
        total += float(item.quantity * item.food_item.price)

    cart_items.delete()

    order.total_amount = total
    order.is_paid = True
    order.save()

    return render(request, 'order_success.html', {'order': order})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_history.html', {'orders': orders})

@login_required
def update_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'increase':
            item.quantity += 1
            item.save()
        elif action == 'decrease':
            item.quantity -= 1
            if item.quantity <= 0:
                item.delete()
            else:
                item.save()

    return redirect('view_cart')

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import FoodItem, CartItem

@login_required
def ajax_add_to_cart(request, item_id):
    if request.method == "POST":
        food_item = get_object_or_404(FoodItem, id=item_id)
        cart_item, created = CartItem.objects.get_or_create(user=request.user, food_item=food_item)
        if not created:
            cart_item.quantity += 1
            cart_item.save()

        cart_count = CartItem.objects.filter(user=request.user).aggregate(Sum('quantity'))['quantity__sum'] or 0

        return JsonResponse({
            'success': True,
            'item_name': food_item.name,
            'cart_count': cart_count,
            'unit_price': float(food_item.price),
            'restaurant': food_item.restaurant.name,  # ✅ send restaurant name
            'cart_item_id': cart_item.id             # ✅ send cart item ID for forms
        })
    return JsonResponse({'success': False})



from django.http import JsonResponse
from django.db.models import Sum
from .models import CartItem

@login_required
def cart_count_api(request):
    count = CartItem.objects.filter(user=request.user).aggregate(Sum('quantity'))['quantity__sum'] or 0
    return JsonResponse({'count': count})

from .recommendations import get_dynamic_recommendations

@login_required
def ajax_recommendations(request):
    if not CartItem.objects.filter(user=request.user).exists():
        return JsonResponse({'recommendations': []})

    rec_items = get_dynamic_recommendations(request.user)
    data = [{
        'id': item.id,
        'name': item.name,
        'price': float(item.price),
        'category': item.category,
    } for item in rec_items]
    return JsonResponse({'recommendations': data})

# views.py
from django.views.decorators.http import require_POST

from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect

@require_POST
@login_required
def rate_order_item(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)
    rating = request.POST.get('rating')
    if rating and rating.isdigit():
        rating = int(rating)
        if 1 <= rating <= 5:
            item.rating = rating
            item.save()
    return redirect('order_history')
