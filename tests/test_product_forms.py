"""
Tests for Product and Category forms

Test coverage for form validation, field constraints, and user input handling.
"""
import pytest
from decimal import Decimal
from models import db, Product, Category
from forms import (
    ProductForm, CategoryForm, ProductSearchForm, CategorySearchForm,
    StockUpdateForm
)


class TestCategoryForm:
    """Test cases for category forms"""

    def test_category_form_valid_data(self, app):
        """Test category form with valid data"""
        with app.app_context():
            form = CategoryForm(data={
                'name': 'Electronics',
                'description': 'Electronic devices and accessories',
                'parent_id': 0
            })

            assert form.validate() is True

    def test_category_form_required_fields(self, app):
        """Test category form required field validation"""
        with app.app_context():
            # Missing name
            form = CategoryForm(data={
                'description': 'Some description',
                'parent_id': 0
            })

            assert form.validate() is False
            assert 'カテゴリ名を入力してください' in form.name.errors

    def test_category_form_name_length(self, app):
        """Test category form name length validation"""
        with app.app_context():
            # Name too long
            long_name = 'a' * 101  # Exceeds max length
            form = CategoryForm(data={
                'name': long_name,
                'parent_id': 0
            })

            assert form.validate() is False
            assert any('文字以下で入力してください' in error for error in form.name.errors)

    def test_category_form_description_length(self, app):
        """Test category form description length validation"""
        with app.app_context():
            # Description too long
            long_desc = 'a' * 1001  # Exceeds max length
            form = CategoryForm(data={
                'name': 'Valid Name',
                'description': long_desc,
                'parent_id': 0
            })

            assert form.validate() is False
            assert any('文字以下で入力してください' in error for error in form.description.errors)

    def test_category_form_parent_validation(self, app):
        """Test category form parent validation"""
        with app.app_context():
            # Create parent category
            parent = Category(name='Parent Category')
            db.session.add(parent)
            db.session.commit()

            # Valid parent
            form = CategoryForm(data={
                'name': 'Child Category',
                'parent_id': parent.id
            })

            assert form.validate() is True

            # Invalid parent
            form = CategoryForm(data={
                'name': 'Child Category',
                'parent_id': 99999
            })

            assert form.validate() is False
            assert '指定された親カテゴリが見つかりません' in form.parent_id.errors

    def test_category_form_edit_mode(self, app):
        """Test category form in edit mode"""
        with app.app_context():
            # Create categories
            parent = Category(name='Parent')
            category = Category(name='Category')
            child = Category(name='Child')
            db.session.add_all([parent, category, child])
            db.session.commit()

            # Set up parent-child relationship
            child.parent_id = category.id
            db.session.commit()

            # Edit form should exclude self and descendants from parent choices
            form = CategoryForm(category=category)

            # Check that category choices are properly set
            parent_choices = [choice[0] for choice in form.parent_id.choices]
            assert parent.id in parent_choices
            assert category.id not in parent_choices  # Self excluded
            assert child.id not in parent_choices     # Child excluded


