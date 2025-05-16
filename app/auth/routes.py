from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import bcrypt, db
from app.auth.forms import SignUpForm, LoginForm
from app.models import User
from sqlalchemy.exc import IntegrityError

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Route for user registration.
    
    Handles user signup with validation and error handling for database operations.
    """
    # Redirect to home if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = SignUpForm()
    if form.validate_on_submit():
        try:
            # Hash the password
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            
            # Create new user
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=hashed_password
            )
            
            # Add user to database
            db.session.add(user)
            db.session.commit()
            
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        except IntegrityError:
            db.session.rollback()
            # Check which unique constraint was violated
            existing_username = User.query.filter_by(username=form.username.data).first()
            if existing_username:
                flash('That username is already taken. Please choose a different one.', 'danger')
                form.username.errors.append('Username already exists')
            else:
                flash('That email is already registered. Please use a different one.', 'danger')
                form.email.errors.append('Email already exists')
        except Exception as e:
            db.session.rollback()
            flash(f'An unexpected error occurred. Please try again.', 'danger')
            print(f"Error during signup: {str(e)}")
    
    return render_template('auth/signup.html', form=form, title='Sign Up')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Route for user login.
    
    Authenticates users and manages login attempts with proper error handling.
    """
    # Redirect to home if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        try:
            # Find user by username
            user = User.query.filter_by(username=form.username.data).first()
            
            # Check if user exists
            if not user:
                flash('No account found with that username.', 'danger')
                form.username.errors.append('Username not found')
                return render_template('auth/login.html', form=form, title='Login')
            
            # Check if password is correct
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                
                # Redirect to the page user was trying to access before login
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):  # Security check for redirects
                    return redirect(next_page)
                return redirect(url_for('main.index'))
            else:
                flash('Incorrect password. Please try again.', 'danger')
                form.password.errors.append('Incorrect password')
        except Exception as e:
            flash('An error occurred during login. Please try again.', 'danger')
            print(f"Error during login: {str(e)}")
    
    return render_template('auth/login.html', form=form, title='Login')

@auth.route('/logout')
@login_required
def logout():
    """
    Route for user logout.
    
    Handles user logout and redirects to the home page.
    """
    try:
        logout_user()
        flash('You have been logged out successfully.', 'info')
    except Exception as e:
        flash('An error occurred during logout.', 'warning')
        print(f"Error during logout: {str(e)}")
    
    return redirect(url_for('main.index'))