import pytest
from app import create_app, db
from app.models import User, Listing, Report
from werkzeug.security import generate_password_hash


class TestConfig:
    SECRET_KEY = 'test-secret'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True
    WTF_CSRF_ENABLED = False
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    UPLOAD_FOLDER = '/tmp/test-uploads'
    SSO_ALLOWED_EMAIL_DOMAINS = ['uwa.edu.au', 'student.uwa.edu.au']


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def regular_user(app):
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('password123'),
        )
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def admin_user(app):
    with app.app_context():
        user = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('password123'),
            is_admin=True,
        )
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def moderator_user(app):
    with app.app_context():
        user = User(
            username='moderator',
            email='mod@example.com',
            password_hash=generate_password_hash('password123'),
            is_moderator=True,
        )
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def sample_listing(app, regular_user):
    with app.app_context():
        listing = Listing(
            title='Test Textbook',
            description='A test listing',
            price=25.0,
            category='books',
            seller_id=regular_user,
        )
        db.session.add(listing)
        db.session.commit()
        return listing.id


def login(client, email, password='password123'):
    return client.post('/auth/login', data={
        'email': email,
        'password': password,
    }, follow_redirects=True)