class TestProductForm:
    """Test cases for product forms"""

    def test_product_form_valid_data(self, app):
        """Test product form with valid data"""
        with app.app_context():
            category = Category(name='Electronics')
            db.session.add(category)
            db.session.commit()

            form = ProductForm(data={
                'name': 'iPhone 15',
                'sku': 'IPHONE-15-128GB',
                'price': '999.00',
                'cost': '700.00',
                'category_id': category.id,
                'stock_quantity': 50,
                'min_stock_level': 10,
                'description': 'Latest iPhone model'
            })

            assert form.validate() is True

    def test_product_form_required_fields(self, app):
        """Test product form required field validation"""
        with app.app_context():
            form = ProductForm(data={})

            assert form.validate() is False
            assert '製品名を入力してください' in form.name.errors
            assert 'SKUを入力してください' in form.sku.errors
            assert '価格を入力してください' in form.price.errors
            assert 'カテゴリを選択してください' in form.category_id.errors
            assert '在庫数量を入力してください' in form.stock_quantity.errors
            assert '最小在庫レベルを入力してください' in form.min_stock_level.errors

    def test_product_form_name_length(self, app):
        """Test product form name length validation"""
        with app.app_context():
            category = Category(name='Electronics')
            db.session.add(category)
            db.session.commit()

            # Name too long
            long_name = 'a' * 201  # Exceeds max length
            form = ProductForm(data={
                'name': long_name,
                'sku': 'SKU123',
                'price': '100.00',
                'category_id': category.id,
                'stock_quantity': 10,
                'min_stock_level': 5
            })

            assert form.validate() is False
            assert any('文字以下で入力してください' in error for error in form.name.errors)

    def test_product_form_sku_validation(self, app):
        """Test product form SKU validation"""
        with app.app_context():
            category = Category(name='Electronics')
            db.session.add(category)
            db.session.commit()

            # Invalid SKU characters
            form = ProductForm(data={
                'name': 'Product',
                'sku': 'INVALID@SKU!',  # Contains invalid characters
                'price': '100.00',
                'category_id': category.id,
                'stock_quantity': 10,
                'min_stock_level': 5
            })

            assert form.validate() is False
            assert '英数字、ハイフン、アンダースコアのみ使用可能です' in form.sku.errors

    def test_product_form_sku_duplicate(self, app):
        """Test product form SKU duplicate validation"""
        with app.app_context():
            category = Category(name='Electronics')
            db.session.add(category)
            db.session.commit()

            # Create existing product
            existing_product = Product(
                name='Existing Product',
                sku='DUPLICATE-SKU',
                price=100,
                category_id=category.id
            )
            db.session.add(existing_product)
            db.session.commit()

            # Try to create new product with same SKU
            form = ProductForm(data={
                'name': 'New Product',
                'sku': 'DUPLICATE-SKU',
                'price': '200.00',
                'category_id': category.id,
                'stock_quantity': 10,
                'min_stock_level': 5
            })

            assert form.validate() is False
            assert 'このSKUは既に使用されています' in form.sku.errors

    def test_product_form_price_validation(self, app):
        """Test product form price validation"""
        with app.app_context():
            category = Category(name='Electronics')
            db.session.add(category)
            db.session.commit()

            # Negative price
            form = ProductForm(data={
                'name': 'Product',
                'sku': 'SKU123',
                'price': '-10.00',
                'category_id': category.id,
                'stock_quantity': 10,
                'min_stock_level': 5
            })

            assert form.validate() is False
            assert '価格は0以上である必要があります' in form.price.errors

    def test_product_form_category_validation(self, app):
        """Test product form category validation"""
        with app.app_context():
            # No category selected
            form = ProductForm(data={
                'name': 'Product',
                'sku': 'SKU123',
                'price': '100.00',
                'category_id': 0,  # No category selected
                'stock_quantity': 10,
                'min_stock_level': 5
            })

            assert form.validate() is False
            assert 'カテゴリを選択してください' in form.category_id.errors

            # Invalid category
            form = ProductForm(data={
                'name': 'Product',
                'sku': 'SKU123',
                'price': '100.00',
                'category_id': 99999,  # Non-existent category
                'stock_quantity': 10,
                'min_stock_level': 5
            })

            assert form.validate() is False
            assert '指定されたカテゴリが見つかりません' in form.category_id.errors

    def test_product_form_stock_validation(self, app):
        """Test product form stock validation"""
        with app.app_context():
            category = Category(name='Electronics')
            db.session.add(category)
            db.session.commit()

            # Negative stock
            form = ProductForm(data={
                'name': 'Product',
                'sku': 'SKU123',
                'price': '100.00',
                'category_id': category.id,
                'stock_quantity': -5,
                'min_stock_level': 5
            })

            assert form.validate() is False

            # Min stock level higher than current stock
            form = ProductForm(data={
                'name': 'Product',
                'sku': 'SKU123',
                'price': '100.00',
                'category_id': category.id,
                'stock_quantity': 5,
                'min_stock_level': 10
            })

            assert form.validate() is False
            assert '最小在庫レベルは現在の在庫数量以下である必要があります' in form.min_stock_level.errors

    def test_product_form_edit_mode(self, app):
        """Test product form in edit mode"""
        with app.app_context():
            category = Category(name='Electronics')
            db.session.add(category)
            db.session.commit()

            product = Product(
                name='Test Product',
                sku='TEST-SKU',
                price=100,
                category_id=category.id
            )
            db.session.add(product)
            db.session.commit()

            # Edit form should allow same SKU for the same product
            form = ProductForm(product=product, data={
                'name': 'Updated Product',
                'sku': 'TEST-SKU',  # Same SKU, should be valid
                'price': '150.00',
                'category_id': category.id,
                'stock_quantity': 20,
                'min_stock_level': 5
            })

            assert form.validate() is True


