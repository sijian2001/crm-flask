from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DecimalField, IntegerField, SelectField, DateField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Regexp, Optional, NumberRange
from models import User, Customer, Product, Category, Store, Employee, Position, Department
from customer_config import CustomerConfig
from product_config import ProductConfig

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


class BaseCategoryForm(FlaskForm):
    """カテゴリ関連フォームの基底クラス"""
    name = StringField(
        'カテゴリ名',
        validators=[
            DataRequired(message='カテゴリ名を入力してください'),
            Length(min=1, max=ProductConfig.get_category_config()['name_max_length'],
                   message=f'カテゴリ名は1文字以上{ProductConfig.get_category_config()["name_max_length"]}文字以下で入力してください')
        ],
        render_kw={'placeholder': 'カテゴリ名'}
    )

    description = TextAreaField(
        '説明',
        validators=[
            Optional(),
            Length(max=ProductConfig.get_category_config()['description_max_length'],
                   message=f'説明は{ProductConfig.get_category_config()["description_max_length"]}文字以下で入力してください')
        ],
        render_kw={'placeholder': 'カテゴリの説明を入力してください', 'rows': 3}
    )


class CategoryForm(BaseCategoryForm):
    """カテゴリ登録・編集フォーム"""
    parent_id = SelectField(
        '親カテゴリ',
        validators=[Optional()],
        coerce=int,
        choices=[]
    )

    submit = SubmitField('保存')

    def __init__(self, category=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category = category

        # 親カテゴリの選択肢を設定
        self.parent_id.choices = [(0, '選択してください')]

        # アクティブなカテゴリを取得（編集中のカテゴリの子孫は除外）
        categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()

        if category:
            # 編集時は自分自身とその子孫を除外
            excluded_ids = {category.id}
            excluded_ids.update(child.id for child in category.get_all_children())
            categories = [c for c in categories if c.id not in excluded_ids]

        for cat in categories:
            self.parent_id.choices.append((cat.id, cat.full_path))

    def validate_parent_id(self, parent_id):
        """親カテゴリの妥当性チェック"""
        if parent_id.data and parent_id.data != 0:
            parent = Category.query.get(parent_id.data)
            if not parent or not parent.is_active:
                raise ValidationError('指定された親カテゴリが見つかりません。')


class BaseProductForm(FlaskForm):
    """製品関連フォームの基底クラス"""
    name = StringField(
        '製品名',
        validators=[
            DataRequired(message='製品名を入力してください'),
            Length(min=1, max=ProductConfig.get_name_max_length(),
                   message=f'製品名は1文字以上{ProductConfig.get_name_max_length()}文字以下で入力してください')
        ],
        render_kw={'placeholder': '製品名'}
    )

    sku = StringField(
        'SKU',
        validators=[
            DataRequired(message='SKUを入力してください'),
            Length(min=1, max=ProductConfig.get_sku_max_length(),
                   message=f'SKUは1文字以上{ProductConfig.get_sku_max_length()}文字以下で入力してください'),
            Regexp(r'^[A-Za-z0-9_-]+$', message='SKUは英数字、ハイフン、アンダースコアのみ使用可能です')
        ],
        render_kw={'placeholder': 'PROD-001'}
    )

    description = TextAreaField(
        '説明',
        validators=[
            Optional(),
            Length(max=ProductConfig.get_description_max_length(),
                   message=f'説明は{ProductConfig.get_description_max_length()}文字以下で入力してください')
        ],
        render_kw={'placeholder': '製品の説明を入力してください', 'rows': 4}
    )

    price = DecimalField(
        '価格',
        validators=[
            DataRequired(message='価格を入力してください'),
            NumberRange(min=0, message='価格は0以上である必要があります')
        ],
        render_kw={'placeholder': '1000.00', 'step': '0.01', 'min': '0'}
    )

    category_id = SelectField(
        'カテゴリ',
        validators=[DataRequired(message='カテゴリを選択してください')],
        coerce=int,
        choices=[]
    )


class ProductForm(BaseProductForm):
    """製品登録・編集フォーム"""
    cost = DecimalField(
        '原価',
        validators=[
            Optional(),
            NumberRange(min=0, message='原価は0以上である必要があります')
        ],
        render_kw={'placeholder': '800.00', 'step': '0.01', 'min': '0'}
    )

    stock_quantity = IntegerField(
        '在庫数量',
        validators=[
            DataRequired(message='在庫数量を入力してください'),
            NumberRange(min=0, max=ProductConfig.get_validation_config()['stock_max_value'],
                       message=f'在庫数量は0以上{ProductConfig.get_validation_config()["stock_max_value"]}以下である必要があります')
        ],
        render_kw={'placeholder': '100', 'min': '0'}
    )

    min_stock_level = IntegerField(
        '最小在庫レベル',
        validators=[
            DataRequired(message='最小在庫レベルを入力してください'),
            NumberRange(min=0, max=ProductConfig.get_validation_config()['stock_max_value'],
                       message=f'最小在庫レベルは0以上{ProductConfig.get_validation_config()["stock_max_value"]}以下である必要があります')
        ],
        default=ProductConfig.get_default_min_stock_level(),
        render_kw={'placeholder': str(ProductConfig.get_default_min_stock_level()), 'min': '0'}
    )

    submit = SubmitField('保存')

    def __init__(self, product=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.product = product

        # カテゴリの選択肢を設定
        self.category_id.choices = [(0, 'カテゴリを選択してください')]
        categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()
        for category in categories:
            self.category_id.choices.append((category.id, category.full_path))

    def validate_sku(self, sku):
        """SKUの重複チェック"""
        product = Product.query.filter_by(sku=sku.data).first()
        if product and (not self.product or product.id != self.product.id):
            raise ValidationError('このSKUは既に使用されています。')

    def validate_category_id(self, category_id):
        """カテゴリの妥当性チェック"""
        if category_id.data == 0:
            raise ValidationError('カテゴリを選択してください。')

        category = Category.query.get(category_id.data)
        if not category or not category.is_active:
            raise ValidationError('指定されたカテゴリが見つかりません。')

    def validate_min_stock_level(self, min_stock_level):
        """最小在庫レベルの妥当性チェック"""
        if self.stock_quantity.data and min_stock_level.data > self.stock_quantity.data:
            raise ValidationError('最小在庫レベルは現在の在庫数量以下である必要があります。')


class ProductSearchForm(FlaskForm):
    """製品検索フォーム"""
    search = StringField(
        '検索',
        validators=[Optional()],
        render_kw={'placeholder': '製品名、SKU、説明で検索...'}
    )

    category_id = SelectField(
        'カテゴリ',
        validators=[Optional()],
        coerce=int,
        choices=[]
    )

    low_stock_only = BooleanField('在庫不足のみ表示')

    submit = SubmitField('検索')
    clear = SubmitField('クリア')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # カテゴリの選択肢を設定
        self.category_id.choices = [(0, 'すべてのカテゴリ')]
        categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()
        for category in categories:
            self.category_id.choices.append((category.id, category.full_path))


class StockUpdateForm(FlaskForm):
    """在庫更新フォーム"""
    stock_quantity = IntegerField(
        '在庫数量',
        validators=[
            DataRequired(message='在庫数量を入力してください'),
            NumberRange(min=0, max=ProductConfig.get_validation_config()['stock_max_value'],
                       message=f'在庫数量は0以上{ProductConfig.get_validation_config()["stock_max_value"]}以下である必要があります')
        ],
        render_kw={'min': '0'}
    )

    submit = SubmitField('更新')


class CategorySearchForm(FlaskForm):
    """カテゴリ検索フォーム"""
    search = StringField(
        '検索',
        validators=[Optional()],
        render_kw={'placeholder': 'カテゴリ名、説明で検索...'}
    )

    parent_id = SelectField(
        '親カテゴリ',
        validators=[Optional()],
        coerce=int,
        choices=[]
    )

    submit = SubmitField('検索')
    clear = SubmitField('クリア')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 親カテゴリの選択肢を設定
        self.parent_id.choices = [(0, 'すべての親カテゴリ'), (-1, 'ルートカテゴリのみ')]
        categories = Category.query.filter_by(is_active=True, parent_id=None).order_by(Category.name).all()
        for category in categories:
            self.parent_id.choices.append((category.id, category.name))


class StoreForm(FlaskForm):
    """店舗登録・編集フォーム"""
    name = StringField(
        '店舗名',
        validators=[
            DataRequired(message='店舗名を入力してください'),
            Length(max=200, message='店舗名は200文字以下で入力してください')
        ],
        render_kw={'placeholder': '店舗名'}
    )

    address = TextAreaField(
        '住所',
        validators=[
            DataRequired(message='住所を入力してください'),
            Length(max=500, message='住所は500文字以下で入力してください')
        ],
        render_kw={'placeholder': '住所を入力してください', 'rows': 3}
    )

    phone = StringField(
        '電話番号',
        validators=[
            Optional(),
            Length(max=20, message='電話番号は20文字以下で入力してください'),
            Regexp(r'^[\d\-\(\)\+\s]*$', message='有効な電話番号を入力してください')
        ],
        render_kw={'placeholder': '03-1234-5678'}
    )

    email = StringField(
        'メールアドレス',
        validators=[
            Optional(),
            Email(message='有効なメールアドレスを入力してください'),
            Length(max=120, message='メールアドレスは120文字以下で入力してください')
        ],
        render_kw={'placeholder': 'store@example.com'}
    )

    location_prefecture = StringField(
        '都道府県',
        validators=[
            Optional(),
            Length(max=50, message='都道府県は50文字以下で入力してください')
        ],
        render_kw={'placeholder': '東京都'}
    )

    location_city = StringField(
        '市区町村',
        validators=[
            Optional(),
            Length(max=100, message='市区町村は100文字以下で入力してください')
        ],
        render_kw={'placeholder': '渋谷区'}
    )

    status = SelectField(
        '営業状況',
        validators=[DataRequired(message='営業状況を選択してください')],
        choices=[
            ('active', '営業中'),
            ('temporarily_closed', '一時休業'),
            ('inactive', '休業')
        ],
        default='active'
    )

    establishment_date = DateField(
        '開店日',
        validators=[Optional()],
        render_kw={'placeholder': 'YYYY-MM-DD'}
    )

    # 営業時間フィールド（簡略化）
    monday_hours = StringField(
        '月曜日',
        validators=[Optional(), Length(max=20)],
        render_kw={'placeholder': '09:00-18:00 または closed'}
    )

    tuesday_hours = StringField(
        '火曜日',
        validators=[Optional(), Length(max=20)],
        render_kw={'placeholder': '09:00-18:00 または closed'}
    )

    wednesday_hours = StringField(
        '水曜日',
        validators=[Optional(), Length(max=20)],
        render_kw={'placeholder': '09:00-18:00 または closed'}
    )

    thursday_hours = StringField(
        '木曜日',
        validators=[Optional(), Length(max=20)],
        render_kw={'placeholder': '09:00-18:00 または closed'}
    )

    friday_hours = StringField(
        '金曜日',
        validators=[Optional(), Length(max=20)],
        render_kw={'placeholder': '09:00-18:00 または closed'}
    )

    saturday_hours = StringField(
        '土曜日',
        validators=[Optional(), Length(max=20)],
        render_kw={'placeholder': '10:00-17:00 または closed'}
    )

    sunday_hours = StringField(
        '日曜日',
        validators=[Optional(), Length(max=20)],
        render_kw={'placeholder': 'closed'}
    )

    closed_days = StringField(
        '定休日',
        validators=[
            Optional(),
            Length(max=50, message='定休日は50文字以下で入力してください')
        ],
        render_kw={'placeholder': '日曜日、祝日など'}
    )

    submit = SubmitField('保存')

    def __init__(self, store=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.store = store

        # 既存店舗の場合、営業時間を設定
        if store and store.business_hours:
            hours = store.business_hours
            self.monday_hours.data = hours.get('mon', '')
            self.tuesday_hours.data = hours.get('tue', '')
            self.wednesday_hours.data = hours.get('wed', '')
            self.thursday_hours.data = hours.get('thu', '')
            self.friday_hours.data = hours.get('fri', '')
            self.saturday_hours.data = hours.get('sat', '')
            self.sunday_hours.data = hours.get('sun', '')

    def validate_name(self, name):
        """店舗名の重複チェック"""
        store = Store.query.filter_by(name=name.data).first()
        if store and (not self.store or store.id != self.store.id):
            raise ValidationError('この店舗名は既に使用されています。')

    def get_business_hours(self):
        """営業時間辞書を作成"""
        return {
            'mon': self.monday_hours.data or 'closed',
            'tue': self.tuesday_hours.data or 'closed',
            'wed': self.wednesday_hours.data or 'closed',
            'thu': self.thursday_hours.data or 'closed',
            'fri': self.friday_hours.data or 'closed',
            'sat': self.saturday_hours.data or 'closed',
            'sun': self.sunday_hours.data or 'closed'
        }


class StoreSearchForm(FlaskForm):
    """店舗検索フォーム"""
    search = StringField(
        '検索',
        validators=[Optional()],
        render_kw={'placeholder': '店舗名、住所で検索...'}
    )

    status = SelectField(
        '営業状況',
        validators=[Optional()],
        choices=[
            ('', 'すべて'),
            ('active', '営業中'),
            ('temporarily_closed', '一時休業'),
            ('inactive', '休業')
        ]
    )

    prefecture = SelectField(
        '都道府県',
        validators=[Optional()],
        choices=[('', 'すべて')]
    )

    city = SelectField(
        '市区町村',
        validators=[Optional()],
        choices=[('', 'すべて')]
    )

    submit = SubmitField('検索')
    clear = SubmitField('クリア')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 都道府県の選択肢を動的に設定
        prefectures = Store.query.with_entities(Store.location_prefecture).filter(
            Store.location_prefecture.isnot(None)
        ).distinct().order_by(Store.location_prefecture).all()

        self.prefecture.choices = [('', 'すべて')]
        for (pref,) in prefectures:
            if pref:
                self.prefecture.choices.append((pref, pref))

        # 市区町村の選択肢は JavaScript で動的に更新


class EmployeeForm(FlaskForm):
    """従業員登録・編集フォーム"""
    employee_code = StringField(
        '従業員コード',
        validators=[
            DataRequired(message='従業員コードを入力してください'),
            Length(max=20, message='従業員コードは20文字以下で入力してください'),
            Regexp(r'^[A-Za-z0-9\-_]+$', message='従業員コードは英数字とハイフン、アンダースコアのみ使用可能です')
        ],
        render_kw={'placeholder': 'EMP001'}
    )

    first_name = StringField(
        '名',
        validators=[
            DataRequired(message='名を入力してください'),
            Length(max=50, message='名は50文字以下で入力してください')
        ],
        render_kw={'placeholder': '太郎'}
    )

    last_name = StringField(
        '姓',
        validators=[
            DataRequired(message='姓を入力してください'),
            Length(max=50, message='姓は50文字以下で入力してください')
        ],
        render_kw={'placeholder': '田中'}
    )

    email = StringField(
        'メールアドレス',
        validators=[
            Optional(),
            Email(message='有効なメールアドレスを入力してください'),
            Length(max=120, message='メールアドレスは120文字以下で入力してください')
        ],
        render_kw={'placeholder': 'employee@example.com'}
    )

    phone = StringField(
        '電話番号',
        validators=[
            Optional(),
            Length(max=20, message='電話番号は20文字以下で入力してください'),
            Regexp(r'^[\d\-\(\)\+\s]*$', message='有効な電話番号を入力してください')
        ],
        render_kw={'placeholder': '090-1234-5678'}
    )

    hire_date = DateField(
        '入社日',
        validators=[DataRequired(message='入社日を選択してください')],
        render_kw={'placeholder': 'YYYY-MM-DD'}
    )

    employment_status = SelectField(
        '雇用状況',
        validators=[DataRequired(message='雇用状況を選択してください')],
        choices=[
            ('active', '在職'),
            ('on_leave', '休職'),
            ('inactive', '退職'),
            ('terminated', '解雇')
        ],
        default='active'
    )

    salary_level = IntegerField(
        '給与レベル',
        validators=[
            Optional(),
            NumberRange(min=1, max=10, message='給与レベルは1-10の範囲で入力してください')
        ],
        render_kw={'placeholder': '1-10', 'min': '1', 'max': '10'}
    )

    store_id = SelectField(
        '所属店舗',
        validators=[DataRequired(message='所属店舗を選択してください')],
        coerce=int
    )

    position_id = SelectField(
        '役職',
        validators=[DataRequired(message='役職を選択してください')],
        coerce=int
    )

    department_id = SelectField(
        '部署',
        validators=[Optional()],
        coerce=lambda x: int(x) if x else None
    )

    manager_id = SelectField(
        '上司',
        validators=[Optional()],
        coerce=lambda x: int(x) if x else None
    )

    emergency_contact_name = StringField(
        '緊急連絡先（氏名）',
        validators=[
            Optional(),
            Length(max=100, message='緊急連絡先氏名は100文字以下で入力してください')
        ],
        render_kw={'placeholder': '緊急連絡先の氏名'}
    )

    emergency_contact_phone = StringField(
        '緊急連絡先（電話番号）',
        validators=[
            Optional(),
            Length(max=20, message='緊急連絡先電話番号は20文字以下で入力してください'),
            Regexp(r'^[\d\-\(\)\+\s]*$', message='有効な電話番号を入力してください')
        ],
        render_kw={'placeholder': '090-1234-5678'}
    )

    notes = TextAreaField(
        '備考',
        validators=[Optional()],
        render_kw={'placeholder': '特記事項があれば入力してください', 'rows': 3}
    )

    submit = SubmitField('保存')

    def __init__(self, employee=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.employee = employee

        # 店舗の選択肢を設定
        self.store_id.choices = [(0, '店舗を選択してください')]
        stores = Store.query.filter_by(status='active').order_by(Store.name).all()
        for store in stores:
            self.store_id.choices.append((store.id, store.name))

        # 役職の選択肢を設定
        self.position_id.choices = [(0, '役職を選択してください')]
        positions = Position.query.filter_by(is_active=True).order_by(Position.level, Position.name).all()
        for position in positions:
            level_indicator = "★" * min(position.level, 5) if position.is_management else ""
            display_name = f"{position.name} {level_indicator}".strip()
            self.position_id.choices.append((position.id, display_name))

        # 部署の選択肢を設定
        self.department_id.choices = [('', '部署を選択してください（任意）')]
        departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
        for department in departments:
            self.department_id.choices.append((department.id, department.full_name))

        # 上司の選択肢を設定（管理職のみ）
        self.manager_id.choices = [('', '上司を選択してください（任意）')]
        managers = Employee.query.join(Position).filter(
            Employee.employment_status == 'active',
            Position.is_management == True
        ).order_by(Employee.last_name, Employee.first_name).all()

        for manager in managers:
            # 自分自身は選択肢に含めない
            if not employee or manager.id != employee.id:
                self.manager_id.choices.append((manager.id, f"{manager.full_name} ({manager.position.name})"))

    def validate_employee_code(self, employee_code):
        """従業員コードの重複チェック"""
        employee = Employee.query.filter_by(employee_code=employee_code.data).first()
        if employee and (not self.employee or employee.id != self.employee.id):
            raise ValidationError('この従業員コードは既に使用されています。')

    def validate_email(self, email):
        """メールアドレスの重複チェック"""
        if email.data:
            employee = Employee.query.filter_by(email=email.data).first()
            if employee and (not self.employee or employee.id != self.employee.id):
                raise ValidationError('このメールアドレスは既に使用されています。')

    def validate_manager_id(self, manager_id):
        """上司設定の循環参照チェック"""
        if manager_id.data and self.employee:
            manager = Employee.query.get(manager_id.data)
            if manager and not self.employee.can_be_manager_of(manager):
                raise ValidationError('循環参照となる上司の設定はできません。')


class EmployeeSearchForm(FlaskForm):
    """従業員検索フォーム"""
    search = StringField(
        '検索',
        validators=[Optional()],
        render_kw={'placeholder': '従業員名、従業員コード、メールアドレスで検索...'}
    )

    store_id = SelectField(
        '店舗',
        validators=[Optional()],
        coerce=lambda x: int(x) if x else None
    )

    position_id = SelectField(
        '役職',
        validators=[Optional()],
        coerce=lambda x: int(x) if x else None
    )

    department_id = SelectField(
        '部署',
        validators=[Optional()],
        coerce=lambda x: int(x) if x else None
    )

    employment_status = SelectField(
        '雇用状況',
        validators=[Optional()],
        choices=[
            ('', 'すべて'),
            ('active', '在職'),
            ('on_leave', '休職'),
            ('inactive', '退職'),
            ('terminated', '解雇')
        ]
    )

    manager_id = SelectField(
        '上司',
        validators=[Optional()],
        coerce=lambda x: int(x) if x else None
    )

    submit = SubmitField('検索')
    clear = SubmitField('クリア')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 店舗の選択肢を設定
        self.store_id.choices = [('', 'すべて')]
        stores = Store.query.filter_by(status='active').order_by(Store.name).all()
        for store in stores:
            self.store_id.choices.append((store.id, store.name))

        # 役職の選択肢を設定
        self.position_id.choices = [('', 'すべて')]
        positions = Position.query.filter_by(is_active=True).order_by(Position.level, Position.name).all()
        for position in positions:
            level_indicator = "★" * min(position.level, 5) if position.is_management else ""
            display_name = f"{position.name} {level_indicator}".strip()
            self.position_id.choices.append((position.id, display_name))

        # 部署の選択肢を設定
        self.department_id.choices = [('', 'すべて')]
        departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
        for department in departments:
            self.department_id.choices.append((department.id, department.full_name))

        # 上司の選択肢を設定
        self.manager_id.choices = [('', 'すべて')]
        managers = Employee.query.join(Position).filter(
            Employee.employment_status == 'active',
            Position.is_management == True
        ).order_by(Employee.last_name, Employee.first_name).all()

        for manager in managers:
            self.manager_id.choices.append((manager.id, f"{manager.full_name} ({manager.position.name})"))


class PositionForm(FlaskForm):
    """役職登録・編集フォーム"""
    name = StringField(
        '役職名',
        validators=[
            DataRequired(message='役職名を入力してください'),
            Length(max=100, message='役職名は100文字以下で入力してください')
        ],
        render_kw={'placeholder': '店長、副店長、スタッフなど'}
    )

    level = IntegerField(
        '階層レベル',
        validators=[
            DataRequired(message='階層レベルを入力してください'),
            NumberRange(min=1, max=999, message='階層レベルは1-999の範囲で入力してください')
        ],
        render_kw={'placeholder': '1（最上位）～999', 'min': '1', 'max': '999'}
    )

    description = TextAreaField(
        '説明',
        validators=[Optional()],
        render_kw={'placeholder': '役職の説明を入力してください', 'rows': 3}
    )

    is_management = BooleanField(
        '管理職',
        validators=[Optional()]
    )

    salary_min = IntegerField(
        '最低給与（万円）',
        validators=[
            Optional(),
            NumberRange(min=100, max=2000, message='最低給与は100-2000万円の範囲で入力してください')
        ],
        render_kw={'placeholder': '例: 200', 'min': '100', 'max': '2000'}
    )

    salary_max = IntegerField(
        '最高給与（万円）',
        validators=[
            Optional(),
            NumberRange(min=100, max=2000, message='最高給与は100-2000万円の範囲で入力してください')
        ],
        render_kw={'placeholder': '例: 800', 'min': '100', 'max': '2000'}
    )

    is_active = BooleanField(
        'アクティブ',
        validators=[Optional()],
        default=True
    )

    submit = SubmitField('保存')

    def __init__(self, position=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.position = position

    def validate_name(self, name):
        """役職名の重複チェック"""
        position = Position.query.filter_by(name=name.data).first()
        if position and (not self.position or position.id != self.position.id):
            raise ValidationError('この役職名は既に使用されています。')

    def validate_salary_max(self, salary_max):
        """給与範囲の妥当性チェック"""
        if salary_max.data and self.salary_min.data:
            if salary_max.data < self.salary_min.data:
                raise ValidationError('最高給与は最低給与以上にしてください。')


class DepartmentForm(FlaskForm):
    """部署登録・編集フォーム"""
    name = StringField(
        '部署名',
        validators=[
            DataRequired(message='部署名を入力してください'),
            Length(max=100, message='部署名は100文字以下で入力してください')
        ],
        render_kw={'placeholder': '営業部、管理部など'}
    )

    parent_id = SelectField(
        '親部署',
        validators=[Optional()],
        coerce=lambda x: int(x) if x else None
    )

    description = TextAreaField(
        '説明',
        validators=[Optional()],
        render_kw={'placeholder': '部署の説明を入力してください', 'rows': 3}
    )

    head_employee_id = SelectField(
        '部署長',
        validators=[Optional()],
        coerce=lambda x: int(x) if x else None
    )

    is_active = BooleanField(
        'アクティブ',
        validators=[Optional()],
        default=True
    )

    submit = SubmitField('保存')

    def __init__(self, department=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.department = department

        # 親部署の選択肢を設定
        self.parent_id.choices = [('', '親部署なし（ルート部署）')]
        departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
        for dept in departments:
            # 自分自身は選択肢に含めない
            if not department or dept.id != department.id:
                self.parent_id.choices.append((dept.id, dept.full_name))

        # 部署長の選択肢を設定（管理職のみ）
        self.head_employee_id.choices = [('', '部署長を選択してください（任意）')]
        managers = Employee.query.join(Position).filter(
            Employee.employment_status == 'active',
            Position.is_management == True
        ).order_by(Employee.last_name, Employee.first_name).all()

        for manager in managers:
            self.head_employee_id.choices.append((manager.id, f"{manager.full_name} ({manager.position.name})"))

    def validate_parent_id(self, parent_id):
        """親部署設定の循環参照チェック"""
        if parent_id.data and self.department:
            parent = Department.query.get(parent_id.data)
            if parent and not self.department.can_be_moved_to(parent):
                raise ValidationError('循環参照となる親部署の設定はできません。')