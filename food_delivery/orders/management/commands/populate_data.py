from django.core.management.base import BaseCommand
from orders.models import Restaurant, FoodItem
import random

class Command(BaseCommand):
    help = 'Populates realistic restaurants and food items'

    def handle(self, *args, **kwargs):
        restaurant_data = {
            "KFC": [
                ("Zinger Burger", "Starter", "Crispy fried chicken burger with spicy mayo.", 199),
                ("Chicken Bucket", "Snacks", "Bucket of golden fried chicken pieces.", 499),
                ("Pepsi", "Drink", "Chilled soft drink to go with your chicken.", 60),
                ("Popcorn Chicken", "Snacks", "Bite-sized crispy chicken chunks.", 159),
                ("French Fries", "Side Dish", "Golden, crispy potato fries.", 99),
                ("Veg Strips", "Starter", "Crispy veggie strips with dip.", 139),
                ("Choco Lava Cake", "Dessert", "Warm chocolate-filled cake.", 99),
                ("Rice Bowl Combo", "Main Course", "Fried chicken over spiced rice.", 229),
                ("Peri Peri Chicken", "Main Course", "Spicy grilled chicken.", 279),
                ("Masala Corn", "Snacks", "Hot corn seasoned with butter & spices.", 89),
            ],
            "Domino's": [
                ("Margherita Pizza", "Main Course", "Classic cheese pizza with tomato sauce.", 199),
                ("Farmhouse Pizza", "Main Course", "Loaded with mushrooms, onions, capsicum, tomato.", 349),
                ("Garlic Breadsticks", "Side Dish", "Soft breadsticks with garlic seasoning.", 129),
                ("Choco Lava Cake", "Dessert", "Molten chocolate cake served warm.", 99),
                ("Peppy Paneer", "Main Course", "Paneer, capsicum & red paprika pizza.", 299),
                ("Coke", "Drink", "Chilled Coca-Cola can.", 60),
                ("Taco Mexicana", "Snacks", "Spicy veg filling in a crunchy taco shell.", 159),
                ("Cheesy Dip", "Side Dish", "Domino’s special creamy cheese dip.", 35),
                ("Chicken Dominator", "Main Course", "Loaded with chicken sausage, tikka, keema.", 449),
                ("Butterscotch Mousse", "Dessert", "Creamy dessert with a caramel twist.", 89),
            ],
            "McDonald's": [
                ("McAloo Tikki", "Main Course", "Spiced potato patty burger.", 99),
                ("Ice Cream", "Dessert", "Vanilla soft serve in a cone or cup.", 60),
                ("Chicken Maharaja Mac", "Main Course", "Big chicken burger with double patties.", 289),
                ("Fries", "Side Dish", "World-famous fries, golden & crispy.", 99),
                ("McFlurry Oreo", "Dessert", "Vanilla soft serve with Oreo bits.", 109),
                ("Veg Pizza McPuff", "Snacks", "Hot pocket filled with cheesy pizza filling.", 49),
                ("Coke Float", "Drink", "Cola topped with vanilla ice cream.", 89),
                ("Egg McMuffin", "Starter", "Egg & cheese in a soft muffin.", 129),
                ("McSpicy Paneer", "Main Course", "Paneer patty in spicy coating.", 199),
                ("Iced Tea", "Drink", "Cool and refreshing lemon iced tea.", 69),
                ("Strawberry Sundae", "Dessert", "Vanilla ice cream with strawberry syrup.", 99),
            ],
            "Starbucks": [
                ("Caffè Latte", "Drink", "Espresso with steamed milk & light foam.", 210),
                ("Cold Brew", "Drink", "Slow-steeped cold coffee.", 250),
                ("Dark Forest Pastry", "Dessert", "Rich pastry with chocolate sponge and cherries.", 180),
                ("Blueberry Muffin", "Dessert", "Soft muffin loaded with blueberries.", 170),
                ("Veg Sandwich", "Main Course", "Grilled veggie sandwich with pesto.", 230),
                ("Java Chip Frappuccino", "Drink", "Coffee blended with chocolate chips.", 280),
                ("Cheese Croissant", "Snacks", "Flaky croissant filled with melted cheese.", 150),
                ("Hot Chocolate", "Drink", "Steamed milk with chocolate sauce.", 200),
                ("Butter Scone", "Dessert", "British-style scone with butter.", 140),
                ("Spinach & Corn Sandwich", "Side Dish", "Creamy filling with spinach & corn.", 190),
                ("Strawberry Cheesecake", "Dessert", "Classic cheesecake topped with strawberry glaze.", 240),
            ],
            "Biryani House": [
                ("Chicken Biryani", "Main Course", "Hyderabadi dum biryani with tender chicken.", 249),
                ("Mutton Biryani", "Main Course", "Fragrant rice with slow-cooked mutton.", 349),
                ("Paneer Biryani", "Main Course", "Spiced paneer cubes with basmati rice.", 199),
                ("Raita", "Side Dish", "Cool yogurt with cucumber & spices.", 40),
                ("Gulab Jamun", "Dessert", "Soft syrupy sweet balls.", 90),
                ("Masala Coke", "Drink", "Cola with a spicy Indian twist.", 60),
                ("Naan", "Side Dish", "Soft tandoori flatbread served with curries.", 35),
                ("Egg Biryani", "Main Course", "Boiled eggs with spicy biryani rice.", 199),
                ("Chicken 65", "Starter", "Crispy spicy fried chicken bites.", 160),
                ("Veg Kurma", "Side Dish", "Mixed vegetable curry with coconut gravy.", 130),
                ("Double Ka Meetha", "Dessert", "Hyderabadi bread pudding with saffron.", 110),
            ],
            "Nawab's Chicken": [
                ("Tandoori Chicken", "Starter", "Char-grilled chicken marinated in yogurt & spices.", 289),
                ("Butter Chicken", "Main Course", "Creamy tomato gravy with tender chicken.", 320),
                ("Chicken Kebab", "Snacks", "Juicy minced chicken skewers.", 199),
                ("Kesar Phirni", "Dessert", "Chilled rice pudding with saffron.", 90),
                ("Masala Kulcha", "Side Dish", "Stuffed kulcha with onion & spices.", 60),
                ("Lassi", "Drink", "Traditional sweet Punjabi yogurt drink.", 70),
                ("Chicken Handi", "Main Course", "Spicy handi-style chicken curry.", 310),
                ("Chicken Tikka Masala", "Main Course", "Roasted chicken in spicy curry sauce.", 330),
                ("Jeera Rice", "Side Dish", "Steamed rice with cumin.", 70),
                ("Chicken Soup", "Starter", "Hot and spicy chicken broth.", 99),
            ],
            "Chocolate World": [
                ("Chocolate Fudge Cake", "Dessert", "Rich layered chocolate cake.", 180),
                ("Brownie with Ice Cream", "Dessert", "Warm brownie topped with vanilla scoop.", 150),
                ("Hot Chocolate", "Drink", "Creamy hot chocolate with cocoa.", 130),
                ("Chocolate Shake", "Drink", "Thick shake made with dark chocolate.", 160),
                ("Nutella Waffle", "Dessert", "Crispy waffle drizzled with Nutella.", 170),
                ("Litchi Ice Cream", "Dessert", "Refreshing litchi-flavored creamy ice cream.", 120),
                ("Dark Forest Pastry", "Dessert", "Moist chocolate pastry with a cherry twist.", 160),
                ("Choco Chip Cookie", "Snacks", "Baked cookie filled with chocolate chips.", 70),
                ("Dark Chocolate Tart", "Dessert", "Mini tart with rich dark chocolate.", 190),
                ("Chocolate Truffle", "Dessert", "Gooey truffle balls rolled in cocoa.", 120),
                ("Swiss Roll", "Dessert", "Soft sponge roll with chocolate cream.", 140),
                ("Cold Mocha", "Drink", "Chilled mocha coffee with cream.", 150),
            ],
            "Disney Hotel": [
                ("Mickey Waffles", "Dessert", "Waffles shaped like Mickey, served with syrup.", 160),
                ("Magic Potion Smoothie", "Drink", "Colorful mixed fruit smoothie.", 140),
                ("Fairy Dust Fries", "Snacks", "Fries with glittery cheese dust (edible shimmer).", 120),
                ("Donald’s Egg Sandwich", "Main Course", "Egg salad sandwich with toast.", 150),
                ("Pluto’s Chicken Popcorn", "Snacks", "Crispy chicken bites with dips.", 180),
                ("Snow White Salad", "Side Dish", "Apple, lettuce, walnuts & dressing.", 110),
                ("Cinderella Soup", "Starter", "Creamy mushroom soup.", 130),
                ("Goofy Burger", "Main Course", "Towering veg burger with 3 patties.", 200),
                ("Frozen Ice Cream", "Dessert", "Blueberry ice cream inspired by Elsa.", 130),
                ("Toon Town Pizza", "Main Course", "Cheesy mini pizzas shaped like stars.", 170),
            ],
            "Foodie Hub": [
                ("Chole Bhature", "Main Course", "Spiced chickpeas with fluffy fried bread.", 140),
                ("Masala Dosa", "Main Course", "South Indian crepe with potato stuffing.", 120),
                ("Pav Bhaji", "Main Course", "Spicy mashed veggies served with buttered buns.", 130),
                ("Jalebi", "Dessert", "Crispy syrup-soaked spirals.", 90),
                ("Aam Panna", "Drink", "Refreshing raw mango summer drink.", 70),
                ("Samosa", "Snacks", "Fried pastry filled with spicy potatoes.", 40),
                ("Paneer Pakoda", "Snacks", "Batter-fried paneer fritters.", 100),
                ("Buttermilk", "Drink", "Chilled spiced chaas.", 60),
                ("Rajma Chawal", "Main Course", "Red kidney beans curry with rice.", 140),
                ("Falooda", "Dessert", "Rose-flavored milkshake with vermicelli & jelly.", 120),
                ("Ice Cream", "Dessert", "Classic vanilla ice cream served chilled.", 50),
            ]
        }

        for rest_name, menu_items in restaurant_data.items():
            restaurant = Restaurant.objects.create(
                name=rest_name,
                rating=round(random.uniform(3.5, 5.0), 1),
                is_active=True,
                budget_range=random.choice(["Low", "Medium", "High"])
            )

            for name, category, description, price in menu_items:
                FoodItem.objects.create(
                    restaurant=restaurant,
                    name=name,
                    category=category,
                    description=description,
                    price=price,
                    food_type=random.choice(["Veg", "Non-Veg"]),
                    rating=round(random.uniform(3.6, 5.0), 1),
                    is_available=True
                )

        self.stdout.write(self.style.SUCCESS("✅ Populated restaurants and food items successfully."))
