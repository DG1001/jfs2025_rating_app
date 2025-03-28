from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import time
from models import User

auth = Blueprint('auth', __name__)

def generate_token(length=16):
    """Generate a random access token."""
    return secrets.token_hex(length)

# User loader for Flask-Login
@auth.record_once
def on_load(state):
    login_manager = LoginManager()
    login_manager.init_app(state.app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """User login with access token."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        token = request.form.get('token', '').strip()
        
        if not token:
            flash('Bitte geben Sie ein Access-Token ein.', 'danger')
            return render_template('auth/login.html')
        
        # Find user with matching token
        user = User.get_by_token(token)
        if user:
            login_user(user)
            flash(f'Willkommen, {user.name}!', 'success')
            return redirect(url_for('main.index'))
        
        flash('Ungültiges Access-Token.', 'danger')
    
    return render_template('auth/login.html')

@auth.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """Admin login with username and password."""
    if current_user.is_authenticated and session.get('is_admin'):
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Bitte geben Sie Benutzername und Passwort ein.', 'danger')
            return render_template('auth/admin_login.html')
        
        # Check against environment variables
        if (username == current_app.config['ADMIN_USERNAME'] and 
            password == current_app.config['ADMIN_PASSWORD']):
            # Create admin user
            admin_user = User(
                id='admin',
                name='Administrator',
                email='admin@example.com',
                token='admin-token'
            )
            login_user(admin_user)
            session['is_admin'] = True
            flash('Admin-Login erfolgreich!', 'success')
            return redirect(url_for('admin.dashboard'))
        
        flash('Ungültiger Benutzername oder Passwort.', 'danger')
    
    return render_template('auth/admin_login.html')

@auth.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    session.pop('is_admin', None)
    flash('Sie wurden erfolgreich abgemeldet.', 'success')
    return redirect(url_for('auth.login'))
