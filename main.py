from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
from flask_login import current_user, login_required
import json
import logging
import time
from datetime import datetime

from models import Talk, Speaker, User, Rating, Comment
from utils import setup_logging, recover_ratings_from_log

# Create blueprint
main = Blueprint('main', __name__)

# Register Jinja filters
@main.app_template_filter('strftime')
def _jinja2_filter_strftime(timestamp, format='%Y-%m-%d %H:%M:%S'):
    """Convert a Unix timestamp to a formatted date string."""
    return datetime.fromtimestamp(timestamp).strftime(format)

@main.route('/')
def index():
    """Home page route."""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    # Load talks data
    talks = Talk.get_all()
    
    # Load user's ratings if authenticated
    user_ratings = {}
    if current_user.is_authenticated:
        user_ratings = Rating.get_for_user(current_user.id)
    
    # Get all unique topics from talks
    topics = Talk.get_all_topics()
    
    # Count talks per topic
    topic_counts = Talk.count_by_topic()
    
    # Get filter parameters from request or session
    topic_filter = request.args.get('topic', session.get('topic_filter', ''))
    keyword_filter = request.args.get('keyword', session.get('keyword_filter', ''))
    rated_filter = request.args.get('rated', session.get('rated_filter', ''))  # New filter
    
    # Store filters in session
    session['topic_filter'] = topic_filter
    session['keyword_filter'] = keyword_filter
    session['rated_filter'] = rated_filter  # Store new filter
    
    # Filter talks based on parameters
    filtered_talks = talks
    if rated_filter == 'yes' and current_user.is_authenticated:
        filtered_talks = Talk.get_rated_by_user(current_user.id)
    elif rated_filter == 'no' and current_user.is_authenticated:
        filtered_talks = {k: v for k, v in talks.items() if k not in user_ratings}
    
    if topic_filter:
        filtered_talks = {k: v for k, v in filtered_talks.items() if v.get('topicId') == topic_filter}
    
    if keyword_filter:
        filtered_talks = Talk.search(keyword_filter)
        if topic_filter:
            filtered_talks = {k: v for k, v in filtered_talks.items() if v.get('topicId') == topic_filter}
        if rated_filter == 'yes' and current_user.is_authenticated:
            filtered_talks = {k: v for k, v in filtered_talks.items() if k in user_ratings}
        elif rated_filter == 'no' and current_user.is_authenticated:
            filtered_talks = {k: v for k, v in filtered_talks.items() if k not in user_ratings}
    
    return render_template('index.html', 
                        talks=filtered_talks, 
                        user_ratings=user_ratings,
                        topics=topics,
                        topic_counts=topic_counts,
                        total_talks=len(talks),
                        filtered_count=len(filtered_talks),
                        current_topic=session['topic_filter'],
                        current_keyword=session['keyword_filter'],
                        current_rated=session['rated_filter'])  # Pass new filter state

@main.route('/talk/<talk_id>')
@login_required
def talk_detail(talk_id):
    """Talk detail page route."""
    # Get talk data
    talk = Talk.get_by_id(talk_id)
    if not talk:
        flash('Vortrag nicht gefunden', 'danger')
        return redirect(url_for('main.index'))
    
    # Get speaker information (sanitized)
    speaker = None
    co_speakers = []
    
    if 'speakerId' in talk and talk['speakerId']:
        speaker = Speaker.get_sanitized(str(talk['speakerId']))
    
    if 'coSpeakerId1' in talk and talk['coSpeakerId1']:
        co_speaker = Speaker.get_sanitized(str(talk['coSpeakerId1']))
        if co_speaker:
            co_speakers.append(co_speaker)
    
    if 'coSpeakerId2' in talk and talk['coSpeakerId2']:
        co_speaker = Speaker.get_sanitized(str(talk['coSpeakerId2']))
        if co_speaker:
            co_speakers.append(co_speaker)
    
    # Get user's rating for this talk
    user_rating = Rating.get_user_rating_for_talk(current_user.id, talk_id)
    
    # Get comments for this talk
    comments = Comment.get_for_talk(talk_id)
    
    # Get all ratings for this talk with user info
    all_ratings = []
    ratings_data = Rating.get_for_talk(talk_id)
    for user_id, rating in ratings_data.items():
        user = User.get_by_id(user_id)
        all_ratings.append({
            'user_name': user.name if user else 'Unknown',
            'rating': rating
        })
    
    return render_template('talk_detail.html', 
                        talk=talk,
                        talk_id=talk_id,
                        speaker=speaker,
                        co_speakers=co_speakers,
                        user_rating=user_rating,
                        max_rating=current_app.config['MAX_RATING'],
                        comments=comments,
                        all_ratings=all_ratings)

