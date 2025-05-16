# Create your models here.
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from datetime import datetime
from app.extensions import db

# Association table for Recipe and Category (many-to-many)
recipe_categories = db.Table('recipe_categories',
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    """
    User model for authentication and recipe ownership.
    
    Attributes:
        id (int): Primary key for the user
        username (str): Unique username for the user
        email (str): Unique email address for the user
        password (str): Hashed password for authentication
        profile_picture (str): URL to the user's profile picture
        created_at (datetime): Timestamp when the user account was created
        recipes (relationship): One-to-many relationship with Recipe model
        comments (relationship): One-to-many relationship with Comment model
        favorites (relationship): One-to-many relationship with Favorite model
        ratings (relationship): One-to-many relationship with Rating model
    """
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    profile_picture = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    recipes = db.relationship('Recipe', back_populates='user', cascade='all, delete-orphan')
    comments = db.relationship('Comment', back_populates='user', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', back_populates='user', cascade='all, delete-orphan')
    ratings = db.relationship('Rating', back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'

class Recipe(db.Model):
    """
    Recipe model for culinary creations.
    
    Attributes:
        id (int): Primary key for the recipe
        title (str): Title of the recipe
        description (text): Detailed description of the recipe
        preparation_time (int): Time required for preparation in minutes
        cooking_time (int): Time required for cooking in minutes
        servings (int): Number of servings the recipe yields
        image_url (str): URL to the recipe image
        created_at (datetime): Timestamp when the recipe was created
        user_id (int): Foreign key to the User who created the recipe
        user (relationship): Many-to-one relationship with User model
        recipe_ingredients (relationship): One-to-many relationship with RecipeIngredient model
        comments (relationship): One-to-many relationship with Comment model
        favorites (relationship): One-to-many relationship with Favorite model
        ratings (relationship): One-to-many relationship with Rating model
        categories (relationship): Many-to-many relationship with Category model
    """
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    preparation_time = db.Column(db.Integer, nullable=False)  # in minutes
    cooking_time = db.Column(db.Integer, nullable=False)  # in minutes
    servings = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    user = db.relationship('User', back_populates='recipes')
    recipe_ingredients = db.relationship('RecipeIngredient', 
                                        back_populates='recipe',
                                        cascade='all, delete-orphan')
    comments = db.relationship('Comment', back_populates='recipe',
                              cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', back_populates='recipe',
                               cascade='all, delete-orphan')
    ratings = db.relationship('Rating', back_populates='recipe',
                             cascade='all, delete-orphan')
    categories = db.relationship('Category', secondary=recipe_categories, 
                                back_populates='recipes')
    
    def __repr__(self):
        return f'<Recipe {self.title}>'
    
    @property
    def average_rating(self):
        """Calculate the average rating for this recipe."""
        if not self.ratings:
            return 0
        return sum(rating.value for rating in self.ratings) / len(self.ratings)

class Ingredient(db.Model):
    """
    Ingredient model for recipe components.
    
    Attributes:
        id (int): Primary key for the ingredient
        name (str): Unique name of the ingredient
        measurement_unit (str): Default unit of measurement for the ingredient
        recipe_ingredients (relationship): One-to-many relationship with RecipeIngredient model
    """
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    measurement_unit = db.Column(db.String(50), nullable=False)
    
    recipe_ingredients = db.relationship('RecipeIngredient', 
                                        back_populates='ingredient',
                                        cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Ingredient {self.name}>'

class RecipeIngredient(db.Model):
    """
    Join table for recipes and ingredients with quantity information.
    
    Attributes:
        id (int): Primary key
        recipe_id (int): Foreign key to the Recipe
        ingredient_id (int): Foreign key to the Ingredient
        quantity (float): Quantity of the ingredient used in the recipe
        recipe (relationship): Many-to-one relationship with Recipe model
        ingredient (relationship): Many-to-one relationship with Ingredient model
    """
    
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), 
                             nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    
    recipe = db.relationship('Recipe', back_populates='recipe_ingredients')
    ingredient = db.relationship('Ingredient', back_populates='recipe_ingredients')
    
    def __repr__(self):
        return f'<RecipeIngredient {self.recipe_id}:{self.ingredient_id}>'

class Category(db.Model):
    """
    Category model for recipe classification.
    
    Attributes:
        id (int): Primary key for the category
        name (str): Unique name of the category
        description (text): Description of what the category represents
        recipes (relationship): Many-to-many relationship with Recipe model
    """
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    recipes = db.relationship('Recipe', secondary=recipe_categories, 
                             back_populates='categories')
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Comment(db.Model):
    """
    Comment model for recipe feedback.
    
    Attributes:
        id (int): Primary key for the comment
        content (text): Content of the comment
        created_at (datetime): Timestamp when the comment was created
        recipe_id (int): Foreign key to the Recipe being commented on
        user_id (int): Foreign key to the User who made the comment
        recipe (relationship): Many-to-one relationship with Recipe model
        user (relationship): Many-to-one relationship with User model
    """
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    recipe = db.relationship('Recipe', back_populates='comments')
    user = db.relationship('User', back_populates='comments')
    
    def __repr__(self):
        return f'<Comment {self.id}>'

class Favorite(db.Model):
    """
    Favorite model for tracking user favorites.
    
    Attributes:
        id (int): Primary key for the favorite entry
        user_id (int): Foreign key to the User who favorited
        recipe_id (int): Foreign key to the Recipe that was favorited
        user (relationship): Many-to-one relationship with User model
        recipe (relationship): Many-to-one relationship with Recipe model
    
    Constraints:
        - A user can only favorite a recipe once (unique constraint on user_id, recipe_id)
    """
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    
    user = db.relationship('User', back_populates='favorites')
    recipe = db.relationship('Recipe', back_populates='favorites')
    
    # Ensure a user can only favorite a recipe once
    __table_args__ = (db.UniqueConstraint('user_id', 'recipe_id'),)
    
    def __repr__(self):
        return f'<Favorite {self.user_id}:{self.recipe_id}>'

class Rating(db.Model):
    """
    Rating model for recipe ratings.
    
    Attributes:
        id (int): Primary key for the rating
        value (int): Rating value (1-5)
        created_at (datetime): Timestamp when the rating was submitted
        recipe_id (int): Foreign key to the Recipe being rated
        user_id (int): Foreign key to the User who rated
        recipe (relationship): Many-to-one relationship with Recipe model
        user (relationship): Many-to-one relationship with User model
    
    Constraints:
        - A user can only rate a recipe once (unique constraint on user_id, recipe_id)
    """
    
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)  # 1-5 star rating
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    recipe = db.relationship('Recipe', back_populates='ratings')
    user = db.relationship('User', back_populates='ratings')
    
    # Ensure a user can only rate a recipe once
    __table_args__ = (db.UniqueConstraint('user_id', 'recipe_id'),)
    
    def __repr__(self):
        return f'<Rating {self.user_id}:{self.recipe_id}:{self.value}>'