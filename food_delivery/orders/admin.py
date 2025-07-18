from django.contrib import admin
from .models import Restaurant, FoodItem, CartItem, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')
    inlines = [OrderItemInline]
    ordering = ['-created_at']

admin.site.register(Restaurant)
admin.site.register(FoodItem)
admin.site.register(CartItem)
admin.site.register(Order, OrderAdmin)