@main.route('/rate/<talk_id>', methods=['POST'])
@login_required
def rate_talk(talk_id):
    """Rate a talk."""
    rating = request.form.get('rating', type=int)
    
    # Validate rating
    if not rating or rating < 1 or rating > current_app.config['MAX_RATING']:
        flash(f'Ungültige Bewertung. Bitte wählen Sie 1-{current_app.config["MAX_RATING"]} Sterne.', 'danger')
        return redirect(url_for('main.talk_detail', talk_id=talk_id))
    
    # Set the rating
    success, message = Rating.set_rating(current_user.id, talk_id, rating)
    
    if success:
        flash(f'Bewertung erfolgreich gespeichert!', 'success')
    else:
        flash(message, 'danger')
        
    return redirect(url_for('main.talk_detail', talk_id=talk_id))

@main.route('/comment/<talk_id>', methods=['POST'])
@login_required
def add_comment(talk_id):
    """Add a comment to a talk."""
    comment_text = request.form.get('comment', '')
    
    # Add the comment
    success, message = Comment.add_comment(talk_id, current_user.id, current_user.name, comment_text)
    
    if success:
        flash('Kommentar erfolgreich hinzugefügt!', 'success')
    else:
        flash(message, 'danger')
        
    return redirect(url_for('main.talk_detail', talk_id=talk_id))

@main.route('/recover-ratings', methods=['POST'])
@login_required
def recover_ratings():
    """Recover ratings from log file."""
    if not session.get('is_admin'):
        flash('Nur Administratoren können diese Funktion nutzen.', 'danger')
        return redirect(url_for('main.index'))
    
    success, message = recover_ratings_from_log()
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
        
    return redirect(url_for('admin.dashboard'))

@main.route('/random-talk')
@login_required
def random_talk():
    """Get a random unrated talk."""
    # Get all talks
    talks = Talk.get_all()
    
    # Get user's ratings
    user_ratings = Rating.get_for_user(current_user.id)
    
    # Filter out talks that the user has already rated
    unrated_talks = {talk_id: talk for talk_id, talk in talks.items() 
                    if talk_id not in user_ratings}
    
    # If all talks are rated, just return any random talk
    if not unrated_talks:
        unrated_talks = talks
    
    # Select a random talk
    import random
    if unrated_talks:
        random_talk_id = random.choice(list(unrated_talks.keys()))
        return redirect(url_for('main.talk_detail', talk_id=random_talk_id))
    
    # If no talks found
    flash('Keine Vorträge gefunden.', 'warning')
    return redirect(url_for('main.index'))

def init_app(app):
    """Initialize the main blueprint with the app."""
    # Setup logging
    with app.app_context():
        setup_logging()
    
    # Register the blueprint
    app.register_blueprint(main)
    
    # Register Jinja filters
    @app.template_filter('strftime')
    def _jinja2_filter_strftime(timestamp, format='%Y-%m-%d %H:%M:%S'):
        """Convert a Unix timestamp to a formatted date string."""
        return datetime.fromtimestamp(timestamp).strftime(format)
