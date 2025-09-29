"""
Category model for product categorization with hierarchical support
"""
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func, select
from . import db


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

    @hybrid_property
    def product_count(self):
        """このカテゴリの製品数を取得"""
        from .product import Product  # Avoid circular import
        return Product.query.filter_by(category_id=self.id, is_active=True).count()

    @product_count.expression
    def product_count(cls):
        """SQLクエリで使用する場合の製品数計算"""
        from .product import Product  # Avoid circular import
        return (
            select([func.count(Product.id)])
            .where(Product.category_id == cls.id)
            .where(Product.is_active == True)
            .label('product_count')
        )

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