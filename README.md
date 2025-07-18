# 🍔 Online Food Ordering System

A feature-rich, Django-based web application for browsing restaurants, filtering food, and placing orders with a personalized cart and smart recommendation system. Built as a full-stack college project — clean, modular, and scalable.

---

## 🚀 Features

* 🔐 **User Authentication** – Sign up, log in/out, CSRF-protected forms
* 🏪 **Restaurants & Food Browsing**

  * Search, filters (category, type, price range, rating, budget)
  * Dynamic, filterable menu per restaurant
* 🛒 **Cart Functionality**

  * Add/remove items, update quantity
  * Live cart count with AJAX
* 📦 **Order Placement**

  * Full order flow with success screen
  * Track previous orders via order history
* ⭐ **Rate Your Order**

  * Users can rate individual food items from their orders
* 🧠 **Smart Food Recommendations**

  * Content-based recommendation system using TF-IDF + cosine similarity
  * Real-time suggestions based on browsing, cart, and past orders
  * AJAX-enabled for dynamic UI updates
* 🎨 **Simple UI** – Clean, responsive, and practical without flashy distractions

---

## 📊 Smart Recommendation Engine

The system uses a **real-time, intelligent recommendation engine**:

### 🔍 Behavior Considered:

* **Cart Items**: 1.0 weight
* **Past Orders**: 0.6 weight
* **Browsing History**: 0.2 weight

### ⚙️ How It Works:

* Combines text data (`name`, `description`, `type`, `category`) of food items
* Applies **TF-IDF vectorization**
* Calculates **cosine similarity** between interacted and candidate items
* Ranks candidates based on total weighted similarity score
* Filters out already-carted items and (optionally) restricts to the same restaurant

### 🧪 Stack Used:

* `scikit-learn` – `TfidfVectorizer`, `cosine_similarity`
* `pandas`, `numpy`
* Django models and ORM queries

```python
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(text_data)
similarity = cosine_similarity(candidate_vecs, weighted_user_vecs)
scores = similarity.sum(axis=1)
```

> 🍟 “Add Fries with that Burger?” — now your app *actually* means it.

---

## 🏗️ Tech Stack

* **Frontend**: HTML, CSS, JS (vanilla + minimal Bootstrap icons)
* **Backend**: Django, Python
* **Database**: SQLite (for simplicity)
* **ML/Logic**: scikit-learn, numpy, pandas

---

## 🛠️ Installation & Setup

1. **Clone the repo**:

   ```bash
   git clone https://github.com/your-username/food-ordering-system.git
   cd food-ordering-system
   ```

2. **Create & activate virtual environment**:

   ```bash
   python -m venv env
   source env/bin/activate  # For Windows: env\Scripts\activate
   ```

3. **Install requirements**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Start the development server**:

   ```bash
   python manage.py runserver
   ```

---

## 📸 Screenshots (Optional)

*Add minimal UI screenshots like Home Page, Cart, Order History.*

---

## 👩‍💻 Author

**Sunandita Kaveti**
B.Tech CSE,  – The Apollo University
[LinkedIn](https://linkedin.com) | [GitHub](https://github.com)


---

Let your food app not just be functional — but intelligent 🍕✨
