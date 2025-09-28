import pytest
from datetime import datetime
from models import User, db

class TestUserModel:
    """Userモデルのユニットテスト"""

    def test_user_creation(self, app):
        """ユーザー作成のテスト"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password='password123'
            )

            assert user.username == 'testuser'
            assert user.email == 'test@example.com'
            assert user.password_hash is not None
            assert user.password_hash != 'password123'  # パスワードがハッシュ化されている
            assert user.is_active == True
            assert isinstance(user.created_at, datetime)

    def test_password_hashing(self, app):
        """パスワードハッシュ化のテスト"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password='password123'
            )

            # 正しいパスワードで認証成功
            assert user.check_password('password123') is True

            # 間違ったパスワードで認証失敗
            assert user.check_password('wrongpassword') is False
            assert user.check_password('') is False

    def test_set_password(self, app):
        """パスワード設定メソッドのテスト"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password='original123'
            )

            original_hash = user.password_hash

            # パスワードを変更
            user.set_password('newpassword123')

            # ハッシュが変更されている
            assert user.password_hash != original_hash

            # 新しいパスワードで認証成功
            assert user.check_password('newpassword123') is True

            # 古いパスワードで認証失敗
            assert user.check_password('original123') is False

    def test_update_last_login(self, app):
        """最終ログイン時刻更新のテスト"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password='password123'
            )

            # 初期値はNone
            assert user.last_login is None

            # 最終ログイン時刻を更新
            user.update_last_login()

            # 更新されている
            assert user.last_login is not None
            assert isinstance(user.last_login, datetime)

    def test_get_id(self, app):
        """ユーザーID取得のテスト（Flask-Login用）"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password='password123'
            )

            db.session.add(user)
            db.session.commit()

            # IDが文字列として返される
            user_id = user.get_id()
            assert isinstance(user_id, str)
            assert user_id == str(user.id)

    def test_is_authenticated(self, app):
        """認証状態確認のテスト"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password='password123'
            )

            assert user.is_authenticated() is True

    def test_is_anonymous(self, app):
        """匿名ユーザー確認のテスト"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password='password123'
            )

            assert user.is_anonymous() is False

    def test_user_repr(self, app):
        """文字列表現のテスト"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password='password123'
            )

            assert repr(user) == '<User testuser>'

    def test_user_persistence(self, app):
        """ユーザーのデータベース永続化テスト"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password='password123'
            )

            db.session.add(user)
            db.session.commit()

            # データベースから取得
            saved_user = User.query.filter_by(username='testuser').first()

            assert saved_user is not None
            assert saved_user.username == 'testuser'
            assert saved_user.email == 'test@example.com'
            assert saved_user.check_password('password123') is True

    def test_unique_constraints(self, app):
        """一意制約のテスト"""
        with app.app_context():
            # 最初のユーザー
            user1 = User(
                username='testuser',
                email='test@example.com',
                password='password123'
            )
            db.session.add(user1)
            db.session.commit()

            # 同じユーザー名で別のユーザーを作成
            user2 = User(
                username='testuser',
                email='different@example.com',
                password='password456'
            )
            db.session.add(user2)

            # IntegrityErrorが発生するはず
            with pytest.raises(Exception):  # SQLAlchemyのIntegrityError
                db.session.commit()

            db.session.rollback()

            # 同じメールアドレスで別のユーザーを作成
            user3 = User(
                username='differentuser',
                email='test@example.com',
                password='password789'
            )
            db.session.add(user3)

            # IntegrityErrorが発生するはず
            with pytest.raises(Exception):  # SQLAlchemyのIntegrityError
                db.session.commit()