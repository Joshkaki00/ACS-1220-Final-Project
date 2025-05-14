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
    """User model for authentication and recipe ownership."""
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    profile_picture = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    recipes = db.relationship('Recipe', back_populates='user', cascade='all, delete-orphan')
    comments = db.relationship('Comment', back_populates='user', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'

class Recipe(db.Model):
    """Recipe model for culinary creations."""
    
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
    categories = db.relationship('Category', secondary=recipe_categories, 
                                back_populates='recipes')
    
    def __repr__(self):
        return f'<Recipe {self.title}>'

class Ingredient(db.Model):
    """Ingredient model for recipe components."""
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    measurement_unit = db.Column(db.String(50), nullable=False)
    
    recipe_ingredients = db.relationship('RecipeIngredient', 
                                        back_populates='ingredient',
                                        cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Ingredient {self.name}>'

class RecipeIngredient(db.Model):
    """Join table for recipes and ingredients with quantity."""
    
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
    """Category model for recipe classification."""
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    recipes = db.relationship('Recipe', secondary=recipe_categories, 
                             back_populates='categories')
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Comment(db.Model):
    """Comment model for recipe feedback."""
    
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
    """Favorite model for tracking user favorites."""
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    
    user = db.relationship('User', back_populates='favorites')
    recipe = db.relationship('Recipe', back_populates='favorites')
    
    # Ensure a user can only favorite a recipe once
    __table_args__ = (db.UniqueConstraint('user_id', 'recipe_id'),)
    
    def __repr__(self):
        return f'<Favorite {self.user_id}:{self.recipe_id}>'