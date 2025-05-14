# Create your tests here.

import unittest
from flask import url_for
from app import app, db
from app.models import User, Recipe, Category
from app.extensions import bcrypt

class MainRouteTests(unittest.TestCase):
    def setUp(self):
        """Set up test variables and initialize app."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create a test user
        hashed_password = bcrypt.generate_password_hash('password').decode('utf-8')
        self.user = User(
            username='testuser',
            email='test@example.com',
            password=hashed_password
        )
        db.session.add(self.user)
        
        # Create test categories
        self.category = Category(name='Test Category', description='Test description')
        db.session.add(self.category)
        
        db.session.commit()
        
        # Create a test recipe
        self.recipe = Recipe(
            title='Test Recipe',
            description='Test description',
            preparation_time=10,
            cooking_time=20,
            servings=4,
            user_id=self.user.id
        )
        db.session.add(self.recipe)
        db.session.commit()
        
    def tearDown(self):
        """Tear down all setup variables."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_homepage(self):
        """Test the homepage loads correctly."""
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
    def test_all_recipes(self):
        """Test the all recipes page loads correctly."""
        response = self.app.get('/recipes', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
    def test_recipe_detail(self):
        """Test the recipe detail page loads correctly."""
        response = self.app.get(f'/recipes/{self.recipe.id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
    def test_profile(self):
        """Test the user profile page loads correctly."""
        response = self.app.get(f'/profile/{self.user.id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
    def test_category_filter(self):
        """Test filtering recipes by category."""
        # Link recipe to category
        self.recipe.categories.append(self.category)
        db.session.commit()
        
        response = self.app.get(f'/recipes?category={self.category.id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)