"""Script to seed the database with sample data."""
from app.extensions import app, db, bcrypt
from app.models import User, Recipe, Ingredient, RecipeIngredient, Category, Comment, Favorite
from datetime import datetime, timedelta
import random

def seed_database():
    """Seed the database with sample data."""
    # Clear out existing data
    db.drop_all()
    db.create_all()
    
    print("Seeding database...")
    
    # Create users
    users = []
    for i in range(1, 4):
        hashed_password = bcrypt.generate_password_hash('password').decode('utf-8')
        user = User(
            username=f'user{i}',
            email=f'user{i}@example.com',
            password=hashed_password,
            profile_picture=None,
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
        )
        users.append(user)
        db.session.add(user)
    
    # Create categories
    categories = []
    category_names = ['Breakfast', 'Lunch', 'Dinner', 'Dessert', 'Vegetarian', 'Vegan', 'Gluten-Free']
    for name in category_names:
        category = Category(
            name=name,
            description=f'Delicious {name.lower()} recipes for every occasion.'
        )
        categories.append(category)
        db.session.add(category)
    
    # Create ingredients
    ingredients = []
    ingredient_data = [
        ('Flour', 'cups'),
        ('Sugar', 'cups'),
        ('Eggs', ''),
        ('Milk', 'cups'),
        ('Butter', 'tablespoons'),
        ('Salt', 'teaspoons'),
        ('Pepper', 'teaspoons'),
        ('Olive Oil', 'tablespoons'),
        ('Chicken Breast', 'pounds'),
        ('Onion', ''),
        ('Garlic', 'cloves'),
        ('Tomatoes', ''),
        ('Rice', 'cups'),
        ('Pasta', 'ounces'),
        ('Cheese', 'cups'),
        ('Lettuce', 'cups'),
        ('Carrots', ''),
        ('Potatoes', ''),
        ('Broccoli', 'cups'),
        ('Beef', 'pounds')
    ]
    for name, unit in ingredient_data:
        ingredient = Ingredient(name=name, measurement_unit=unit)
        ingredients.append(ingredient)
        db.session.add(ingredient)
    
    # Commit to get IDs assigned
    db.session.commit()
    
    # Create recipes
    recipes = []
    recipe_data = [
        {
            'title': 'Classic Pancakes',
            'description': 'Fluffy and delicious pancakes that are perfect for breakfast.',
            'preparation_time': 10,
            'cooking_time': 15,
            'servings': 4,
            'image_url': 'https://images.unsplash.com/photo-1575853121743-60c24f0a7502',
            'user_id': users[0].id,
            'categories': [categories[0].id, categories[4].id],
            'ingredients': [
                (ingredients[0].id, 2),  # 2 cups flour
                (ingredients[1].id, 0.25),  # 1/4 cup sugar
                (ingredients[2].id, 2),  # 2 eggs
                (ingredients[3].id, 1.5),  # 1.5 cups milk
                (ingredients[4].id, 3)  # 3 tbsp butter
            ]
        },
        {
            'title': 'Spaghetti Carbonara',
            'description': 'A classic Italian pasta dish with eggs, cheese, pancetta, and black pepper.',
            'preparation_time': 15,
            'cooking_time': 20,
            'servings': 4,
            'image_url': 'https://images.unsplash.com/photo-1551183053-bf91a1d81141',
            'user_id': users[1].id,
            'categories': [categories[1].id, categories[2].id],
            'ingredients': [
                (ingredients[13].id, 16),  # 16 oz pasta
                (ingredients[2].id, 3),  # 3 eggs
                (ingredients[14].id, 1),  # 1 cup cheese
                (ingredients[5].id, 0.5),  # 1/2 tsp salt
                (ingredients[6].id, 1)  # 1 tsp pepper
            ]
        },
        {
            'title': 'Vegetable Stir Fry',
            'description': 'A healthy and colorful vegetable stir fry that is quick to prepare.',
            'preparation_time': 20,
            'cooking_time': 10,
            'servings': 3,
            'image_url': 'https://images.unsplash.com/photo-1512058556646-c4da40fba323',
            'user_id': users[2].id,
            'categories': [categories[1].id, categories[2].id, categories[4].id, categories[5].id],
            'ingredients': [
                (ingredients[7].id, 2),  # 2 tbsp olive oil
                (ingredients[10].id, 3),  # 3 cloves garlic
                (ingredients[9].id, 1),  # 1 onion
                (ingredients[18].id, 2),  # 2 cups broccoli
                (ingredients[16].id, 2),  # 2 carrots
                (ingredients[5].id, 1),  # 1 tsp salt
                (ingredients[6].id, 0.5)  # 0.5 tsp pepper
            ]
        }
    ]
    
    for data in recipe_data:
        recipe = Recipe(
            title=data['title'],
            description=data['description'],
            preparation_time=data['preparation_time'],
            cooking_time=data['cooking_time'],
            servings=data['servings'],
            image_url=data['image_url'],
            user_id=data['user_id'],
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 15))
        )
        
        # Add categories
        for category_id in data['categories']:
            category = Category.query.get(category_id)
            recipe.categories.append(category)
        
        recipes.append(recipe)
        db.session.add(recipe)
    
    # Commit to get recipe IDs
    db.session.commit()
    
    # Add ingredients to recipes
    for i, data in enumerate(recipe_data):
        for ingredient_id, quantity in data['ingredients']:
            recipe_ingredient = RecipeIngredient(
                recipe_id=recipes[i].id,
                ingredient_id=ingredient_id,
                quantity=quantity
            )
            db.session.add(recipe_ingredient)
    
    # Add comments
    comments = [
        "This recipe is amazing! I'll definitely make it again.",
        "I added some extra spices and it turned out great!",
        "My family loved this recipe. Thanks for sharing!",
        "Simple and delicious. Perfect for a weeknight dinner.",
        "I've made this three times now and it's always a hit."
    ]
    
    for recipe in recipes:
        # Add 1-3 random comments to each recipe
        for _ in range(random.randint(1, 3)):
            user = random.choice(users)
            comment = Comment(
                content=random.choice(comments),
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 10)),
                recipe_id=recipe.id,
                user_id=user.id
            )
            db.session.add(comment)
    
    # Add favorites
    for user in users:
        # Each user favorites 1-2 random recipes
        for _ in range(random.randint(1, 2)):
            recipe = random.choice(recipes)
            # Make sure user hasn't already favorited this recipe
            existing_favorite = Favorite.query.filter_by(
                user_id=user.id, recipe_id=recipe.id
            ).first()
            if not existing_favorite:
                favorite = Favorite(user_id=user.id, recipe_id=recipe.id)
                db.session.add(favorite)
    
    db.session.commit()
    
    print("Database seeded successfully!")

if __name__ == '__main__':
    with app.app_context():
        seed_database() 