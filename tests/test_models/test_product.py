"""
Test cases for Product model
"""
import pytest
from models import Product, Category
from decimal import Decimal


class TestProductModel:
    """Test Product model functionality"""

    def test_product_creation(self, db_session, sample_category):
        """Test product creation with required fields"""
        product = Product(
            name='テスト製品',
            sku='TEST-001',
            price=1000.00,
            category_id=sample_category.id
        )
        db_session.add(product)
        db_session.commit()

        assert product.id is not None
        assert product.name == 'テスト製品'
        assert product.sku == 'TEST-001'
        assert product.price == Decimal('1000.00')
        assert product.category_id == sample_category.id
        assert product.is_active is True
        assert product.stock_quantity == 0
        assert product.min_stock_level == 0

    def test_product_with_optional_fields(self, db_session, sample_category):
        """Test product creation with optional fields"""
        product = Product(
            name='詳細テスト製品',
            sku='TEST-002',
            price=2000.00,
            category_id=sample_category.id,
            description='テスト用製品の詳細説明',
            cost=1500.00,
            stock_quantity=50,
            min_stock_level=5
        )
        db_session.add(product)
        db_session.commit()

        assert product.description == 'テスト用製品の詳細説明'
        assert product.cost == Decimal('1500.00')
        assert product.stock_quantity == 50
        assert product.min_stock_level == 5

    def test_is_low_stock_property(self, sample_product):
        """Test is_low_stock property"""
        # Initial state: 100 > 10 (not low stock)
        assert not sample_product.is_low_stock

        # Update to low stock: 5 <= 10 (low stock)
        sample_product.stock_quantity = 5
        assert sample_product.is_low_stock

        # Update to exact minimum: 10 <= 10 (low stock)
        sample_product.stock_quantity = 10
        assert sample_product.is_low_stock

    def test_profit_margin_calculation(self, sample_product):
        """Test profit margin calculation"""
        # Sample product: price=1000, cost=800
        # Expected margin: ((1000-800)/1000) * 100 = 20%
        assert sample_product.profit_margin == 20.0

        # Test with no cost
        sample_product.cost = None
        assert sample_product.profit_margin is None

        # Test with zero price
        sample_product.price = 0
        sample_product.cost = 500
        assert sample_product.profit_margin is None

    def test_profit_amount_calculation(self, sample_product):
        """Test profit amount calculation"""
        # Sample product: price=1000, cost=800
        # Expected profit: 1000 - 800 = 200
        assert sample_product.profit_amount == Decimal('200.00')

        # Test with no cost
        sample_product.cost = None
        assert sample_product.profit_amount is None

    def test_update_stock(self, sample_product):
        """Test stock quantity update"""
        initial_stock = sample_product.stock_quantity

        # Normal update
        sample_product.update_stock(75)
        assert sample_product.stock_quantity == 75

        # Negative quantity should be set to 0
        sample_product.update_stock(-10)
        assert sample_product.stock_quantity == 0

    def test_add_stock(self, sample_product):
        """Test adding stock"""
        initial_stock = sample_product.stock_quantity

        # Add positive stock
        sample_product.add_stock(25)
        assert sample_product.stock_quantity == initial_stock + 25

        # Adding zero or negative should not change stock
        sample_product.add_stock(0)
        assert sample_product.stock_quantity == initial_stock + 25

        sample_product.add_stock(-5)
        assert sample_product.stock_quantity == initial_stock + 25

    def test_reduce_stock(self, sample_product):
        """Test reducing stock"""
        initial_stock = sample_product.stock_quantity  # 100

        # Successful reduction
        result = sample_product.reduce_stock(30)
        assert result is True
        assert sample_product.stock_quantity == initial_stock - 30

        # Insufficient stock
        result = sample_product.reduce_stock(100)  # Trying to reduce more than available
        assert result is False
        assert sample_product.stock_quantity == initial_stock - 30  # Unchanged

        # Zero reduction
        result = sample_product.reduce_stock(0)
        assert result is False

    def test_update_info(self, sample_product):
        """Test product info update"""
        original_created_at = sample_product.created_at

        sample_product.update_info(
            name='更新された製品名',
            description='更新された説明',
            price=1500.00
        )

        assert sample_product.name == '更新された製品名'
        assert sample_product.description == '更新された説明'
        assert sample_product.price == Decimal('1500.00')
        assert sample_product.created_at == original_created_at  # Should not change
        assert sample_product.updated_at > original_created_at

    def test_deactivate_activate(self, sample_product):
        """Test product deactivation and activation"""
        # Initial state
        assert sample_product.is_active is True

        # Deactivate
        sample_product.deactivate()
        assert sample_product.is_active is False

        # Activate
        sample_product.activate()
        assert sample_product.is_active is True

    def test_product_category_relationship(self, db_session, sample_category):
        """Test relationship between product and category"""
        product = Product(
            name='関連テスト製品',
            sku='REL-001',
            price=500.00,
            category_id=sample_category.id
        )
        db_session.add(product)
        db_session.commit()

        # Test relationship
        assert product.category == sample_category
        assert product in sample_category.products

    def test_product_str_representation(self, sample_product):
        """Test string representation of product"""
        expected = f'<Product {sample_product.name} ({sample_product.sku})>'
        assert str(sample_product) == expected