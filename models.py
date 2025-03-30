import json
import os
import time
import logging
from datetime import datetime
from flask import current_app
from flask_login import UserMixin

class JSONStorageModel:
    """Base class for models that are stored in JSON files."""
    
    @classmethod
    def get_file_path(cls):
        """Get the file path for the model's JSON storage."""
        raise NotImplementedError("Subclasses must implement get_file_path")
    
    @classmethod
    def load_all(cls):
        """Load all items from the JSON file."""
        try:
            file_path = cls.get_file_path()
            if not os.path.exists(file_path):
                return {}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading data from {file_path}: {str(e)}")
            return {}
    
    @classmethod
    def save_all(cls, data):
        """Save all items to the JSON file."""
        try:
            file_path = cls.get_file_path()
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            logging.error(f"Error saving data to {file_path}: {str(e)}")
            return False


class Talk(JSONStorageModel):
    """Model for conference talks."""
    
    @classmethod
    def get_file_path(cls):
        return current_app.config['TALKS_FILE']
    
    @classmethod
    def get_by_id(cls, talk_id):
        """Get a talk by ID."""
        talks = cls.load_all()
        return talks.get(str(talk_id))
    
    @classmethod
    def get_all(cls):
        """Get all talks."""
        return cls.load_all()
    
    @classmethod
    def get_by_topic(cls, topic_id):
        """Get all talks for a specific topic."""
        talks = cls.load_all()
        return {k: v for k, v in talks.items() if v.get('topicId') == topic_id}
    
    @classmethod
    def search(cls, keyword=None, abstract=None):
        """Search talks by keyword in title/abstract/keywords and/or abstract text."""
        talks = cls.load_all()
        
        # Prepare search terms
        keyword = keyword.lower() if keyword else None
        abstract = abstract.lower() if abstract else None
        
        filtered = {}
        for talk_id, talk in talks.items():
            matches = True
            
            # Keyword search (title, abstract or keywords)
            if keyword:
                matches = (keyword in talk.get('title', '').lower() or 
                         keyword in talk.get('abstract', '').lower() or 
                         keyword in talk.get('keywords', '').lower())
            
            # Additional abstract search if keyword matched or no keyword search
            if matches and abstract:
                matches = abstract in talk.get('abstract', '').lower()
            
            if matches:
                filtered[talk_id] = talk
        
        return filtered
    
    @classmethod
    def get_all_topics(cls):
        """Get all unique topics from talks."""
        talks = cls.load_all()
        topics = set()
        for talk in talks.values():
            if 'topicId' in talk and talk['topicId']:
                topics.add(talk['topicId'])
        return sorted(topics)
    
    @classmethod
    def count_by_topic(cls):
        """Count talks per topic."""
        talks = cls.load_all()
        topics = cls.get_all_topics()
        
        counts = {}
        for topic in topics:
            counts[topic] = sum(1 for talk in talks.values() if talk.get('topicId') == topic)
        
        return counts

    @classmethod
    def get_rated_by_user(cls, user_id):
        """Get all talks rated by a specific user."""
        talks = cls.load_all()
        ratings = Rating.get_for_user(user_id)
        return {talk_id: talk for talk_id, talk in talks.items() if talk_id in ratings}


class Speaker(JSONStorageModel):
    """Model for conference speakers."""
    
    @classmethod
    def get_file_path(cls):
        return current_app.config['SPEAKERS_FILE']
    
    @classmethod
    def get_by_id(cls, speaker_id):
        """Get a speaker by ID."""
        speakers = cls.load_all()
        return speakers.get(str(speaker_id))
    
    @classmethod
    def get_all(cls):
        """Get all speakers."""
        return cls.load_all()
    
    @classmethod
    def get_sanitized(cls, speaker_id):
        """Get a speaker with sensitive information removed."""
        speaker = cls.get_by_id(speaker_id)
        if not speaker:
            return None
        
        # Create a copy to avoid modifying the original
        sanitized = speaker.copy()
        
        # Remove sensitive information
        sensitive_fields = ['phone', 'eMail', 'address', 'zipCode']
        for field in sensitive_fields:
            if field in sanitized:
                del sanitized[field]
        
        return sanitized


