"""
Product model for product inventory and management
"""
from datetime import datetime
from . import db


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