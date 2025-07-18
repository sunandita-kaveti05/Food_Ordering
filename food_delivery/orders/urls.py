from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('', views.home, name='home'),
     path('ajax/login/', views.ajax_login, name='ajax_login'),
    path('ajax/signup/', views.ajax_signup, name='ajax_signup'),

    # ✅ Logout still fine
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),

    path('restaurants/', views.restaurant_list, name='restaurant_list'),
    path('restaurant/<int:pk>/', views.restaurant_detail, name='restaurant_detail'),
    path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('place-order/', views.place_order, name='place_order'),
    path('place-order/', views.place_order, name='place_order'),
    path('orders/history/', views.order_history, name='order_history'),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('ajax/add-to-cart/<int:item_id>/', views.ajax_add_to_cart, name='ajax_add_to_cart'),
    path('cart/count/', views.cart_count_api, name='cart_count_api'),
    path('ajax/recommendations/', views.ajax_recommendations, name='ajax_recommendations'),
    path('rate-order-item/<int:item_id>/', views.rate_order_item, name='rate_order_item'),


    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