class User(UserMixin, JSONStorageModel):
    """Model for application users."""
    
    def __init__(self, id, name, email, token):
        self.id = id
        self.name = name
        self.email = email
        self.token = token
    
    @classmethod
    def get_file_path(cls):
        return current_app.config['USERS_FILE']
    
    @classmethod
    def get_by_id(cls, user_id):
        """Get a user by ID."""
        users = cls.load_all()
        if user_id in users:
            user_data = users[user_id]
            return cls(
                id=user_id,
                name=user_data.get('name', ''),
                email=user_data.get('email', ''),
                token=user_data.get('token', '')
            )
        return None
    
    @classmethod
    def get_by_token(cls, token):
        """Get a user by access token with security checks."""
        if not token or len(token) < 16:  # Basic token length check
            logging.warning(f"Invalid token format: {token}")
            return None
            
        users = cls.load_all()
        for user_id, user_data in users.items():
            if user_data.get('token') == token:
                # Check if token is expired (if we implement expiration)
                if 'token_expires' in user_data and user_data['token_expires'] < time.time():
                    logging.warning(f"Expired token attempt for user {user_id}")
                    return None
                    
                return cls(
                    id=user_id,
                    name=user_data.get('name', ''),
                    email=user_data.get('email', ''),
                    token=token
                )
        logging.warning(f"Invalid token attempt: {token}")
        return None
    
    @classmethod
    def create(cls, name, email):
        """Create a new user."""
        users = cls.load_all()
        
        # Check if email already exists
        for user_data in users.values():
            if user_data.get('email') == email:
                return None, "Ein Benutzer mit dieser E-Mail-Adresse existiert bereits."
        
        # Generate user ID and token
        from auth import generate_token
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
        if cls.save_all(users):
            return cls(
                id=user_id,
                name=name,
                email=email,
                token=token
            ), token
        
        return None, "Fehler beim Speichern des Benutzers."
    
    @classmethod
    def regenerate_token(cls, user_id):
        """Regenerate access token for a user."""
        users = cls.load_all()
        
        if user_id not in users:
            return None, "Benutzer nicht gefunden."
        
        # Generate new token
        from auth import generate_token
        new_token = generate_token()
        users[user_id]['token'] = new_token
        
        # Save updated users
        if cls.save_all(users):
            return new_token, None
        
        return None, "Fehler beim Speichern des neuen Tokens."
    
    @classmethod
    def delete(cls, user_id):
        """Delete a user."""
        users = cls.load_all()
        
        if user_id not in users:
            return False, "Benutzer nicht gefunden."
        
        # Delete user
        del users[user_id]
        
        # Save updated users
        if not cls.save_all(users):
            return False, "Fehler beim Löschen des Benutzers."
        
        # Also remove user's ratings
        from .rating import Rating
        Rating.delete_for_user(user_id)
        
        return True, None


class Rating(JSONStorageModel):
    """Model for talk ratings."""
    
    @classmethod
    def get_file_path(cls):
        return current_app.config['RATINGS_FILE']
    
    @classmethod
    def get_for_user(cls, user_id):
        """Get all ratings for a specific user."""
        ratings = cls.load_all()
        return ratings.get(user_id, {})
    
    @classmethod
    def get_for_talk(cls, talk_id):
        """Get all ratings for a specific talk."""
        ratings = cls.load_all()
        talk_ratings = {}
        
        for user_id, user_ratings in ratings.items():
            if talk_id in user_ratings:
                talk_ratings[user_id] = user_ratings[talk_id]
        
        return talk_ratings
    
    @classmethod
    def get_user_rating_for_talk(cls, user_id, talk_id):
        """Get a user's rating for a specific talk."""
        user_ratings = cls.get_for_user(user_id)
        return user_ratings.get(talk_id, 0)
    
    @classmethod
    def set_rating(cls, user_id, talk_id, rating_value):
        """Set a user's rating for a talk."""
        if rating_value < 1 or rating_value > current_app.config['MAX_RATING']:
            return False, f"Ungültige Bewertung. Bitte wählen Sie 1-{current_app.config['MAX_RATING']} Sterne."
        
        ratings = cls.load_all()
        
        # Initialize user ratings if not exists
        if user_id not in ratings:
            ratings[user_id] = {}
        
        # Get old rating for logging
        old_rating = ratings[user_id].get(talk_id)
        
        # Set new rating
        ratings[user_id][talk_id] = rating_value
        
        # Save updated ratings
        if not cls.save_all(ratings):
            return False, "Fehler beim Speichern der Bewertung."
        
        # Log the rating action
        from utils import log_rating
        log_rating(user_id, talk_id, rating_value, old_rating)
        
        return True, None
    
    @classmethod
    def delete_for_user(cls, user_id):
        """Delete all ratings for a user."""
        ratings = cls.load_all()
        
        if user_id in ratings:
            del ratings[user_id]
            return cls.save_all(ratings)
        
        return True
    
    @classmethod
    def get_average_ratings(cls):
        """Calculate average ratings for all talks."""
        ratings = cls.load_all()
        avg_ratings = {}
        
        # Get all talk IDs from ratings
        all_talk_ids = set()
        for user_ratings in ratings.values():
            all_talk_ids.update(user_ratings.keys())
        
        # Calculate average for each talk
        for talk_id in all_talk_ids:
            talk_ratings = []
            for user_ratings in ratings.values():
                if talk_id in user_ratings:
                    talk_ratings.append(user_ratings[talk_id])
            
            if talk_ratings:
                avg_ratings[talk_id] = sum(talk_ratings) / len(talk_ratings)
            else:
                avg_ratings[talk_id] = 0
        
        return avg_ratings


class Comment(JSONStorageModel):
    """Model for talk comments."""
    
    @classmethod
    def get_file_path(cls):
        return current_app.config['COMMENTS_FILE']
    
    @classmethod
    def get_for_talk(cls, talk_id):
        """Get all comments for a specific talk."""
        comments = cls.load_all()
        return comments.get(talk_id, [])
    
    @classmethod
    def add_comment(cls, talk_id, user_id, user_name, text):
        """Add a comment to a talk."""
        if not text.strip():
            return False, "Bitte geben Sie einen Kommentar ein."
            
        # Check comment length
        if len(text) > 200:
            return False, "Kommentar darf maximal 200 Zeichen lang sein."
        
        comments = cls.load_all()
        
        # Initialize talk comments if not exists
        if talk_id not in comments:
            comments[talk_id] = []
        
        # Add new comment
        comments[talk_id].append({
            'user_id': user_id,
            'user_name': user_name,
            'text': text,
            'timestamp': time.time()
        })
        
        # Save updated comments
        if cls.save_all(comments):
            return True, None
        
        return False, "Fehler beim Speichern des Kommentars."
