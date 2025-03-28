import unittest
import os
import json
import tempfile
import shutil
from app import create_app
from models import Talk, Speaker, User, Rating, Comment

class TestJFSRatingApp(unittest.TestCase):
    """Test cases for the JFS 2025 Rating App."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        
        # Configure app for testing
        self.app = create_app('development')
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        
        # Override data file paths to use temporary directory
        self.app.config['TALKS_FILE'] = os.path.join(self.test_dir, 'talks.json')
        self.app.config['SPEAKERS_FILE'] = os.path.join(self.test_dir, 'speakers.json')
        self.app.config['USERS_FILE'] = os.path.join(self.test_dir, 'users.json')
        self.app.config['RATINGS_FILE'] = os.path.join(self.test_dir, 'ratings.json')
        self.app.config['COMMENTS_FILE'] = os.path.join(self.test_dir, 'comments.json')
        self.app.config['LOG_DIR'] = os.path.join(self.test_dir, 'logs')
        self.app.config['RATING_LOG_FILE'] = os.path.join(self.app.config['LOG_DIR'], 'ratings.log')
        
        # Create test client
        self.client = self.app.test_client()
        
        # Create test data
        self._create_test_data()
        
        # Create application context
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()
        shutil.rmtree(self.test_dir)
    
    def _create_test_data(self):
        """Create test data for the tests."""
        # Create directories
        os.makedirs(self.app.config['LOG_DIR'], exist_ok=True)
        
        # Create test talks
        talks = {
            "1": {
                "bookingNumber": "TX-001",
                "id": 1,
                "title": "Test Talk 1",
                "abstract": "This is a test talk abstract.",
                "topicId": "Java",
                "keywords": "test,java",
                "speakerId": 101
            },
            "2": {
                "bookingNumber": "TX-002",
                "id": 2,
                "title": "Test Talk 2",
                "abstract": "This is another test talk abstract.",
                "topicId": "Spring",
                "keywords": "test,spring",
                "speakerId": 102
            }
        }
        
        # Create test speakers
        speakers = {
            "101": {
                "id": 101,
                "firstName": "John",
                "surName": "Doe",
                "company": "Test Company",
                "phone": "+1234567890",
                "eMail": "john@example.com",
                "address": "123 Test St",
                "bio": "Test bio for John Doe"
            },
            "102": {
                "id": 102,
                "firstName": "Jane",
                "surName": "Smith",
                "company": "Another Company",
                "phone": "+0987654321",
                "eMail": "jane@example.com",
                "address": "456 Test Ave",
                "bio": "Test bio for Jane Smith"
            }
        }
        
        # Create test users
        users = {
            "user1": {
                "name": "Test User",
                "email": "user@example.com",
                "token": "test_token_123",
                "created_at": "2025-03-01T12:00:00"
            }
        }
        
        # Write test data to files
        with open(self.app.config['TALKS_FILE'], 'w') as f:
            json.dump(talks, f)
        
        with open(self.app.config['SPEAKERS_FILE'], 'w') as f:
            json.dump(speakers, f)
        
        with open(self.app.config['USERS_FILE'], 'w') as f:
            json.dump(users, f)
        
        with open(self.app.config['RATINGS_FILE'], 'w') as f:
            json.dump({}, f)
        
        with open(self.app.config['COMMENTS_FILE'], 'w') as f:
            json.dump({}, f)
    
    def test_talk_model(self):
        """Test Talk model functionality."""
        # Test get_all
        talks = Talk.get_all()
        self.assertEqual(len(talks), 2)
        
        # Test get_by_id
        talk = Talk.get_by_id("1")
        self.assertEqual(talk['title'], "Test Talk 1")
        
        # Test get_by_topic
        java_talks = Talk.get_by_topic("Java")
        self.assertEqual(len(java_talks), 1)
        self.assertEqual(list(java_talks.values())[0]['title'], "Test Talk 1")
        
        # Test search
        search_results = Talk.search("spring")
        self.assertEqual(len(search_results), 1)
        self.assertEqual(list(search_results.values())[0]['title'], "Test Talk 2")
        
        # Test get_all_topics
        topics = Talk.get_all_topics()
        self.assertEqual(set(topics), {"Java", "Spring"})
    
    def test_speaker_model(self):
        """Test Speaker model functionality."""
        # Test get_all
        speakers = Speaker.get_all()
        self.assertEqual(len(speakers), 2)
        
        # Test get_by_id
        speaker = Speaker.get_by_id("101")
        self.assertEqual(speaker['firstName'], "John")
        
        # Test get_sanitized (should not include sensitive information)
        sanitized = Speaker.get_sanitized("101")
        self.assertNotIn('phone', sanitized)
        self.assertNotIn('eMail', sanitized)
        self.assertNotIn('address', sanitized)
    
    def test_user_model(self):
        """Test User model functionality."""
        # Test get_by_id
        user = User.get_by_id("user1")
        self.assertEqual(user.name, "Test User")
        
        # Test get_by_token
        user = User.get_by_token("test_token_123")
        self.assertEqual(user.id, "user1")
        
        # Test create
        user, token = User.create("New User", "new@example.com")
        self.assertIsNotNone(user)
        self.assertEqual(user.name, "New User")
        
        # Test regenerate_token
        new_token, error = User.regenerate_token(user.id)
        self.assertIsNotNone(new_token)
        self.assertIsNone(error)
        
        # Test delete
        success, error = User.delete(user.id)
        self.assertTrue(success)
        self.assertIsNone(error)
    
    def test_rating_model(self):
        """Test Rating model functionality."""
        # Test set_rating
        success, error = Rating.set_rating("user1", "1", 5)
        self.assertTrue(success)
        self.assertIsNone(error)
        
        # Test get_user_rating_for_talk
        rating = Rating.get_user_rating_for_talk("user1", "1")
        self.assertEqual(rating, 5)
        
        # Test get_for_talk
        ratings = Rating.get_for_talk("1")
        self.assertEqual(len(ratings), 1)
        self.assertEqual(ratings["user1"], 5)
        
        # Test get_average_ratings
        avg_ratings = Rating.get_average_ratings()
        self.assertEqual(avg_ratings["1"], 5)
    
    def test_comment_model(self):
        """Test Comment model functionality."""
        # Test add_comment
        success, error = Comment.add_comment("1", "user1", "Test User", "This is a test comment")
        self.assertTrue(success)
        self.assertIsNone(error)
        
        # Test get_for_talk
        comments = Comment.get_for_talk("1")
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0]['text'], "This is a test comment")
    
    def test_login_page(self):
        """Test login page."""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Access Token', response.data)
    
    def test_admin_login_page(self):
        """Test admin login page."""
        response = self.client.get('/admin-login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Administrator Login', response.data)

if __name__ == '__main__':
    unittest.main()
