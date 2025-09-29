"""
Test configuration and fixtures for CRM application tests
"""
import pytest
import tempfile
import os
from app import create_app
from models import db, User, Customer, Product, Category
from config import Config


class TestConfig(Config):
    """Test configuration with in-memory database"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'
    LOG_LEVEL = 'ERROR'


@pytest.fixture(scope='session')
def app():
    """Create application for testing"""
    # Create test app with test configuration
    app = create_app()
    app.config.from_object(TestConfig)

    with app.app_context():
        yield app


@pytest.fixture(scope='function')
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Create database session for testing"""
    with app.app_context():
        db.create_all()
        yield db.session
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_user(db_session):
    """Create sample user for testing"""
    user = User(
        username='testuser',
        email='test@example.com',
        password='testpassword123'
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def sample_customer(db_session):
    """Create sample customer for testing"""
    customer = Customer(
        first_name='太郎',
        last_name='田中',
        email='tanaka@example.com',
        phone='090-1234-5678',
        company='テスト株式会社'
    )
    db_session.add(customer)
    db_session.commit()
    return customer


@pytest.fixture
def sample_category(db_session):
    """Create sample category for testing"""
    category = Category(
        name='テストカテゴリ',
        description='テスト用のカテゴリです'
    )
    db_session.add(category)
    db_session.commit()
    return category


@pytest.fixture
def sample_product(db_session, sample_category):
    """Create sample product for testing"""
    product = Product(
        name='テスト製品',
        sku='TEST-001',
        price=1000.00,
        category_id=sample_category.id,
        description='テスト用の製品です',
        cost=800.00,
        stock_quantity=100,
        min_stock_level=10
    )
    db_session.add(product)
    db_session.commit()
    return product


@pytest.fixture
def authenticated_client(client, sample_user):
    """Create authenticated test client"""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(sample_user.id)
        sess['_fresh'] = True
    return client