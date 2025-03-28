import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-development-only'
    
    # Admin credentials from environment variables
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or 'admin'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'admin'
    
    # Data directory
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    
    # File paths for data storage
    TALKS_FILE = os.path.join(DATA_DIR, 'talks.json')
    SPEAKERS_FILE = os.path.join(DATA_DIR, 'speakers.json')
    USERS_FILE = os.path.join(DATA_DIR, 'users.json')
    RATINGS_FILE = os.path.join(DATA_DIR, 'ratings.json')
    COMMENTS_FILE = os.path.join(DATA_DIR, 'comments.json')
    
    # Logging configuration
    LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    RATING_LOG_FILE = os.path.join(LOG_DIR, 'ratings.log')
    
    # Session configuration
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_FILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'sessions')
    
    # Application settings
    MAX_RATING = 5  # Maximum rating value (5 stars)
    
    @staticmethod
    def init_app(app):
        """Initialize application with this configuration."""
        # Create necessary directories if they don't exist
        os.makedirs(os.path.dirname(Config.TALKS_FILE), exist_ok=True)
        os.makedirs(os.path.dirname(Config.RATING_LOG_FILE), exist_ok=True)
        os.makedirs(Config.SESSION_FILE_DIR, exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    
    # In production, SECRET_KEY must be set in environment
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        assert os.environ.get('SECRET_KEY'), 'SECRET_KEY environment variable must be set in production'
        assert os.environ.get('ADMIN_USERNAME'), 'ADMIN_USERNAME environment variable must be set in production'
        assert os.environ.get('ADMIN_PASSWORD'), 'ADMIN_PASSWORD environment variable must be set in production'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
