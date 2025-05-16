from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db, bcrypt
from app.models import Recipe, Category, User, Ingredient, RecipeIngredient, Comment, Favorite, Rating
from app.main.forms import RecipeForm, CommentForm, ProfileForm, RatingForm
from sqlalchemy import or_

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Homepage route showing featured recipes and categories."""
    # Get 6 most recent recipes for featured display
    recipes = Recipe.query.order_by(Recipe.created_at.desc()).limit(6).all()
    
    # Get all categories
    categories = Category.query.all()
    
    return render_template('main/index.html', 
                          recipes=recipes, 
                          categories=categories,
                          title='Home - CulinaryConnect')

@main.route('/profile/<int:user_id>')
def profile(user_id):
    """Display a user's profile and their recipes."""
    user = User.query.get_or_404(user_id)
    recipes = Recipe.query.filter_by(user_id=user.id).order_by(Recipe.created_at.desc()).all()
    
    return render_template('main/profile.html', 
                          user=user, 
                          recipes=recipes,
                          title=f"{user.username}'s Profile")

@main.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Allow users to edit their profile information."""
    form = ProfileForm(original_username=current_user.username, original_email=current_user.email)
    
    if form.validate_on_submit():
        # Verify current password if changing password
        password_changed = form.new_password.data and form.current_password.data
        
        if password_changed and not bcrypt.check_password_hash(current_user.password, form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return render_template('main/profile_edit.html', form=form, title='Edit Profile')
        
        # Update user information
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.profile_picture = form.profile_picture.data
        
        # Update password if provided
        if password_changed:
            hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            current_user.password = hashed_password
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('main.profile', user_id=current_user.id))
    
    elif request.method == 'GET':
        # Pre-populate form with current user data
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.profile_picture.data = current_user.profile_picture
    
    return render_template('main/profile_edit.html', form=form, title='Edit Profile')

@main.route('/recipes')
def all_recipes():
    """
    Display all recipes with filtering options and pagination.
    
    Supports filtering by category and paginates results for better performance.
    Also allows searching by recipe title and description.
    """
    # Get query parameters for filtering and search
    category_id = request.args.get('category', type=int)
    search_query = request.args.get('search', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = 9  # Number of recipes per page
    
    # Base query
    query = Recipe.query
    
    # Apply category filter if provided
    if category_id:
        category = Category.query.get_or_404(category_id)
        query = query.filter(Recipe.categories.contains(category))
    
    # Apply search filter if provided
    if search_query:
        search_terms = f"%{search_query}%"
        query = query.filter(
            or_(
                Recipe.title.ilike(search_terms),
                Recipe.description.ilike(search_terms)
            )
        )
    
    # Get recipes, newest first with pagination
    pagination = query.order_by(Recipe.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    recipes = pagination.items
    
    # Get all categories for filter dropdown
    categories = Category.query.all()
    
    return render_template('main/recipes.html', 
                          recipes=recipes,
                          pagination=pagination,
                          categories=categories,
                          selected_category=category_id,
                          search_query=search_query,
                          title='All Recipes')

@main.route('/recipes/<int:recipe_id>', methods=['GET', 'POST'])
def recipe_detail(recipe_id):
    """
    Display a specific recipe with details and handle comments and ratings.
    
    Allows authenticated users to comment on and rate recipes.
    """
    recipe = Recipe.query.get_or_404(recipe_id)
    comment_form = CommentForm()
    rating_form = RatingForm()
    
    # Check if user has already rated this recipe
    user_rating = None
    if current_user.is_authenticated:
        user_rating = Rating.query.filter_by(
            user_id=current_user.id, 
            recipe_id=recipe.id
        ).first()
        
        # Pre-select current rating if it exists
        if user_rating:
            rating_form.value.data = user_rating.value
    
    # Handle comment submission
    if comment_form.validate_on_submit() and current_user.is_authenticated:
        comment = Comment(
            content=comment_form.content.data,
            recipe_id=recipe.id,
            user_id=current_user.id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added!', 'success')
        return redirect(url_for('main.recipe_detail', recipe_id=recipe.id))
    
    # Handle rating submission
    if 'rating_submit' in request.form and rating_form.validate_on_submit() and current_user.is_authenticated:
        if user_rating:
            # Update existing rating
            user_rating.value = rating_form.value.data
            flash('Your rating has been updated!', 'success')
        else:
            # Create new rating
            rating = Rating(
                value=rating_form.value.data,
                recipe_id=recipe.id,
                user_id=current_user.id
            )
            db.session.add(rating)
            flash('Your rating has been added!', 'success')
            
        db.session.commit()
        return redirect(url_for('main.recipe_detail', recipe_id=recipe.id))
        
    return render_template('main/recipe_detail.html', 
                           recipe=recipe,
                           comment_form=comment_form,
                           rating_form=rating_form,
                           user_rating=user_rating,
                           title=recipe.title)

@main.route('/recipes/new', methods=['GET', 'POST'])
@login_required
def new_recipe():
    """Create a new recipe."""
    form = RecipeForm()
    
    if form.validate_on_submit():
        recipe = Recipe(
            title=form.title.data,
            description=form.description.data,
            preparation_time=form.preparation_time.data,
            cooking_time=form.cooking_time.data,
            servings=form.servings.data,
            image_url=form.image_url.data,
            user_id=current_user.id
        )
        
        # Add categories
        for category_id in form.category_ids.data:
            category = Category.query.get(category_id)
            if category:
                recipe.categories.append(category)
        
        db.session.add(recipe)
        db.session.commit()
        
        flash('Your recipe has been created!', 'success')
        return redirect(url_for('main.recipe_detail', recipe_id=recipe.id))
    
    return render_template('main/recipe_form.html', 
                           form=form,
                           title='Create Recipe',
                           heading='Create a New Recipe')

@main.route('/recipes/<int:recipe_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    """Edit an existing recipe."""
    recipe = Recipe.query.get_or_404(recipe_id)
    
    # Check if the current user is the owner of the recipe
    if recipe.user_id != current_user.id:
        flash('You can only edit your own recipes!', 'danger')
        return redirect(url_for('main.recipe_detail', recipe_id=recipe.id))
    
    form = RecipeForm()
    
    if request.method == 'GET':
        # Pre-fill the form with existing recipe data
        form.title.data = recipe.title
        form.description.data = recipe.description
        form.preparation_time.data = recipe.preparation_time
        form.cooking_time.data = recipe.cooking_time
        form.servings.data = recipe.servings
        form.image_url.data = recipe.image_url
        form.category_ids.data = [category.id for category in recipe.categories]
    
    if form.validate_on_submit():
        # Update recipe with form data
        recipe.title = form.title.data
        recipe.description = form.description.data
        recipe.preparation_time = form.preparation_time.data
        recipe.cooking_time = form.cooking_time.data
        recipe.servings = form.servings.data
        recipe.image_url = form.image_url.data
        
        # Update categories
        recipe.categories = []
        for category_id in form.category_ids.data:
            category = Category.query.get(category_id)
            if category:
                recipe.categories.append(category)
        
        db.session.commit()
        
        flash('Your recipe has been updated!', 'success')
        return redirect(url_for('main.recipe_detail', recipe_id=recipe.id))
    
    return render_template('main/recipe_form.html', 
                           form=form,
                           title='Edit Recipe',
                           heading=f'Edit Recipe: {recipe.title}')

@main.route('/recipes/<int:recipe_id>/delete', methods=['POST'])
@login_required
def delete_recipe(recipe_id):
    """Delete a recipe."""
    recipe = Recipe.query.get_or_404(recipe_id)
    
    # Check if the current user is the owner of the recipe
    if recipe.user_id != current_user.id:
        flash('You can only delete your own recipes!', 'danger')
        return redirect(url_for('main.recipe_detail', recipe_id=recipe.id))
    
    db.session.delete(recipe)
    db.session.commit()
    
    flash('Your recipe has been deleted!', 'success')
    return redirect(url_for('main.all_recipes'))

@main.route('/comments/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    """Delete a comment."""
    comment = Comment.query.get_or_404(comment_id)
    
    # Check if the current user is the owner of the comment
    if comment.user_id != current_user.id:
        flash('You can only delete your own comments!', 'danger')
        return redirect(url_for('main.recipe_detail', recipe_id=comment.recipe_id))
    
    recipe_id = comment.recipe_id
    
    db.session.delete(comment)
    db.session.commit()
    
    flash('Your comment has been deleted!', 'success')
    return redirect(url_for('main.recipe_detail', recipe_id=recipe_id))

@main.route('/dashboard')
@login_required
def dashboard():
    """
    User dashboard for managing recipes, favorites, and ratings.
    
    Displays user's recipes, favorites, and recently rated recipes in a dashboard layout.
    """
    # Get user's recipes
    user_recipes = Recipe.query.filter_by(user_id=current_user.id).order_by(Recipe.created_at.desc()).all()
    
    # Get user's favorite recipes
    favorites = Favorite.query.filter_by(user_id=current_user.id).order_by(Favorite.id.desc()).all()
    favorite_recipes = [favorite.recipe for favorite in favorites]
    
    # Get user's recent ratings
    recent_ratings = Rating.query.filter_by(user_id=current_user.id).order_by(Rating.created_at.desc()).limit(5).all()
    
    # Get counts
    recipe_count = len(user_recipes)
    favorite_count = len(favorites)
    comment_count = Comment.query.filter_by(user_id=current_user.id).count()
    rating_count = Rating.query.filter_by(user_id=current_user.id).count()
    
    return render_template('main/dashboard.html',
                          user_recipes=user_recipes,
                          favorite_recipes=favorite_recipes,
                          recent_ratings=recent_ratings,
                          recipe_count=recipe_count,
                          favorite_count=favorite_count,
                          comment_count=comment_count,
                          rating_count=rating_count,
                          title='My Dashboard')

@main.route('/favorites/toggle/<int:recipe_id>', methods=['POST'])
@login_required
def toggle_favorite(recipe_id):
    """
    Toggle a recipe as favorite/unfavorite.
    
    Adds or removes a recipe from the user's favorites.
    """
    recipe = Recipe.query.get_or_404(recipe_id)
    
    # Check if recipe is already favorited
    favorite = Favorite.query.filter_by(
        user_id=current_user.id,
        recipe_id=recipe.id
    ).first()
    
    if favorite:
        # Remove from favorites
        db.session.delete(favorite)
        db.session.commit()
        flash('Recipe removed from favorites', 'info')
    else:
        # Add to favorites
        favorite = Favorite(user_id=current_user.id, recipe_id=recipe.id)
        db.session.add(favorite)
        db.session.commit()
        flash('Recipe added to favorites', 'success')
    
    # Redirect back to the previous page
    next_page = request.referrer or url_for('main.recipe_detail', recipe_id=recipe_id)
    return redirect(next_page)