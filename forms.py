from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Regexp
from models import User

class BaseUserForm(FlaskForm):
    """ユーザー関連フォームの基底クラス"""
    username = StringField(
        'ユーザー名',
        validators=[
            DataRequired(message='ユーザー名を入力してください'),
            Length(min=3, max=80, message='ユーザー名は3文字以上80文字以下で入力してください')
        ],
        render_kw={'placeholder': 'ユーザー名'}
    )

    def validate_username(self, username):
        """ユーザー名の重複チェック"""
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('このユーザー名は既に使用されています。')

class LoginForm(BaseUserForm):
    """ログインフォーム"""
    password = PasswordField(
        'パスワード',
        validators=[
            DataRequired(message='パスワードを入力してください'),
            Length(min=4, message='パスワードは4文字以上で入力してください')
        ],
        render_kw={'placeholder': 'パスワード'}
    )

    remember_me = BooleanField('ログイン状態を保持する')
    submit = SubmitField('ログイン')

    def validate_username(self, username):
        """ログインフォームではユーザー名重複チェックを無効化"""
        pass

class RegistrationForm(BaseUserForm):
    """ユーザー登録フォーム"""

    email = StringField(
        'メールアドレス',
        validators=[
            DataRequired(message='メールアドレスを入力してください'),
            Email(message='有効なメールアドレスを入力してください'),
            Length(max=120, message='メールアドレスは120文字以下で入力してください')
        ],
        render_kw={'placeholder': 'email@example.com'}
    )

    password = PasswordField(
        'パスワード',
        validators=[
            DataRequired(message='パスワードを入力してください'),
            Length(min=8, message='パスワードは8文字以上で入力してください'),
            Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)', message='英大文字、小文字、数字を含む必要があります')
        ],
        render_kw={'placeholder': 'パスワード'}
    )

    password2 = PasswordField(
        'パスワード確認',
        validators=[
            DataRequired(message='パスワード確認を入力してください')
        ],
        render_kw={'placeholder': 'パスワード確認'}
    )

    submit = SubmitField('登録')

    def validate_email(self, email):
        """メールアドレスの重複チェック"""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('このメールアドレスは既に使用されています。')

    def validate_password2(self, password2):
        """パスワード確認チェック"""
        if self.password.data != password2.data:
            raise ValidationError('パスワードが一致しません。')