"""
Tests for Product and Category models

Test coverage for model functionality, relationships, and business logic.
"""
import pytest
from datetime import datetime
from decimal import Decimal
from models import db, Product, Category
from product_config import ProductConfig


class TestCategoryModel:
    """Test cases for Category model"""

    def test_category_creation(self, app):
        """Test basic category creation"""
        with app.app_context():
            category = Category(
                name="Electronics",
                description="Electronic devices and accessories"
            )
            db.session.add(category)
            db.session.commit()

            assert category.id is not None
            assert category.name == "Electronics"
            assert category.description == "Electronic devices and accessories"
            assert category.parent_id is None
            assert category.is_active is True
            assert isinstance(category.created_at, datetime)
            assert isinstance(category.updated_at, datetime)

    def test_category_hierarchy(self, app):
        """Test hierarchical category relationships"""
        with app.app_context():
            # Create parent category
            parent = Category(name="Electronics")
            db.session.add(parent)
            db.session.commit()

            # Create child category
            child = Category(name="Smartphones", parent_id=parent.id)
            db.session.add(child)
            db.session.commit()

            # Test relationships
            assert child.parent == parent
            assert child in parent.children
            assert child.full_path == "Electronics > Smartphones"
            assert parent.full_path == "Electronics"

    def test_category_full_path_multilevel(self, app):
        """Test full path for multi-level hierarchies"""
        with app.app_context():
            # Create 3-level hierarchy
            level1 = Category(name="Electronics")
            db.session.add(level1)
            db.session.commit()

            level2 = Category(name="Mobile Devices", parent_id=level1.id)
            db.session.add(level2)
            db.session.commit()

            level3 = Category(name="Smartphones", parent_id=level2.id)
            db.session.add(level3)
            db.session.commit()

            assert level3.full_path == "Electronics > Mobile Devices > Smartphones"

    def test_category_get_all_children(self, app):
        """Test recursive children retrieval"""
        with app.app_context():
            # Create hierarchy
            parent = Category(name="Electronics")
            db.session.add(parent)
            db.session.commit()

            child1 = Category(name="Smartphones", parent_id=parent.id)
            child2 = Category(name="Laptops", parent_id=parent.id)
            db.session.add_all([child1, child2])
            db.session.commit()

            grandchild = Category(name="Gaming Laptops", parent_id=child2.id)
            db.session.add(grandchild)
            db.session.commit()

            all_children = parent.get_all_children()
            assert len(all_children) == 3
            assert child1 in all_children
            assert child2 in all_children
            assert grandchild in all_children

    def test_category_deactivate(self, app):
        """Test category deactivation"""
        with app.app_context():
            category = Category(name="Test Category")
            db.session.add(category)
            db.session.commit()

            assert category.is_active is True

            category.deactivate()
            assert category.is_active is False

    def test_category_activate(self, app):
        """Test category activation"""
        with app.app_context():
            category = Category(name="Test Category")
            category.is_active = False
            db.session.add(category)
            db.session.commit()

            category.activate()
            assert category.is_active is True

    def test_category_repr(self, app):
        """Test category string representation"""
        with app.app_context():
            category = Category(name="Test Category")
            assert str(category) == "<Category Test Category>"


