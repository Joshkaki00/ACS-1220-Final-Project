from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Recipe, Category, User, Ingredient, RecipeIngredient, Comment
from app.main.forms import RecipeForm, CommentForm

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

@main.route('/recipes/<int:recipe_id>', methods=['GET', 'POST'])
def recipe_detail(recipe_id):
    """Display a specific recipe with details and handle comments."""
    recipe = Recipe.query.get_or_404(recipe_id)
    form = CommentForm()
    
    if form.validate_on_submit() and current_user.is_authenticated:
        comment = Comment(
            content=form.content.data,
            recipe_id=recipe.id,
            user_id=current_user.id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added!', 'success')
        return redirect(url_for('main.recipe_detail', recipe_id=recipe.id))
        
    return render_template('main/recipe_detail.html', 
                           recipe=recipe,
                           form=form,
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