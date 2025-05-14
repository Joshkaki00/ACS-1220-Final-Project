# Create your forms here.

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectMultipleField, SubmitField, FloatField, PasswordField
from wtforms.validators import DataRequired, Length, NumberRange, URL, Optional, Email, EqualTo, ValidationError
from app.models import Category, User

class RecipeForm(FlaskForm):
    """Form for creating and editing recipes."""
    
    title = StringField('Recipe Title', validators=[
        DataRequired(),
        Length(min=3, max=100, message='Title must be between 3 and 100 characters')
    ])
    
    description = TextAreaField('Description', validators=[
        DataRequired(),
        Length(min=10, message='Description must be at least 10 characters')
    ])
    
    preparation_time = IntegerField('Preparation Time (minutes)', validators=[
        DataRequired(),
        NumberRange(min=1, message='Preparation time must be at least 1 minute')
    ])
    
    cooking_time = IntegerField('Cooking Time (minutes)', validators=[
        DataRequired(),
        NumberRange(min=0, message='Cooking time must be a positive number')
    ])
    
    servings = IntegerField('Servings', validators=[
        DataRequired(),
        NumberRange(min=1, message='Recipe must serve at least 1 person')
    ])
    
    image_url = StringField('Image URL', validators=[
        Optional(),
        URL(message='Please provide a valid URL for the image')
    ])
    
    category_ids = SelectMultipleField('Categories', coerce=int)
    
    submit = SubmitField('Save Recipe')
    
    def __init__(self, *args, **kwargs):
        """Initialize the form and set up category choices."""
        super(RecipeForm, self).__init__(*args, **kwargs)
        self.category_ids.choices = [(c.id, c.name) for c in Category.query.order_by('name')]


class IngredientForm(FlaskForm):
    """Form for adding an ingredient to a recipe."""
    
    ingredient_id = SelectMultipleField('Ingredient', coerce=int)
    quantity = FloatField('Quantity', validators=[
        DataRequired(),
        NumberRange(min=0.01, message='Quantity must be greater than 0')
    ])
    
    submit = SubmitField('Add Ingredient')


class CommentForm(FlaskForm):
    """Form for adding a comment to a recipe."""
    
    content = TextAreaField('Comment', validators=[
        DataRequired(),
        Length(min=3, max=500, message='Comment must be between 3 and 500 characters')
    ])
    
    submit = SubmitField('Post Comment')
    
    
class ProfileForm(FlaskForm):
    """Form for editing user profile."""
    
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=80, message='Username must be between 3 and 80 characters')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address')
    ])
    
    profile_picture = StringField('Profile Picture URL', validators=[
        Optional(),
        URL(message='Please provide a valid URL for the profile picture')
    ])
    
    current_password = PasswordField('Current Password')
    
    new_password = PasswordField('New Password', validators=[
        Optional(),
        Length(min=6, message='Password must be at least 6 characters')
    ])
    
    confirm_password = PasswordField('Confirm New Password', validators=[
        Optional(),
        EqualTo('new_password', message='Passwords must match')
    ])
    
    submit = SubmitField('Update Profile')
    
    def __init__(self, original_username, original_email, *args, **kwargs):
        """Initialize the form with original username and email."""
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email
    
    def validate_username(self, username):
        """Check if username is already taken."""
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        """Check if email is already registered."""
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email is already registered. Please use a different one.')