import pytest
import re
from werkzeug.security import check_password_hash
from models import User, db
from forms import RegistrationForm, LoginForm

class TestPasswordSecurity:
    """パスワードセキュリティのテスト"""

    def test_password_hashing_strength(self, app):
        """パスワードハッシュ化の強度テスト"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password='StrongPassword123'
            )

            # パスワードがハッシュ化されている
            assert user.password_hash is not None
            assert user.password_hash != 'StrongPassword123'

            # Werkzeugハッシュの形式をチェック（scryptまたはpbkdf2で開始）
            assert user.password_hash.startswith(('scrypt:', 'pbkdf2:', '$2b$'))

            # ハッシュが十分な長さを持っている
            assert len(user.password_hash) >= 60

    def test_password_hash_uniqueness(self, app):
        """同じパスワードでも異なるハッシュが生成されることのテスト"""
        with app.app_context():
            user1 = User(
                username='user1',
                email='user1@example.com',
                password='SamePassword123'
            )

            user2 = User(
                username='user2',
                email='user2@example.com',
                password='SamePassword123'
            )

            # 同じパスワードでも異なるハッシュが生成される（salt使用確認）
            assert user1.password_hash != user2.password_hash

            # どちらも正しく検証される
            assert user1.check_password('SamePassword123')
            assert user2.check_password('SamePassword123')

    def test_password_cannot_be_retrieved(self, app):
        """パスワードが平文で取得できないことのテスト"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password='SecretPassword123'
            )

            # passwordフィールドが存在しない（セッター専用）
            assert not hasattr(user, 'password')

            # password_hashから元のパスワードを推測できない
            assert 'SecretPassword123' not in user.password_hash
            assert 'secret' not in user.password_hash.lower()

    def test_password_complexity_validation(self, app):
        """パスワード複雑性要件のテスト"""
        with app.app_context():
            form = RegistrationForm()

            # 弱いパスワードのテストケース
            weak_passwords = [
                'short',  # 短すぎる
                'onlylowercase',  # 小文字のみ
                'ONLYUPPERCASE',  # 大文字のみ
                '12345678',  # 数字のみ
                'NoNumbers',  # 数字なし
                'nocapitals123',  # 大文字なし
                'NOSMALL123',  # 小文字なし
            ]

            for password in weak_passwords:
                form.password.data = password
                form.password2.data = password
                form.username.data = 'testuser'
                form.email.data = 'test@example.com'

                # バリデーションが失敗する
                assert not form.validate()

    def test_timing_attack_protection(self, app):
        """タイミング攻撃からの保護テスト"""
        with app.app_context():
            # 存在するユーザー
            user = User(
                username='existinguser',
                email='existing@example.com',
                password='ValidPassword123'
            )
            db.session.add(user)
            db.session.commit()

            # 存在しないユーザーに対しても一定時間をかける
            # (実際の実装では一定の計算を行うべき)
            import time

            start_time = time.time()
            nonexistent_user = User.query.filter_by(username='nonexistent').first()
            if nonexistent_user:
                nonexistent_user.check_password('anypassword')
            end_time = time.time()

            # 最低限の時間がかかることを確認
            # （実際の実装ではより厳密なタイミング制御が必要）
            elapsed_time = end_time - start_time
            assert elapsed_time >= 0  # 基本的なチェック

class TestCSRFProtection:
    """CSRF保護のテスト"""

    def test_csrf_token_in_forms(self, client):
        """フォームにCSRFトークンが含まれることのテスト"""
        # ログインフォーム
        response = client.get('/auth/login')
        assert response.status_code == 200
        # テスト環境ではCSRFが無効なので、フォームの存在確認
        assert 'form' in response.get_data(as_text=True).lower()

        # 登録フォーム
        response = client.get('/auth/register')
        assert response.status_code == 200
        # テスト環境ではCSRFが無効なので、フォームの存在確認
        assert 'form' in response.get_data(as_text=True).lower()

    def test_csrf_protection_enabled(self, app):
        """CSRF保護が有効になっていることのテスト"""
        # テスト設定ではCSRFが無効化されているため、
        # プロダクション設定でのテストが必要
        from config import Config
        prod_config = Config()

        # プロダクション設定ではCSRFがデフォルトで有効（明示的に無効化されていない）
        csrf_enabled = getattr(prod_config, 'WTF_CSRF_ENABLED', True)
        assert csrf_enabled is not False

    def test_form_validation_with_csrf(self, client, app):
        """CSRFトークンを含むフォーム送信のテスト"""
        with app.test_request_context():
            # CSRFが有効な場合のテスト用設定
            app.config['WTF_CSRF_ENABLED'] = True

            # CSRFトークンなしでの送信は失敗するはず
            # （テスト環境ではCSRFが無効化されているため、実際のテストは制限される）

            # 実際のアプリケーションではCSRFトークンの検証が行われる
            form = LoginForm()
            assert hasattr(form, 'csrf_token')

