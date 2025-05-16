# Create your forms here.
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Regexp
from app.models import User

class SignUpForm(FlaskForm):
    """
    Form for user registration with detailed validation.
    
    Includes validation for username format, email format, password strength,
    and checks for existing users in the database.
    """
    
    username = StringField('Username', validators=[
        DataRequired(message="Username is required"),
        Length(min=3, max=80, message='Username must be between 3 and 80 characters'),
        Regexp('^[A-Za-z0-9_-]*$', message="Username can only contain letters, numbers, underscores and hyphens")
    ])
    email = StringField('Email', validators=[
        DataRequired(message="Email is required"),
        Email(message='Please enter a valid email address'),
        Length(max=80, message='Email must be less than 80 characters')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required"),
        Length(min=6, message='Password must be at least 6 characters long'),
        Regexp('(?=.*\d)(?=.*[a-z])(?=.*[A-Z])', 
               message="Password must include at least one uppercase letter, one lowercase letter, and one number")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="Please confirm your password"),
        EqualTo('password', message='Passwords must match exactly')
    ])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        """Check if username is already taken."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        """Check if email is already registered."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already registered. Please use a different one or try logging in.')


class LoginForm(FlaskForm):
    """
    Form for user login with remember me functionality.
    
    Provides fields for username/password authentication with an option
    to remember the login session.
    """
    
    username = StringField('Username', validators=[
        DataRequired(message="Please enter your username")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Please enter your password")
    ])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')