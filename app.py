import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash

from config import config
from auth import auth
from admin import admin
import main

def create_app(config_name='default'):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize Flask-Session
    Session(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Configure logging
    if not os.path.exists(app.config['LOG_DIR']):
        os.makedirs(app.config['LOG_DIR'])
    
    # Setup rating logger
    rating_logger = logging.getLogger('rating_logger')
    rating_logger.setLevel(logging.INFO)
    rating_handler = logging.FileHandler(app.config['RATING_LOG_FILE'])
    rating_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    rating_logger.addHandler(rating_handler)
    
    # Copy demo data to data directory if not exists
    _initialize_data(app)
    
    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(main.main)
    app.register_blueprint(admin, url_prefix='/admin')
    
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}
    
    return app

def _initialize_data(app):
    """Initialize data files from demo data if they don't exist."""
    # Check if talks data exists, if not copy from demo
    if not os.path.exists(app.config['TALKS_FILE']):
        demo_talks_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                      'upload', 'talks_demo.json')
        if os.path.exists(demo_talks_path):
            with open(demo_talks_path, 'r') as f:
                talks_data = json.load(f)
            
            with open(app.config['TALKS_FILE'], 'w') as f:
                json.dump(talks_data, f, indent=4)
    
    # Check if speakers data exists, if not copy from demo
    if not os.path.exists(app.config['SPEAKERS_FILE']):
        demo_speakers_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                         'upload', 'speaker_demo.json')
        if os.path.exists(demo_speakers_path):
            with open(demo_speakers_path, 'r') as f:
                speakers_data = json.load(f)
            
            with open(app.config['SPEAKERS_FILE'], 'w') as f:
                json.dump(speakers_data, f, indent=4)
    
    # Initialize empty users file if it doesn't exist
    if not os.path.exists(app.config['USERS_FILE']):
        with open(app.config['USERS_FILE'], 'w') as f:
            json.dump({}, f, indent=4)
    
    # Initialize empty ratings file if it doesn't exist
    if not os.path.exists(app.config['RATINGS_FILE']):
        with open(app.config['RATINGS_FILE'], 'w') as f:
            json.dump({}, f, indent=4)
    
    # Initialize empty comments file if it doesn't exist
    if not os.path.exists(app.config['COMMENTS_FILE']):
        with open(app.config['COMMENTS_FILE'], 'w') as f:
            json.dump({}, f, indent=4)

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    app.run(host='0.0.0.0', port=5000)