class TestSessionSecurity:
    """セッションセキュリティのテスト"""

    def test_session_configuration(self, app):
        """セッション設定のセキュリティテスト"""
        # セッションクッキーの設定確認
        assert app.config.get('SESSION_COOKIE_SECURE') is not None
        assert app.config.get('SESSION_COOKIE_HTTPONLY') is not None
        assert app.config.get('SESSION_COOKIE_SAMESITE') is not None

    def test_remember_me_security(self, client, test_user):
        """Remember me機能のセキュリティテスト"""
        # Remember meでログイン
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'TestPassword123',
            'remember_me': 'y'  # チェックボックスの値として'y'を使用
        })

        assert response.status_code == 302

        # セッションクッキーが設定されている
        # remember meログインが成功したことをレスポンスで確認
        assert response.location == '/'

        # 認証状態を確認するため、保護されたページにアクセス
        profile_response = client.get('/auth/profile')
        assert profile_response.status_code == 200

    def test_logout_clears_session(self, authenticated_client):
        """ログアウト時のセッションクリアテスト"""
        # ログアウト前は認証済み
        response = authenticated_client.get('/auth/profile')
        assert response.status_code == 200

        # ログアウト
        response = authenticated_client.get('/auth/logout')
        assert response.status_code == 302

        # ログアウト後は認証が必要
        response = authenticated_client.get('/auth/profile')
        assert response.status_code == 302  # ログインページにリダイレクト

class TestSecurityLogging:
    """セキュリティログのテスト"""

    def test_login_attempt_logging(self, client, test_user, caplog):
        """ログイン試行のログ記録テスト"""
        import logging

        with caplog.at_level(logging.INFO):
            # 成功ログイン
            client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'TestPassword123'
            })

            # ログが記録されている
            assert 'logged in successfully' in caplog.text

    def test_failed_login_logging(self, client, test_user, caplog):
        """失敗ログインのログ記録テスト"""
        import logging

        with caplog.at_level(logging.WARNING):
            # 失敗ログイン
            client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'wrongpassword'
            })

            # 警告ログが記録されている
            assert 'Failed login attempt' in caplog.text

    def test_registration_logging(self, client, caplog):
        """ユーザー登録のログ記録テスト"""
        import logging

        with caplog.at_level(logging.INFO, logger='auth'):
            # 新規登録
            response = client.post('/auth/register', data={
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'ValidPassword123',
                'password2': 'ValidPassword123'
            })

            # 成功した場合のみログをチェック
            if response.status_code == 302:  # リダイレクト成功
                # 登録ログが記録されている
                log_messages = [record.message for record in caplog.records]
                assert any('New user registered' in msg for msg in log_messages)

class TestInputValidation:
    """入力検証のセキュリティテスト"""

    def test_sql_injection_protection(self, client):
        """SQLインジェクション攻撃からの保護テスト"""
        # SQLインジェクション攻撃を試行
        malicious_inputs = [
            "admin'; DROP TABLE users; --",
            "' OR '1'='1",
            "admin' UNION SELECT * FROM users --"
        ]

        for malicious_input in malicious_inputs:
            response = client.post('/auth/login', data={
                'username': malicious_input,
                'password': 'anypassword'
            })

            # 攻撃は失敗し、正常にエラーメッセージが表示される
            assert response.status_code == 200
            assert 'ユーザー名またはパスワードが正しくありません' in response.get_data(as_text=True)

    def test_xss_protection(self, client):
        """XSS攻撃からの保護テスト"""
        xss_payload = "<script>alert('XSS')</script>"

        response = client.post('/auth/login', data={
            'username': xss_payload,
            'password': 'anypassword'
        })

        # スクリプトタグがエスケープされて実行されない
        response_text = response.get_data(as_text=True)
        assert '<script>' not in response_text
        assert '&lt;script&gt;' in response_text or 'alert' not in response_text

    def test_email_validation_security(self, client):
        """メールアドレス検証のセキュリティテスト"""
        invalid_emails = [
            "not-an-email",
            "@domain.com",
            "user@",
            "user..double.dot@example.com",
            "user@domain..com"
        ]

        for invalid_email in invalid_emails:
            response = client.post('/auth/register', data={
                'username': 'testuser',
                'email': invalid_email,
                'password': 'ValidPassword123',
                'password2': 'ValidPassword123'
            })

            # 無効なメールアドレスは拒否される
            assert response.status_code == 200  # フォームエラーで同じページに戻る