class TestSearchForms:
    """Test cases for search forms"""

    def test_product_search_form(self, app):
        """Test product search form"""
        with app.app_context():
            category = Category(name='Electronics')
            db.session.add(category)
            db.session.commit()

            form = ProductSearchForm(data={
                'search': 'iPhone',
                'category_id': category.id,
                'low_stock_only': True
            })

            # Search forms should always validate (all fields optional)
            assert form.validate() is True

    def test_category_search_form(self, app):
        """Test category search form"""
        with app.app_context():
            category = Category(name='Electronics')
            db.session.add(category)
            db.session.commit()

            form = CategorySearchForm(data={
                'search': 'Electronics',
                'parent_id': category.id
            })

            assert form.validate() is True

    def test_stock_update_form(self, app):
        """Test stock update form"""
        with app.app_context():
            # Valid stock quantity
            form = StockUpdateForm(data={
                'stock_quantity': 25
            })

            assert form.validate() is True

            # Negative stock quantity
            form = StockUpdateForm(data={
                'stock_quantity': -5
            })

            assert form.validate() is False

            # Missing stock quantity
            form = StockUpdateForm(data={})

            assert form.validate() is False
            assert '在庫数量を入力してください' in form.stock_quantity.errors


class TestFormIntegration:
    """Test form integration with models and configuration"""

    def test_form_uses_config_limits(self, app):
        """Test that forms use configuration limits"""
        with app.app_context():
            from product_config import ProductConfig

            # Forms should use configuration for validation limits
            form = ProductForm()

            # Check that form validators use config values
            name_validator = next(
                (v for v in form.name.validators if hasattr(v, 'max')), None
            )
            if name_validator:
                assert name_validator.max == ProductConfig.get_name_max_length()

    def test_form_category_choices_populated(self, app):
        """Test that category choices are properly populated"""
        with app.app_context():
            # Create categories
            parent = Category(name='Parent')
            child = Category(name='Child', parent_id=None)
            db.session.add_all([parent, child])
            db.session.commit()

            child.parent_id = parent.id
            db.session.commit()

            # Product form should have category choices
            form = ProductForm()
            category_choices = dict(form.category_id.choices)

            assert parent.id in category_choices
            assert child.id in category_choices
            assert category_choices[parent.id] == 'Parent'
            assert category_choices[child.id] == 'Parent > Child'

    def test_form_preserves_data_on_validation_error(self, app):
        """Test that form preserves user data on validation errors"""
        with app.app_context():
            form = ProductForm(data={
                'name': 'Test Product',
                'sku': 'INVALID@SKU',  # Invalid SKU
                'price': '100.00',
                'category_id': 0,  # Invalid category
                'stock_quantity': 10,
                'min_stock_level': 5
            })

            assert form.validate() is False

            # Form should preserve the data entered by user
            assert form.name.data == 'Test Product'
            assert form.sku.data == 'INVALID@SKU'
            assert form.price.data == Decimal('100.00')
            assert form.stock_quantity.data == 10