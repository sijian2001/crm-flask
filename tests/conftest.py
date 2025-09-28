import pytest
import tempfile
import os
from app import create_app
from models import db, User, Customer, Product, Category
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret-key'
    WTF_CSRF_ENABLED = False  # CSRF無効（テスト用）

@pytest.fixture
def app():
    """テスト用Flaskアプリケーション"""
    app = create_app()
    app.config.from_object(TestConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """テスト用クライアント"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """テスト用CLIランナー"""
    return app.test_cli_runner()

@pytest.fixture
def test_user(app):
    """テスト用ユーザー"""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password='TestPassword123'
        )
        db.session.add(user)
        db.session.commit()
        return user

class AuthActions:
    """Helper class for authentication actions in tests"""

    def __init__(self, client):
        self._client = client
        self._user = None

    def login(self, username='testuser', password='TestPassword123'):
        """Login with test user"""
        return self._client.post('/auth/login', data={
            'username': username,
            'password': password,
            'submit': 'Submit'
        })

    def logout(self):
        """Logout current user"""
        return self._client.get('/auth/logout')

    def create_user(self, username='testuser', email='test@example.com', password='TestPassword123'):
        """Create and return a test user"""
        with self._client.application.app_context():
            user = User(username=username, email=email, password=password)
            db.session.add(user)
            db.session.commit()
            self._user = user
            return user


@pytest.fixture
def authenticated_client(client, test_user):
    """認証済みテストクライアント"""
    client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'TestPassword123'
    })
    return client


@pytest.fixture
def auth_user(client):
    """Create authenticated user for tests"""
    auth = AuthActions(client)
    auth.create_user()
    return auth


@pytest.fixture
def sample_category(app):
    """Create a sample category for tests"""
    with app.app_context():
        category = Category(name='Electronics', description='Electronic devices')
        db.session.add(category)
        db.session.commit()
        return category


@pytest.fixture
def sample_product(app, sample_category):
    """Create a sample product for tests"""
    with app.app_context():
        product = Product(
            name='Test Product',
            sku='TEST-001',
            price=99.99,
            category_id=sample_category.id,
            description='A test product',
            stock_quantity=10,
            min_stock_level=5
        )
        db.session.add(product)
        db.session.commit()
        return product