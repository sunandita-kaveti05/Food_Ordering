from django.db import models
from django.contrib.auth.models import User # Ensure User model is imported

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    rating = models.FloatField(default=0.0)
    budget_range = models.CharField(max_length=50)
    image = models.ImageField(upload_to='restaurant_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class FoodItem(models.Model):
    CATEGORY_CHOICES = [
        ('Starter', 'Starter'),
        ('Main Course', 'Main Course'),
        ('Dessert', 'Dessert'),
        ('Drink', 'Drink'),
        ('Side Dish', 'Side Dish'), # Added 'Side Dish' based on previous context for recommendations
        ('Snacks', 'Snacks'), # Added 'Snacks' as a potential category for recommendations
    ]
    FOOD_TYPE_CHOICES = [('Veg', 'Veg'), ('Non-Veg', 'Non-Veg')]

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='food_items')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    is_available = models.BooleanField(default=True)
    food_type = models.CharField(max_length=10, choices=FOOD_TYPE_CHOICES, default='Veg')
    rating = models.FloatField(default=0.0)
    image = models.ImageField(upload_to='food_images/', blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Main Course')

    def __str__(self):
        return f"{self.name} ({self.category})"


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.food_item.name} x{self.quantity}"

    def total_price(self):
        return self.food_item.price * self.quantity


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # Added to store order total
    is_paid = models.BooleanField(default=False) # Added for payment status

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=7, decimal_places=2)
    rating = models.IntegerField(null=True, blank=True)

    def total_price(self):
        return self.price * self.quantity

# --- NEW: Browse History Model ---
class BrowseHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'food_item') # A user only has one entry per item, timestamp updates
        verbose_name_plural = "Browse Histories"

    def __str__(self):
        return f"{self.user.username} browsed {self.food_item.name} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    
