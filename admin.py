from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session, send_file
from flask_login import login_required, current_user
import json
import os
import csv
import io
import time
from datetime import datetime
from auth import generate_token, User

admin = Blueprint('admin', __name__)

@admin.route('/')
def dashboard():
    """Admin dashboard."""
    # Admin check is now handled by the before_request in app.py
    
    # Load users data
    users = {}
    try:
        with open(current_app.config['USERS_FILE'], 'r') as f:
            users = json.load(f)
    except Exception as e:
        flash(f'Fehler beim Laden der Benutzerdaten: {str(e)}', 'danger')
    
    # Load talks data
    talks = {}
    try:
        with open(current_app.config['TALKS_FILE'], 'r') as f:
            talks = json.load(f)
    except Exception as e:
        flash(f'Fehler beim Laden der Vorträge: {str(e)}', 'danger')
    
    # Load ratings data
    ratings = {}
    try:
        with open(current_app.config['RATINGS_FILE'], 'r') as f:
            ratings = json.load(f)
    except Exception as e:
        flash(f'Fehler beim Laden der Bewertungen: {str(e)}', 'danger')
    
    # Calculate average ratings for each talk
    avg_ratings = {}
    for talk_id in talks:
        ratings_for_talk = []
        for user_ratings in ratings.values():
            if talk_id in user_ratings:
                ratings_for_talk.append(user_ratings[talk_id])
        
        if ratings_for_talk:
            avg_ratings[talk_id] = sum(ratings_for_talk) / len(ratings_for_talk)
        else:
            avg_ratings[talk_id] = 0
    
    # Sort talks by average rating (descending)
    sorted_talks = sorted(
        [(talk_id, talks[talk_id], avg_ratings.get(talk_id, 0)) for talk_id in talks],
        key=lambda x: x[2],
        reverse=True
    )
    
    return render_template('admin/dashboard.html', 
                          users=users,
                          sorted_talks=sorted_talks,
                          user_count=len(users),
                          talk_count=len(talks),
                          max_rating=current_app.config['MAX_RATING'])

@admin.route('/users')
def manage_users():
    """User management page."""
    # Admin check is now handled by the before_request in app.py
    
    # Load users data
    users = {}
    try:
        with open(current_app.config['USERS_FILE'], 'r') as f:
            users = json.load(f)
    except Exception as e:
        flash(f'Fehler beim Laden der Benutzerdaten: {str(e)}', 'danger')
    
    return render_template('admin/users.html', users=users)

