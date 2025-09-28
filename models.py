from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)
        self.is_active = True
        self.created_at = datetime.utcnow()

    def set_password(self, password):
        """パスワードをハッシュ化して保存"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """パスワードを検証"""
        return check_password_hash(self.password_hash, password)

    def update_last_login(self):
        """最終ログイン時刻を更新"""
        self.last_login = datetime.utcnow()

    def get_id(self):
        """Flask-Loginで必要なユーザーID取得メソッド"""
        return str(self.id)

    def is_authenticated(self):
        """認証済みかどうか"""
        return True

    def is_anonymous(self):
        """匿名ユーザーかどうか"""
        return False

    def __repr__(self):
        return f'<User {self.username}>'

class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False, index=True)
    last_name = db.Column(db.String(50), nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    company = db.Column(db.String(100))
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __init__(self, first_name, last_name, email, phone=None, address=None, company=None, notes=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.address = address
        self.company = company
        self.notes = notes
        self.is_active = True
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    @property
    def full_name(self):
        """フルネームを取得"""
        return f"{self.last_name} {self.first_name}"

    def update_info(self, **kwargs):
        """顧客情報を更新"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['id', 'created_at']:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()

    def deactivate(self):
        """顧客を無効化"""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def activate(self):
        """顧客を有効化"""
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def __repr__(self):
        return f'<Customer {self.full_name}>'


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 自己参照関係
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]))
    # 製品との関係
    products = db.relationship('Product', backref='category', lazy=True)

    def __init__(self, name, description=None, parent_id=None):
        self.name = name
        self.description = description
        self.parent_id = parent_id
        self.is_active = True
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    @property
    def full_path(self):
        """カテゴリの完全パスを取得"""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name

    @property
    def product_count(self):
        """このカテゴリの製品数を取得"""
        return Product.query.filter_by(category_id=self.id, is_active=True).count()

    def get_all_children(self):
        """すべての子カテゴリを再帰的に取得"""
        children = []
        for child in self.children:
            if child.is_active:
                children.append(child)
                children.extend(child.get_all_children())
        return children

    def deactivate(self):
        """カテゴリを無効化"""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def activate(self):
        """カテゴリを有効化"""
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def __repr__(self):
        return f'<Category {self.name}>'


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    cost = db.Column(db.Numeric(10, 2))
    stock_quantity = db.Column(db.Integer, default=0, nullable=False)
    min_stock_level = db.Column(db.Integer, default=0, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __init__(self, name, sku, price, category_id, description=None, cost=None,
                 stock_quantity=0, min_stock_level=0):
        self.name = name
        self.description = description
        self.sku = sku
        self.price = price
        self.cost = cost
        self.stock_quantity = stock_quantity
        self.min_stock_level = min_stock_level
        self.category_id = category_id
        self.is_active = True
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    @property
    def is_low_stock(self):
        """在庫が最小レベルを下回っているかチェック"""
        return self.stock_quantity <= self.min_stock_level

    @property
    def profit_margin(self):
        """利益率を計算"""
        if self.cost and self.price > 0:
            return ((self.price - self.cost) / self.price) * 100
        return None

    @property
    def profit_amount(self):
        """利益額を計算"""
        if self.cost:
            return self.price - self.cost
        return None

    def update_stock(self, quantity):
        """在庫数量を更新"""
        self.stock_quantity = max(0, quantity)
        self.updated_at = datetime.utcnow()

    def add_stock(self, quantity):
        """在庫を追加"""
        if quantity > 0:
            self.stock_quantity += quantity
            self.updated_at = datetime.utcnow()

    def reduce_stock(self, quantity):
        """在庫を減らす"""
        if quantity > 0 and self.stock_quantity >= quantity:
            self.stock_quantity -= quantity
            self.updated_at = datetime.utcnow()
            return True
        return False

    def update_info(self, **kwargs):
        """製品情報を更新"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['id', 'created_at']:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()

    def deactivate(self):
        """製品を無効化"""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def activate(self):
        """製品を有効化"""
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def __repr__(self):
        return f'<Product {self.name} ({self.sku})>'