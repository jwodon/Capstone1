import unittest
from app import app
from models import db, User, List  # Import the db instance, User, and List classes

# Set the database URI for testing
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///test_capstone1'

# Disable CSRF protection during testing
app.config['WTF_CSRF_ENABLED'] = False

class TestModels(unittest.TestCase):
    """Test database models."""

    @classmethod
    def setUpClass(cls):
        """Create all tables."""
        with app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        """Remove all tables at the end of testing."""
        with app.app_context():
            db.drop_all()

    def test_user_model(self):
        """Test User model."""
        with app.app_context():
            user = User.signup(username='testuser', password='password', profile_image_url='')
            db.session.commit()
            retrieved_user = User.query.filter_by(username='testuser').first()
            self.assertEqual(retrieved_user.username, 'testuser')



class TestRoutes(unittest.TestCase):
    """Test routes."""

    @classmethod
    def setUpClass(cls):
        """Set up the Flask application context and create all tables."""
        with app.app_context():
            cls.app = app.test_client()  # Instantiate the Flask test client

            # Create all tables
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        """Remove all tables at the end of testing."""
        with app.app_context():
            db.drop_all()

    def test_home_route(self):
        """Test home route."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_signup_route(self):
        """Test signup route."""
        response = self.app.get('/signup')
        self.assertEqual(response.status_code, 200)

    def test_login_route(self):
        """Test login route."""
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)

    def test_logout_route(self):
        """Test logout route."""
        response = self.app.get('/logout')
        self.assertEqual(response.status_code, 302)  # Redirects to login page

    def test_new_list_route(self):
        """Test new list route."""
        response = self.app.get('/new_list')
        self.assertEqual(response.status_code, 302)  # Redirects to login page

    def test_list_route(self):
        """Test list route."""
        response = self.app.get('/list/1')
        self.assertEqual(response.status_code, 404)  # Assuming no list with ID 1


if __name__ == '__main__':
    unittest.main()
