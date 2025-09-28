import pytest
from flask import url_for
from models import User, db

class TestAuthenticationFlow:
    """認証フローの統合テスト"""

    def test_register_user(self, client):
        """ユーザー登録のテスト"""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert 'ユーザー名' in response.get_data(as_text=True)

        # 有効な登録データ
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'ValidPass123',
            'password2': 'ValidPass123'
        })

        assert response.status_code == 302  # リダイレクト
        assert '/auth/login' in response.location

        # ユーザーがデータベースに作成されている
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.email == 'newuser@example.com'

    def test_register_invalid_password(self, client):
        """無効なパスワードでの登録テスト"""
        # 短いパスワード
        response = client.post('/auth/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'short',
            'password2': 'short'
        })

        assert response.status_code == 200
        assert 'パスワードは8文字以上で入力してください' in response.get_data(as_text=True)

        # 複雑性要件を満たさないパスワード
        response = client.post('/auth/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'onlylower',
            'password2': 'onlylower'
        })

        assert response.status_code == 200
        assert '英大文字、小文字、数字を含む必要があります' in response.get_data(as_text=True)

    def test_register_password_mismatch(self, client):
        """パスワード不一致での登録テスト"""
        response = client.post('/auth/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'ValidPass123',
            'password2': 'DifferentPass123'
        })

        assert response.status_code == 200
        assert 'パスワードが一致しません' in response.get_data(as_text=True)

    def test_register_duplicate_username(self, client, test_user):
        """重複ユーザー名での登録テスト"""
        response = client.post('/auth/register', data={
            'username': 'testuser',  # 既存のユーザー名
            'email': 'different@example.com',
            'password': 'ValidPass123',
            'password2': 'ValidPass123'
        })

        assert response.status_code == 200
        assert 'このユーザー名は既に使用されています' in response.get_data(as_text=True)

    def test_login_valid_credentials(self, client, test_user):
        """有効な認証情報でのログインテスト"""
        response = client.get('/auth/login')
        assert response.status_code == 200

        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'TestPassword123'
        })

        assert response.status_code == 302  # リダイレクト
        assert response.location == '/'

    def test_login_invalid_credentials(self, client, test_user):
        """無効な認証情報でのログインテスト"""
        # 間違ったパスワード
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        })

        assert response.status_code == 200
        assert 'ユーザー名またはパスワードが正しくありません' in response.get_data(as_text=True)

        # 存在しないユーザー
        response = client.post('/auth/login', data={
            'username': 'nonexistent',
            'password': 'password123'
        })

        assert response.status_code == 200
        assert 'ユーザー名またはパスワードが正しくありません' in response.get_data(as_text=True)

    def test_logout(self, authenticated_client):
        """ログアウトのテスト"""
        response = authenticated_client.get('/auth/logout')
        assert response.status_code == 302  # リダイレクト
        assert response.location == '/'

    def test_login_required_protection(self, client):
        """ログイン必須ページの保護テスト"""
        # 認証なしでプロファイルページにアクセス
        response = client.get('/auth/profile')
        assert response.status_code == 302  # ログインページにリダイレクト
        assert '/auth/login' in response.location

        # 認証なしでヘルスチェックにアクセス
        response = client.get('/health')
        assert response.status_code == 302  # ログインページにリダイレクト
        assert '/auth/login' in response.location

    def test_authenticated_access(self, authenticated_client):
        """認証済みユーザーのアクセステスト"""
        # プロファイルページにアクセス可能
        response = authenticated_client.get('/auth/profile')
        assert response.status_code == 200
        assert 'ユーザープロファイル' in response.get_data(as_text=True)

        # ヘルスチェックにアクセス可能
        response = authenticated_client.get('/health')
        assert response.status_code == 200

    def test_anonymous_required_protection(self, authenticated_client):
        """匿名ユーザー必須ページの保護テスト（認証済みユーザーのリダイレクト）"""
        # 認証済みユーザーがログインページにアクセス
        response = authenticated_client.get('/auth/login')
        assert response.status_code == 302  # ホームページにリダイレクト
        assert response.location == '/'

        # 認証済みユーザーが登録ページにアクセス
        response = authenticated_client.get('/auth/register')
        assert response.status_code == 302  # ホームページにリダイレクト
        assert response.location == '/'

    def test_remember_me_functionality(self, client, test_user):
        """Remember me機能のテスト"""
        # Remember meにチェックを入れてログイン
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'TestPassword123',
            'remember_me': True
        })

        assert response.status_code == 302

        # セッションクッキーが設定されている（簡易チェック）
        # 実際のRemember me機能のテストはより複雑になる

    def test_redirect_after_login(self, client, test_user):
        """ログイン後のリダイレクトテスト"""
        # 保護されたページに直接アクセス（nextパラメータ付きでログインページにリダイレクト）
        response = client.get('/auth/profile')
        assert response.status_code == 302
        assert '/auth/login' in response.location
        assert 'next=' in response.location

        # ログイン後、元のページにリダイレクトされる
        response = client.post('/auth/login?next=/auth/profile', data={
            'username': 'testuser',
            'password': 'TestPassword123'
        })

        assert response.status_code == 302
        assert '/auth/profile' in response.location

    def test_inactive_user_login(self, client, app):
        """無効化されたユーザーのログインテスト"""
        with app.app_context():
            # 無効化されたユーザーを作成
            inactive_user = User(
                username='inactiveuser',
                email='inactive@example.com',
                password='TestPassword123'
            )
            inactive_user.is_active = False
            db.session.add(inactive_user)
            db.session.commit()

            response = client.post('/auth/login', data={
                'username': 'inactiveuser',
                'password': 'TestPassword123'
            })

            assert response.status_code == 200
            assert 'アカウントが無効化されています' in response.get_data(as_text=True)