class TestProductModel:
    """Test cases for Product model"""

    def test_product_creation(self, app):
        """Test basic product creation"""
        with app.app_context():
            # Create category first
            category = Category(name="Electronics")
            db.session.add(category)
            db.session.commit()

            # Create product
            product = Product(
                name="iPhone 15",
                sku="IPHONE-15-128GB",
                price=Decimal("999.00"),
                category_id=category.id,
                description="Latest iPhone model",
                cost=Decimal("700.00"),
                stock_quantity=50,
                min_stock_level=10
            )
            db.session.add(product)
            db.session.commit()

            assert product.id is not None
            assert product.name == "iPhone 15"
            assert product.sku == "IPHONE-15-128GB"
            assert product.price == Decimal("999.00")
            assert product.cost == Decimal("700.00")
            assert product.category_id == category.id
            assert product.category == category
            assert product.stock_quantity == 50
            assert product.min_stock_level == 10
            assert product.is_active is True

    def test_product_is_low_stock(self, app):
        """Test low stock detection"""
        with app.app_context():
            category = Category(name="Test")
            db.session.add(category)
            db.session.commit()

            # Product with stock above minimum
            product1 = Product(
                name="Product 1", sku="P1", price=100,
                category_id=category.id, stock_quantity=20, min_stock_level=10
            )

            # Product with stock at minimum
            product2 = Product(
                name="Product 2", sku="P2", price=100,
                category_id=category.id, stock_quantity=10, min_stock_level=10
            )

            # Product with stock below minimum
            product3 = Product(
                name="Product 3", sku="P3", price=100,
                category_id=category.id, stock_quantity=5, min_stock_level=10
            )

            assert product1.is_low_stock is False
            assert product2.is_low_stock is True
            assert product3.is_low_stock is True

    def test_product_profit_calculations(self, app):
        """Test profit margin and amount calculations"""
        with app.app_context():
            category = Category(name="Test")
            db.session.add(category)
            db.session.commit()

            # Product with cost
            product = Product(
                name="Test Product", sku="TEST", price=Decimal("100.00"),
                category_id=category.id, cost=Decimal("70.00")
            )

            assert product.profit_amount == Decimal("30.00")
            assert product.profit_margin == 30.0

            # Product without cost
            product_no_cost = Product(
                name="Test Product 2", sku="TEST2", price=Decimal("100.00"),
                category_id=category.id
            )

            assert product_no_cost.profit_amount is None
            assert product_no_cost.profit_margin is None

    def test_product_stock_operations(self, app):
        """Test stock management operations"""
        with app.app_context():
            category = Category(name="Test")
            db.session.add(category)
            db.session.commit()

            product = Product(
                name="Test Product", sku="TEST", price=100,
                category_id=category.id, stock_quantity=20
            )

            # Test update_stock
            product.update_stock(30)
            assert product.stock_quantity == 30

            # Test update_stock with negative value (should set to 0)
            product.update_stock(-5)
            assert product.stock_quantity == 0

            # Test add_stock
            product.add_stock(15)
            assert product.stock_quantity == 15

            # Test add_stock with negative value (should not change)
            original_quantity = product.stock_quantity
            product.add_stock(-5)
            assert product.stock_quantity == original_quantity

            # Test reduce_stock
            success = product.reduce_stock(10)
            assert success is True
            assert product.stock_quantity == 5

            # Test reduce_stock with insufficient stock
            success = product.reduce_stock(10)
            assert success is False
            assert product.stock_quantity == 5

    def test_product_update_info(self, app):
        """Test product information update"""
        with app.app_context():
            category = Category(name="Test")
            db.session.add(category)
            db.session.commit()

            product = Product(
                name="Original Name", sku="ORIG", price=100,
                category_id=category.id
            )
            db.session.add(product)
            db.session.commit()

            # Update product info
            product.update_info(
                name="Updated Name",
                price=Decimal("150.00"),
                description="Updated description"
            )

            assert product.name == "Updated Name"
            assert product.price == Decimal("150.00")
            assert product.description == "Updated description"
            assert product.sku == "ORIG"  # Should remain unchanged

    def test_product_deactivate_activate(self, app):
        """Test product deactivation and activation"""
        with app.app_context():
            category = Category(name="Test")
            db.session.add(category)
            db.session.commit()

            product = Product(
                name="Test Product", sku="TEST", price=100,
                category_id=category.id
            )
            db.session.add(product)
            db.session.commit()

            assert product.is_active is True

            product.deactivate()
            assert product.is_active is False

            product.activate()
            assert product.is_active is True

    def test_product_category_relationship(self, app):
        """Test product-category relationship"""
        with app.app_context():
            category = Category(name="Electronics")
            db.session.add(category)
            db.session.commit()

            product = Product(
                name="Test Product", sku="TEST", price=100,
                category_id=category.id
            )
            db.session.add(product)
            db.session.commit()

            # Test relationship
            assert product.category == category
            assert product in category.products

    def test_product_repr(self, app):
        """Test product string representation"""
        with app.app_context():
            category = Category(name="Test")
            db.session.add(category)
            db.session.commit()

            product = Product(
                name="Test Product", sku="TEST-001", price=100,
                category_id=category.id
            )

            assert str(product) == "<Product Test Product (TEST-001)>"


class TestProductCategoryIntegration:
    """Test integration between Product and Category models"""

    def test_category_product_count(self, app):
        """Test category product count property"""
        with app.app_context():
            category = Category(name="Electronics")
            db.session.add(category)
            db.session.commit()

            # Add active products
            product1 = Product(
                name="Product 1", sku="P1", price=100, category_id=category.id
            )
            product2 = Product(
                name="Product 2", sku="P2", price=200, category_id=category.id
            )
            db.session.add_all([product1, product2])
            db.session.commit()

            assert category.product_count == 2

            # Deactivate one product
            product1.deactivate()
            db.session.commit()

            # Should only count active products
            assert category.product_count == 1

    def test_cascade_operations(self, app):
        """Test that category operations properly handle products"""
        with app.app_context():
            category = Category(name="Test Category")
            db.session.add(category)
            db.session.commit()

            product = Product(
                name="Test Product", sku="TEST", price=100,
                category_id=category.id
            )
            db.session.add(product)
            db.session.commit()

            # Verify relationship works both ways
            assert product.category == category
            assert product in category.products