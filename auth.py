from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import time
import os
from models import User

auth = Blueprint('auth', __name__)

def generate_token(length=16):
    """Generate a random access token."""
    return secrets.token_hex(length)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """User login with access token."""
    if current_user.is_authenticated:
        if session.get('is_admin'):
            return redirect('/admin/')
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
        return redirect('/admin/')
    
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
            
            # Create admin dashboard template if it doesn't exist
            admin_template_dir = os.path.join(current_app.root_path, 'templates', 'admin')
            os.makedirs(admin_template_dir, exist_ok=True)
            
            dashboard_template = os.path.join(admin_template_dir, 'dashboard.html')
            if not os.path.exists(dashboard_template):
                with open(dashboard_template, 'w') as f:
                    f.write("""{% extends 'base.html' %}
{% block title %}Admin Dashboard{% endblock %}
{% block content %}
<div class="container mt-4">
    <h1>Admin Dashboard</h1>
    <div class="row">
        <div class="col-md-6">
            <div class="card mb-4">
                <div class="card-header">
                    <h5>Statistiken</h5>
                </div>
                <div class="card-body">
                    <p>Anzahl Benutzer: {{ user_count }}</p>
                    <p>Anzahl Vorträge: {{ talk_count }}</p>
                </div>
            </div>
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5>Bewertungsübersicht</h5>
                    <a href="{{ url_for('admin.export_ratings') }}" class="btn btn-sm btn-primary">Export CSV</a>
                </div>
                <div class="card-body">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Vortrag</th>
                                <th>Durchschnittliche Bewertung</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for talk_id, talk, avg_rating in sorted_talks %}
                            <tr>
                                <td>{{ talk.title }}</td>
                                <td>
                                    <div class="rating">
                                        {% for i in range(max_rating) %}
                                            {% if i < avg_rating|int %}
                                                <span class="star filled">★</span>
                                            {% elif i < avg_rating and i >= avg_rating|int %}
                                                <span class="star half-filled">★</span>
                                            {% else %}
                                                <span class="star">★</span>
                                            {% endif %}
                                        {% endfor %}
                                        <span class="rating-value">{{ "%.2f"|format(avg_rating) }}</span>
                                    </div>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h5>Aktionen</h5>
                </div>
                <div class="card-body">
                    <a href="{{ url_for('admin.manage_users') }}" class="btn btn-primary mb-2">Benutzer verwalten</a>
                    <a href="{{ url_for('main.recover_ratings') }}" class="btn btn-warning mb-2" onclick="return confirm('Sind Sie sicher? Diese Aktion wird versuchen, Bewertungen aus der Log-Datei wiederherzustellen.')">Bewertungen wiederherstellen</a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}""")
            
            # Force a direct redirect to the admin dashboard
            return redirect('/admin/')
        
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
