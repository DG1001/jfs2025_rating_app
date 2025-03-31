from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import time
import os
import json
import markdown
from models import User

auth = Blueprint('auth', __name__)

def generate_token(length=16):
    """Generate a random access token."""
    return secrets.token_hex(length)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """User login with access token via form or URL."""
    if current_user.is_authenticated:
        if session.get('is_admin'):
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.index'))
    
    # Check for token in URL first
    token = request.args.get('token')
    if token:
        user = User.get_by_token(token.strip())
        if user:
            login_user(user)
            # Check if this is the user's first login
            if 'first_login' not in session:
                try:
                    with open(os.path.join(current_app.config['BASE_DIR'], 'user_info.md'), 'r', encoding='utf-8') as f:
                        info_text = markdown.markdown(f.read())
                    session['show_info_box'] = info_text
                    session['first_login'] = False  # Mark as seen
                except FileNotFoundError:
                    # Try to use the template instead
                    from flask import render_template_string
                    try:
                        info_text = render_template_string("{% include 'info_content.html' %}")
                        session['show_info_box'] = info_text
                        session['first_login'] = False
                    except:
                        flash('Info-Text konnte nicht geladen werden.', 'warning')
            flash(f'Willkommen, {user.name}!', 'success')
            return redirect(url_for('main.index'))
        flash('Ungültiges Access-Token.', 'danger')
        return redirect(url_for('auth.login'))
    
    # Normal form login
    if request.method == 'POST':
        token = request.form.get('token', '').strip()
        
        if not token:
            flash('Bitte geben Sie ein Access-Token ein.', 'danger')
            return render_template('auth/login.html')
        
        user = User.get_by_token(token)
        if user:
            login_user(user)
            # Check if this is the user's first login
            if 'first_login' not in session:
                try:
                    with open(os.path.join(current_app.config['BASE_DIR'], 'user_info.md'), 'r', encoding='utf-8') as f:
                        info_text = markdown.markdown(f.read())
                    session['show_info_box'] = info_text
                    session['first_login'] = False  # Mark as seen
                except FileNotFoundError:
                    # Try to use the template instead
                    from flask import render_template_string
                    try:
                        info_text = render_template_string("{% include 'info_content.html' %}")
                        session['show_info_box'] = info_text
                        session['first_login'] = False
                    except:
                        flash('Info-Text konnte nicht geladen werden.', 'warning')
            flash(f'Willkommen, {user.name}!', 'success')
            return redirect(url_for('main.index'))
        
        flash('Ungültiges Access-Token.', 'danger')
    
    return render_template('auth/login.html')

@auth.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """Admin login with username and password."""
    # Prevent redirect loop - if we're already on admin-login page, don't check admin status
    if request.path == '/admin-login' and current_user.is_authenticated and session.get('is_admin'):
        # We're already an admin and on the admin login page, go directly to dashboard
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
            # Logout any existing user first
            if current_user.is_authenticated:
                logout_user()
                
            # Create admin user - make sure it's properly saved in the User storage
            admin_user = User(
                id='admin',
                name='Administrator',
                email='admin@example.com',
                token='admin-token'
            )
            
            # Save admin user to the users file to ensure it exists
            users = {}
            try:
                with open(current_app.config['USERS_FILE'], 'r') as f:
                    users = json.load(f)
            except Exception as e:
                print(f"Error loading users: {e}")
                
            # Add or update admin user
            users['admin'] = {
                'name': 'Administrator',
                'email': 'admin@example.com',
                'token': 'admin-token'
            }
            
            # Save updated users
            try:
                with open(current_app.config['USERS_FILE'], 'w') as f:
                    json.dump(users, f, indent=4)
            except Exception as e:
                print(f"Error saving admin user: {e}")
            
            # Now login the user
            login_user(admin_user, remember=True)
            session['is_admin'] = True
            session.permanent = True
            # Make sure the session is saved immediately
            session.modified = True
            
            print(f"Admin login successful. User authenticated: {current_user.is_authenticated}")
            flash('Admin-Login erfolgreich!', 'success')
            
            # Force a direct redirect to the admin dashboard
            return redirect(url_for('admin.dashboard'))
        
        flash('Ungültiger Benutzername oder Passwort.', 'danger')
    
    return render_template('auth/admin_login.html')

@auth.route('/dismiss-info', methods=['POST'])
@login_required
def dismiss_info():
    """Dismiss the info box and clear it from the session."""
    session.pop('show_info_box', None)
    return redirect(request.referrer or url_for('main.index'))

@auth.route('/logout')
@login_required
def logout():
    """User logout."""
    is_admin = session.get('is_admin', False)
    logout_user()
    session.pop('is_admin', None)
    flash('Sie wurden erfolgreich abgemeldet.', 'success')
    if is_admin:
        return redirect(url_for('auth.admin_login'))
    return redirect(url_for('auth.login'))
