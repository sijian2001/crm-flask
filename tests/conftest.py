import pytest
import tempfile
import os
from app import create_app
from models import db, User
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

@pytest.fixture
def authenticated_client(client, test_user):
    """認証済みテストクライアント"""
    client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'TestPassword123'
    })
    return client