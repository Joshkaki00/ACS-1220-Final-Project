from flask import Flask, render_template

def create_app(config_class=None):
    """
    Application factory function to create and configure the Flask app.
    
    Args:
        config_class: Configuration class to use (defaults to app.config.Config)
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_class is None:
        from app.config import Config
        app.config.from_object(Config)
    else:
        app.config.from_object(config_class)
    
    # Initialize extensions
    from app.extensions import db, bcrypt, login_manager
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    
    # Set up login manager
    from app.models import User
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.auth.routes import auth
    from app.main.routes import main
    
    app.register_blueprint(auth)
    app.register_blueprint(main)
    
    # Register error handlers
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template('errors/500.html'), 500
    
    return app
