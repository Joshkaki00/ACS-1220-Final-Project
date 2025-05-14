from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Recipe, Category, User

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
    # This will be implemented later
    flash('Profile editing will be available soon!', 'info')
    return redirect(url_for('main.profile', user_id=current_user.id))

@main.route('/recipes')
def all_recipes():
    """Display all recipes with filtering options."""
    # Get query parameters for filtering
    category_id = request.args.get('category', type=int)
    
    # Base query
    query = Recipe.query
    
    # Apply category filter if provided
    if category_id:
        category = Category.query.get_or_404(category_id)
        query = query.filter(Recipe.categories.contains(category))
    
    # Get recipes, newest first
    recipes = query.order_by(Recipe.created_at.desc()).all()
    
    # Get all categories for filter dropdown
    categories = Category.query.all()
    
    return render_template('main/recipes.html', 
                          recipes=recipes, 
                          categories=categories,
                          selected_category=category_id,
                          title='All Recipes')

@main.route('/recipes/<int:recipe_id>')
def recipe_detail(recipe_id):
    """Display a specific recipe with details."""
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template('main/recipe_detail.html', 
                           recipe=recipe,
                           title=recipe.title)

@main.route('/recipes/new', methods=['GET', 'POST'])
@login_required
def new_recipe():
    """Create a new recipe."""
    # This will be implemented later with forms
    flash('Recipe creation form will be available soon!', 'info')
    return redirect(url_for('main.all_recipes'))

@main.route('/recipes/<int:recipe_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    """Edit an existing recipe."""
    recipe = Recipe.query.get_or_404(recipe_id)
    
    # Check if the current user is the owner of the recipe
    if recipe.user_id != current_user.id:
        flash('You can only edit your own recipes!', 'danger')
        return redirect(url_for('main.recipe_detail', recipe_id=recipe.id))
    
    # This will be implemented later with forms
    flash('Recipe editing form will be available soon!', 'info')
    return redirect(url_for('main.recipe_detail', recipe_id=recipe.id))

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