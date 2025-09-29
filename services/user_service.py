"""
User service layer

This module provides business logic for user management including authentication,
user creation, and session management.
"""
from typing import Optional, Tuple
from sqlalchemy.exc import IntegrityError
from models import db, User


class UserService:
    """
    Service class for user-related business logic

    Handles all user operations including authentication, registration,
    and user management with proper error handling and validation.
    """

    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username and password

        Args:
            username: Username for authentication
            password: Plain text password

        Returns:
            User instance if authentication successful, None otherwise
        """
        user = User.query.filter_by(username=username, is_active=True).first()
        if user and user.check_password(password):
            user.update_last_login()
            db.session.commit()
            return user
        return None

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """
        Get user by ID

        Args:
            user_id: User ID

        Returns:
            User instance or None if not found
        """
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """
        Get user by username

        Args:
            username: Username

        Returns:
            User instance or None if not found
        """
        return User.query.filter_by(username=username, is_active=True).first()

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """
        Get user by email

        Args:
            email: Email address

        Returns:
            User instance or None if not found
        """
        return User.query.filter_by(email=email, is_active=True).first()

    @staticmethod
    def create_user(username: str, email: str, password: str) -> Tuple[bool, Optional[User], Optional[str]]:
        """
        Create a new user

        Args:
            username: Username (must be unique)
            email: Email address (must be unique)
            password: Plain text password

        Returns:
            Tuple of (success, user, error_message)
        """
        try:
            # Check for existing username
            if User.query.filter_by(username=username).first():
                return False, None, "指定されたユーザー名は既に使用されています。"

            # Check for existing email
            if User.query.filter_by(email=email).first():
                return False, None, "指定されたメールアドレスは既に使用されています。"

            # Create new user
            user = User(username=username, email=email, password=password)
            db.session.add(user)
            db.session.commit()
            return True, user, None

        except IntegrityError:
            db.session.rollback()
            return False, None, "データベースエラーが発生しました。ユーザー名またはメールアドレスが重複している可能性があります。"
        except Exception as e:
            db.session.rollback()
            return False, None, f"ユーザー作成中にエラーが発生しました: {str(e)}"

    @staticmethod
    def update_user_password(user: User, new_password: str) -> Tuple[bool, Optional[str]]:
        """
        Update user password

        Args:
            user: User instance
            new_password: New plain text password

        Returns:
            Tuple of (success, error_message)
        """
        try:
            if not user.is_active:
                return False, "無効化されたユーザーのパスワードは変更できません。"

            user.set_password(new_password)
            db.session.commit()
            return True, None

        except Exception as e:
            db.session.rollback()
            return False, f"パスワード更新中にエラーが発生しました: {str(e)}"

    @staticmethod
    def deactivate_user(user: User) -> Tuple[bool, Optional[str]]:
        """
        Deactivate a user (soft delete)

        Args:
            user: User instance to deactivate

        Returns:
            Tuple of (success, error_message)
        """
        try:
            if not user.is_active:
                return False, "指定されたユーザーは既に無効化されています。"

            user.is_active = False
            db.session.commit()
            return True, None

        except Exception as e:
            db.session.rollback()
            return False, f"ユーザー無効化中にエラーが発生しました: {str(e)}"

    @staticmethod
    def activate_user(user: User) -> Tuple[bool, Optional[str]]:
        """
        Activate a user

        Args:
            user: User instance to activate

        Returns:
            Tuple of (success, error_message)
        """
        try:
            if user.is_active:
                return False, "指定されたユーザーは既に有効化されています。"

            user.is_active = True
            db.session.commit()
            return True, None

        except Exception as e:
            db.session.rollback()
            return False, f"ユーザー有効化中にエラーが発生しました: {str(e)}"