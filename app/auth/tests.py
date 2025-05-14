# Create your tests here.
import unittest
from flask import url_for
from app import app, db
from app.models import User

class AuthTests(unittest.TestCase):
    def setUp(self):
        """Set up test variables and initialize app."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        
    def tearDown(self):
        """Tear down all setup variables."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_signup_page(self):
        """Test the signup page loads correctly."""
        response = self.app.get('/signup', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
    def test_login_page(self):
        """Test the login page loads correctly."""
        response = self.app.get('/login', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
    def test_signup(self):
        """Test user registration."""
        response = self.app.post(
            '/signup',
            data={
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'password123',
                'confirm_password': 'password123'
            },
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        user = User.query.filter_by(username='testuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')
        
    def test_invalid_signup(self):
        """Test invalid user registration with non-matching passwords."""
        response = self.app.post(
            '/signup',
            data={
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'password123',
                'confirm_password': 'different_password'
            },
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        user = User.query.filter_by(username='testuser').first()
        self.assertIsNone(user)  # User should not be created