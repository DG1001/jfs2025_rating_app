from flask import Flask, session, request, redirect, url_for, flash
from flask_login import LoginManager, current_user
import os
import json

from config import Config
from models import User

def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)
    
    # Ensure data folder exists
    os.makedirs(app.config['DATA_DIR'], exist_ok=True)
    
    # Create empty data files if they don't exist
    if not os.path.exists(app.config['USERS_FILE']):
        with open(app.config['USERS_FILE'], 'w') as f:
            json.dump({}, f)
    
    if not os.path.exists(app.config['RATINGS_FILE']):
        with open(app.config['RATINGS_FILE'], 'w') as f:
            json.dump({}, f)
    
    if not os.path.exists(app.config['COMMENTS_FILE']):
        with open(app.config['COMMENTS_FILE'], 'w') as f:
            json.dump({}, f)
    
    # Copy demo data files if they don't exist
    if not os.path.exists(app.config['TALKS_FILE']):
        try:
            with open(app.config['TALKS_DEMO_FILE'], 'r') as src:
                with open(app.config['TALKS_FILE'], 'w') as dst:
                    dst.write(src.read())
        except Exception as e:
            print(f"Error copying talks demo file: {e}")
    
    if not os.path.exists(app.config['SPEAKERS_FILE']):
        try:
            with open(app.config['SPEAKERS_DEMO_FILE'], 'r') as src:
                with open(app.config['SPEAKERS_FILE'], 'w') as dst:
                    dst.write(src.read())
        except Exception as e:
            print(f"Error copying speakers demo file: {e}")
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)
    
    # Register blueprints
    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    
    # Fix for admin login redirect issue
    @app.before_request
    def check_admin_session():
        if current_user.is_authenticated and session.get('is_admin') and request.path.startswith('/admin'):
            # Ensure the user is still authenticated and has admin privileges
            if current_user.id != 'admin':
                session.pop('is_admin', None)
                flash('Admin-Sitzung abgelaufen. Bitte melden Sie sich erneut an.', 'warning')
                return redirect(url_for('auth.admin_login'))
    
    return app