@admin.route('/users/add', methods=['POST'])
def add_user():
    """Add a new user."""
    # Admin check is now handled by the before_request in app.py
    
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    
    if not name or not email:
        flash('Bitte geben Sie Name und E-Mail-Adresse ein.', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    # Load current users
    users = {}
    try:
        with open(current_app.config['USERS_FILE'], 'r') as f:
            users = json.load(f)
    except Exception as e:
        flash(f'Fehler beim Laden der Benutzerdaten: {str(e)}', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    # Check if email already exists
    for user_data in users.values():
        if user_data.get('email') == email:
            flash(f'Ein Benutzer mit der E-Mail-Adresse {email} existiert bereits.', 'danger')
            return redirect(url_for('admin.manage_users'))
    
    # Generate user ID and token
    user_id = f"user_{int(time.time())}_{len(users) + 1}"
    token = generate_token()
    
    # Add new user
    users[user_id] = {
        'name': name,
        'email': email,
        'token': token,
        'created_at': datetime.now().isoformat()
    }
    
    # Save updated users
    try:
        with open(current_app.config['USERS_FILE'], 'w') as f:
            json.dump(users, f, indent=4)
    except Exception as e:
        flash(f'Fehler beim Speichern des Benutzers: {str(e)}', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    flash(f'Benutzer {name} erfolgreich hinzugefügt. Access-Token: {token}', 'success')
    return redirect(url_for('admin.manage_users'))

@admin.route('/users/regenerate-token/<user_id>', methods=['POST'])
def regenerate_token(user_id):
    """Regenerate access token for a user."""
    # Admin check is now handled by the before_request in app.py
    
    # Load current users
    users = {}
    try:
        with open(current_app.config['USERS_FILE'], 'r') as f:
            users = json.load(f)
    except Exception as e:
        flash(f'Fehler beim Laden der Benutzerdaten: {str(e)}', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    # Check if user exists
    if user_id not in users:
        flash('Benutzer nicht gefunden.', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    # Generate new token
    new_token = generate_token()
    users[user_id]['token'] = new_token
    
    # Save updated users
    try:
        with open(current_app.config['USERS_FILE'], 'w') as f:
            json.dump(users, f, indent=4)
    except Exception as e:
        flash(f'Fehler beim Speichern des neuen Tokens: {str(e)}', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    flash(f'Neues Access-Token für {users[user_id]["name"]} generiert: {new_token}', 'success')
    return redirect(url_for('admin.manage_users'))

@admin.route('/users/delete/<user_id>', methods=['POST'])
def delete_user(user_id):
    """Delete a user."""
    # Admin check is now handled by the before_request in app.py
    
    # Load current users
    users = {}
    try:
        with open(current_app.config['USERS_FILE'], 'r') as f:
            users = json.load(f)
    except Exception as e:
        flash(f'Fehler beim Laden der Benutzerdaten: {str(e)}', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    # Check if user exists
    if user_id not in users:
        flash('Benutzer nicht gefunden.', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    user_name = users[user_id]['name']
    
    # Delete user
    del users[user_id]
    
    # Save updated users
    try:
        with open(current_app.config['USERS_FILE'], 'w') as f:
            json.dump(users, f, indent=4)
    except Exception as e:
        flash(f'Fehler beim Löschen des Benutzers: {str(e)}', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    # Also remove user's ratings
    try:
        with open(current_app.config['RATINGS_FILE'], 'r') as f:
            ratings = json.load(f)
            if user_id in ratings:
                del ratings[user_id]
        
        with open(current_app.config['RATINGS_FILE'], 'w') as f:
            json.dump(ratings, f, indent=4)
    except Exception as e:
        flash(f'Fehler beim Löschen der Bewertungen des Benutzers: {str(e)}', 'warning')
    
    flash(f'Benutzer {user_name} erfolgreich gelöscht.', 'success')
    return redirect(url_for('admin.manage_users'))

@admin.route('/ratings-matrix')
def ratings_matrix():
    """Show matrix of all ratings with talks as rows and users as columns."""
    # Load all data
    talks = {}
    users = {}
    speakers = {}
    ratings = {}
    
    try:
        with open(current_app.config['TALKS_FILE'], 'r') as f:
            talks = json.load(f)
        with open(current_app.config['USERS_FILE'], 'r') as f:
            users = json.load(f)
        with open(current_app.config['SPEAKERS_FILE'], 'r') as f:
            speakers = json.load(f)
        with open(current_app.config['RATINGS_FILE'], 'r') as f:
            ratings = json.load(f)
    except Exception as e:
        flash(f'Error loading data: {str(e)}', 'danger')
        return redirect(url_for('admin.dashboard'))

    # Prepare talk data with speaker names
    talk_data = []
    for talk_id, talk in talks.items():
        speaker_name = ""
        if 'speakerId' in talk and talk['speakerId']:
            speaker = speakers.get(str(talk['speakerId']))
            if speaker:
                speaker_name = f"{speaker.get('firstName', '')} {speaker.get('surName', '')}"
        
        talk_data.append({
            'id': talk_id,
            'title': talk.get('title', ''),
            'speaker': speaker_name,
            'ratings': {}
        })

    # Add ratings for each user
    for user_id in users:
        user_ratings = ratings.get(user_id, {})
        for talk in talk_data:
            talk['ratings'][user_id] = user_ratings.get(talk['id'])

    return render_template('admin/ratings_matrix.html',
                         talks=talk_data,
                         users=users,
                         max_rating=current_app.config['MAX_RATING'])

@admin.route('/export-ratings')
def export_ratings():
    """Export ratings as CSV file."""
    # Admin check is now handled by the before_request in app.py
    
    # Load talks data
    talks = {}
    try:
        with open(current_app.config['TALKS_FILE'], 'r') as f:
            talks = json.load(f)
    except Exception as e:
        flash(f'Fehler beim Laden der Vorträge: {str(e)}', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    # Load ratings data
    ratings = {}
    try:
        with open(current_app.config['RATINGS_FILE'], 'r') as f:
            ratings = json.load(f)
    except Exception as e:
        flash(f'Fehler beim Laden der Bewertungen: {str(e)}', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    # Load users data
    users = {}
    try:
        with open(current_app.config['USERS_FILE'], 'r') as f:
            users = json.load(f)
    except Exception as e:
        flash(f'Fehler beim Laden der Benutzerdaten: {str(e)}', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    # Calculate average ratings for each talk
    avg_ratings = {}
    for talk_id in talks:
        ratings_for_talk = []
        for user_ratings in ratings.values():
            if talk_id in user_ratings:
                ratings_for_talk.append(user_ratings[talk_id])
        
        if ratings_for_talk:
            avg_ratings[talk_id] = sum(ratings_for_talk) / len(ratings_for_talk)
        else:
            avg_ratings[talk_id] = 0
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Talk ID', 'Booking Number', 'Title', 'Topic', 'Average Rating', 'Number of Ratings'])
    
    # Write data rows
    for talk_id, talk_data in talks.items():
        # Count ratings for this talk
        rating_count = sum(1 for user_ratings in ratings.values() if talk_id in user_ratings)
        
        writer.writerow([
            talk_id,
            talk_data.get('bookingNumber', ''),
            talk_data.get('title', ''),
            talk_data.get('topicId', ''),
            f"{avg_ratings.get(talk_id, 0):.2f}",
            rating_count
        ])
    
    # Prepare response
    output.seek(0)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create a BytesIO object from the StringIO
    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8'))
    mem.seek(0)
    output.close()
    
    return send_file(
        mem,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'jfs2025_ratings_export_{timestamp}.csv'
    )
