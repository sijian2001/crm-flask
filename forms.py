from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Regexp, Optional
from models import User, Customer
from customer_config import CustomerConfig

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

class BaseCustomerForm(FlaskForm):
    """顧客関連フォームの基底クラス"""
    first_name = StringField(
        '名前',
        validators=[
            DataRequired(message='名前を入力してください'),
            Length(min=1, max=CustomerConfig.FIELD_LIMITS['first_name'],
                   message=f'名前は1文字以上{CustomerConfig.FIELD_LIMITS["first_name"]}文字以下で入力してください')
        ],
        render_kw={'placeholder': '太郎'}
    )

    last_name = StringField(
        '姓',
        validators=[
            DataRequired(message='姓を入力してください'),
            Length(min=1, max=CustomerConfig.FIELD_LIMITS['last_name'],
                   message=f'姓は1文字以上{CustomerConfig.FIELD_LIMITS["last_name"]}文字以下で入力してください')
        ],
        render_kw={'placeholder': '田中'}
    )

    email = StringField(
        'メールアドレス',
        validators=[
            DataRequired(message='メールアドレスを入力してください'),
            Email(message='有効なメールアドレスを入力してください'),
            Length(max=CustomerConfig.FIELD_LIMITS['email'],
                   message=f'メールアドレスは{CustomerConfig.FIELD_LIMITS["email"]}文字以下で入力してください')
        ],
        render_kw={'placeholder': 'customer@example.com'}
    )

class CustomerForm(BaseCustomerForm):
    """顧客登録・編集フォーム"""
    phone = StringField(
        '電話番号',
        validators=[
            Optional(),
            Length(max=CustomerConfig.FIELD_LIMITS['phone'],
                   message=f'電話番号は{CustomerConfig.FIELD_LIMITS["phone"]}文字以下で入力してください')
        ],
        render_kw={'placeholder': '090-1234-5678'}
    )

    company = StringField(
        '会社名',
        validators=[
            Optional(),
            Length(max=CustomerConfig.FIELD_LIMITS['company'],
                   message=f'会社名は{CustomerConfig.FIELD_LIMITS["company"]}文字以下で入力してください')
        ],
        render_kw={'placeholder': '株式会社サンプル'}
    )

    address = TextAreaField(
        '住所',
        validators=[
            Optional(),
            Length(max=500, message='住所は500文字以下で入力してください')
        ],
        render_kw={'placeholder': '東京都渋谷区...', 'rows': 3}
    )

    notes = TextAreaField(
        '備考',
        validators=[
            Optional(),
            Length(max=CustomerConfig.FIELD_LIMITS['notes'],
                   message=f'備考は{CustomerConfig.FIELD_LIMITS["notes"]}文字以下で入力してください')
        ],
        render_kw={'placeholder': '特記事項があれば入力してください', 'rows': 4}
    )

    submit = SubmitField('保存')

    def __init__(self, customer=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.customer = customer

    def validate_email(self, email):
        """メールアドレスの重複チェック"""
        customer = Customer.query.filter_by(email=email.data).first()
        if customer and (not self.customer or customer.id != self.customer.id):
            raise ValidationError('このメールアドレスは既に使用されています。')

class CustomerSearchForm(FlaskForm):
    """顧客検索フォーム"""
    search = StringField(
        '検索',
        validators=[Optional()],
        render_kw={'placeholder': '名前、メール、会社名で検索...'}
    )

    submit = SubmitField('検索')
    clear = SubmitField('クリア')