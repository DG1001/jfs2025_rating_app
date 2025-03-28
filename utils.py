import os
import logging
from datetime import datetime

def setup_logging():
    """Setup logging for rating actions."""
    # Get the log directory from config
    from flask import current_app
    log_dir = current_app.config['LOG_DIR']
    
    # Create log directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Setup rating logger
    rating_logger = logging.getLogger('rating_logger')
    rating_logger.setLevel(logging.INFO)
    
    # Check if handler already exists to avoid duplicate handlers
    if not rating_logger.handlers:
        rating_handler = logging.FileHandler(current_app.config['RATING_LOG_FILE'])
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        rating_handler.setFormatter(formatter)
        rating_logger.addHandler(rating_handler)

def log_rating(user_id, talk_id, rating, old_rating=None):
    """Log a rating action."""
    rating_logger = logging.getLogger('rating_logger')
    
    if old_rating:
        rating_logger.info(f'User {user_id} changed rating for talk {talk_id} from {old_rating} to {rating}')
    else:
        rating_logger.info(f'User {user_id} rated talk {talk_id} with {rating}')

def recover_ratings_from_log():
    """Recover ratings from log file in case of data loss."""
    from flask import current_app
    import re
    import json
    
    log_file = current_app.config['RATING_LOG_FILE']
    ratings_file = current_app.config['RATINGS_FILE']
    
    if not os.path.exists(log_file):
        return False, "Log-Datei nicht gefunden."
    
    # Initialize empty ratings dictionary
    ratings = {}
    
    # Regular expressions for parsing log entries
    rating_pattern = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - User (\w+) rated talk (\w+) with (\d+)')
    change_pattern = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - User (\w+) changed rating for talk (\w+) from (\d+) to (\d+)')
    
    # Read log file and reconstruct ratings
    with open(log_file, 'r') as f:
        for line in f:
            # Check for initial rating
            match = rating_pattern.match(line)
            if match:
                timestamp, user_id, talk_id, rating = match.groups()
                if user_id not in ratings:
                    ratings[user_id] = {}
                ratings[user_id][talk_id] = int(rating)
                continue
            
            # Check for rating change
            match = change_pattern.match(line)
            if match:
                timestamp, user_id, talk_id, old_rating, new_rating = match.groups()
                if user_id not in ratings:
                    ratings[user_id] = {}
                ratings[user_id][talk_id] = int(new_rating)
    
    # Save reconstructed ratings
    try:
        with open(ratings_file, 'w') as f:
            json.dump(ratings, f, indent=4)
        return True, f"Bewertungen erfolgreich aus Log-Datei wiederhergestellt. {sum(len(user_ratings) for user_ratings in ratings.values())} Bewertungen wiederhergestellt."
    except Exception as e:
        return False, f"Fehler beim Speichern der wiederhergestellten Bewertungen: {str(e)}"
