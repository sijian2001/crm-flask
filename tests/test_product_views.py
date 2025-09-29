"""
Tests for Product and Category views

Test coverage for route handlers, request processing, and response validation.
"""
import pytest
from decimal import Decimal
from flask import url_for
from models import db, Product, Category, User
from services.product_service import ProductService, CategoryService


class TestProductViews:
    """Test cases for product views"""

    def test_product_index_get(self, client, auth_user):
        """Test product index page GET request"""
        with client.application.app_context():
            category = Category(name='Electronics')
            db.session.add(category)
            db.session.commit()

            product = Product(
                name='Test Product',
                sku='TEST-001',
                price=100,
                category_id=category.id,
                stock_quantity=10,
                min_stock_level=5
            )
            db.session.add(product)
            db.session.commit()

        # Login and access product index
        auth_user.login()
        response = client.get(url_for('products.index'))

        assert response.status_code == 200
        assert 'Test Product' in response.get_data(as_text=True)
        assert 'TEST-001' in response.get_data(as_text=True)

    def test_product_index_search(self, client, auth_user):
        """Test product index with search"""
        with client.application.app_context():
            category = Category(name='Electronics')
            db.session.add(category)
            db.session.commit()

            product1 = Product(
                name='iPhone 15', sku='IPHONE15', price=999,
                category_id=category.id
            )
            product2 = Product(
                name='Samsung Galaxy', sku='SAMSUNG', price=899,
                category_id=category.id
            )
            db.session.add_all([product1, product2])
            db.session.commit()

        auth_user.login()
        response = client.get(url_for('products.index'), query_string={'search': 'iPhone'})

        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        assert 'iPhone 15' in response_text
        assert 'Samsung Galaxy' not in response_text

    def test_product_index_category_filter(self, client, auth_user):
        """Test product index with category filter"""
        with client.application.app_context():
            category1 = Category(name='Electronics')
            category2 = Category(name='Books')
            db.session.add_all([category1, category2])
            db.session.commit()

            product1 = Product(
                name='Phone', sku='PHONE', price=500, category_id=category1.id
            )
            product2 = Product(
                name='Novel', sku='NOVEL', price=20, category_id=category2.id
            )
            db.session.add_all([product1, product2])
            db.session.commit()

        auth_user.login()
        response = client.get(
            url_for('products.index'),
            query_string={'category_id': category1.id}
        )

        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        assert 'Phone' in response_text
        assert 'Novel' not in response_text

    def test_product_create_get(self, client, auth_user):
        """Test product create page GET request"""
        auth_user.login()
        response = client.get(url_for('products.create'))

        assert response.status_code == 200
        assert '製品新規登録' in response.get_data(as_text=True)

    def test_product_create_post_success(self, client, auth_user):
        """Test successful product creation"""
        with client.application.app_context():
            category = Category(name='Electronics')
            db.session.add(category)
            db.session.commit()
            category_id = category.id

        auth_user.login()
        response = client.post(url_for('products.create'), data={
            'name': 'New Product',
            'sku': 'NEW-001',
            'price': '299.99',
            'cost': '200.00',
            'category_id': category_id,
            'stock_quantity': '20',
            'min_stock_level': '5',
            'description': 'A new product',
            'submit': 'Submit'
        })

        # Should redirect to product view page
        assert response.status_code == 302

        # Verify product was created
        with client.application.app_context():
            product = Product.query.filter_by(sku='NEW-001').first()
            assert product is not None
            assert product.name == 'New Product'
            assert product.price == Decimal('299.99')

    def test_product_create_post_invalid_data(self, client, auth_user):
        """Test product creation with invalid data"""
        auth_user.login()
        response = client.post(url_for('products.create'), data={
            'name': '',  # Missing required field
            'sku': 'INVALID@SKU',  # Invalid characters
            'price': '-100',  # Negative price
            'category_id': '0',  # No category selected
            'submit': 'Submit'
        })

        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        assert '製品名を入力してください' in response_text
        assert '英数字、ハイフン、アンダースコアのみ使用可能です' in response_text

    def test_product_view(self, client, auth_user):
        """Test product detail view"""
        with client.application.app_context():
            category = Category(name='Electronics')
            db.session.add(category)
            db.session.commit()

            product = Product(
                name='Test Product',
                sku='TEST-001',
                price=100,
                category_id=category.id,
                description='Test description',
                stock_quantity=15,
                min_stock_level=5
            )
            db.session.add(product)
            db.session.commit()
            product_id = product.id

        auth_user.login()
        response = client.get(url_for('products.view', id=product_id))

        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        assert 'Test Product' in response_text
        assert 'TEST-001' in response_text
        assert 'Test description' in response_text

    def test_product_view_not_found(self, client, auth_user):
        """Test product view with non-existent product"""
        auth_user.login()
        response = client.get(url_for('products.view', id=99999))

        assert response.status_code == 404

    def test_product_edit_get(self, client, auth_user):
        """Test product edit page GET request"""
        with client.application.app_context():
            category = Category(name='Electronics')
            db.session.add(category)
            db.session.commit()

            product = Product(
                name='Test Product',
                sku='TEST-001',
                price=100,
                category_id=category.id
            )
            db.session.add(product)
            db.session.commit()
            product_id = product.id

        auth_user.login()
        response = client.get(url_for('products.edit', id=product_id))

        assert response.status_code == 200
        assert '製品編集' in response.get_data(as_text=True)

    def test_product_edit_post_success(self, client, auth_user):
        """Test successful product edit"""
        with client.application.app_context():
            category = Category(name='Electronics')
            db.session.add(category)
            db.session.commit()

            product = Product(
                name='Original Name',
                sku='ORIG-001',
                price=100,
                category_id=category.id,
                stock_quantity=10,
                min_stock_level=5
            )
            db.session.add(product)
            db.session.commit()
            product_id = product.id
            category_id = category.id

        auth_user.login()
        response = client.post(url_for('products.edit', id=product_id), data={
            'name': 'Updated Name',
            'sku': 'ORIG-001',
            'price': '150.00',
            'category_id': category_id,
            'stock_quantity': '15',
            'min_stock_level': '5',
            'submit': 'Submit'
        })

        assert response.status_code == 302

        # Verify product was updated
        with client.application.app_context():
            product = Product.query.get(product_id)
            assert product.name == 'Updated Name'
            assert product.price == Decimal('150.00')

    def test_product_delete(self, client, auth_user):
        """Test product deletion (deactivation)"""
        with client.application.app_context():
            category = Category(name='Electronics')
            db.session.add(category)
            db.session.commit()

            product = Product(
                name='Test Product',
                sku='TEST-001',
                price=100,
                category_id=category.id
            )
            db.session.add(product)
            db.session.commit()
            product_id = product.id

        auth_user.login()
        response = client.post(url_for('products.delete', id=product_id))

        assert response.status_code == 302

        # Verify product was deactivated
        with client.application.app_context():
            product = Product.query.get(product_id)
            assert product.is_active is False

    def test_product_activate(self, client, auth_user):
        """Test product activation"""
        with client.application.app_context():
            category = Category(name='Electronics')
            db.session.add(category)
            db.session.commit()

            product = Product(
                name='Test Product',
                sku='TEST-001',
                price=100,
                category_id=category.id
            )
            product.is_active = False
            db.session.add(product)
            db.session.commit()
            product_id = product.id

        auth_user.login()
        response = client.post(url_for('products.activate', id=product_id))

        assert response.status_code == 302

        # Verify product was activated
        with client.application.app_context():
            product = Product.query.get(product_id)
            assert product.is_active is True

    def test_product_update_stock_get(self, client, auth_user):
        """Test stock update page GET request"""
        with client.application.app_context():
            category = Category(name='Electronics')
            db.session.add(category)
            db.session.commit()

            product = Product(
                name='Test Product',
                sku='TEST-001',
                price=100,
                category_id=category.id,
                stock_quantity=10
            )
            db.session.add(product)
            db.session.commit()
            product_id = product.id

        auth_user.login()
        response = client.get(url_for('products.update_stock', id=product_id))

        assert response.status_code == 200
        assert '在庫更新' in response.get_data(as_text=True)

    def test_product_update_stock_post(self, client, auth_user):
        """Test stock update POST request"""
        with client.application.app_context():
            category = Category(name='Electronics')
            db.session.add(category)
            db.session.commit()

            product = Product(
                name='Test Product',
                sku='TEST-001',
                price=100,
                category_id=category.id,
                stock_quantity=10
            )
            db.session.add(product)
            db.session.commit()
            product_id = product.id

        auth_user.login()
        response = client.post(url_for('products.update_stock', id=product_id), data={
            'stock_quantity': '25',
            'submit': 'Submit'
        })

        assert response.status_code == 302

        # Verify stock was updated
        with client.application.app_context():
            product = Product.query.get(product_id)
            assert product.stock_quantity == 25


class TestCategoryViews:
    """Test cases for category views"""

    def test_categories_index_get(self, client, auth_user):
        """Test categories index page GET request"""
        with client.application.app_context():
            category = Category(name='Electronics')
            db.session.add(category)
            db.session.commit()

        auth_user.login()
        response = client.get(url_for('products.categories_index'))

        assert response.status_code == 200
        assert 'Electronics' in response.get_data(as_text=True)

    def test_category_create_get(self, client, auth_user):
        """Test category create page GET request"""
        auth_user.login()
        response = client.get(url_for('products.create_category'))

        assert response.status_code == 200
        assert 'カテゴリ新規作成' in response.get_data(as_text=True)

    def test_category_create_post_success(self, client, auth_user):
        """Test successful category creation"""
        auth_user.login()
        response = client.post(url_for('products.create_category'), data={
            'name': 'New Category',
            'description': 'A new category',
            'parent_id': '0',
            'submit': 'Submit'
        })

        assert response.status_code == 302

        # Verify category was created
        with client.application.app_context():
            category = Category.query.filter_by(name='New Category').first()
            assert category is not None
            assert category.description == 'A new category'

    def test_category_view(self, client, auth_user):
        """Test category detail view"""
        with client.application.app_context():
            category = Category(name='Electronics', description='Electronic devices')
            db.session.add(category)
            db.session.commit()
            category_id = category.id

        auth_user.login()
        response = client.get(url_for('products.view_category', id=category_id))

        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        assert 'Electronics' in response_text
        assert 'Electronic devices' in response_text

    def test_category_edit_get(self, client, auth_user):
        """Test category edit page GET request"""
        with client.application.app_context():
            category = Category(name='Electronics')
            db.session.add(category)
            db.session.commit()
            category_id = category.id

        auth_user.login()
        response = client.get(url_for('products.edit_category', id=category_id))

        assert response.status_code == 200
        assert 'カテゴリ編集' in response.get_data(as_text=True)

    def test_category_edit_post_success(self, client, auth_user):
        """Test successful category edit"""
        with client.application.app_context():
            category = Category(name='Original Name')
            db.session.add(category)
            db.session.commit()
            category_id = category.id

        auth_user.login()
        response = client.post(url_for('products.edit_category', id=category_id), data={
            'name': 'Updated Name',
            'description': 'Updated description',
            'parent_id': '0',
            'submit': 'Submit'
        })

        assert response.status_code == 302

        # Verify category was updated
        with client.application.app_context():
            category = Category.query.get(category_id)
            assert category.name == 'Updated Name'
            assert category.description == 'Updated description'

    def test_category_delete_success(self, client, auth_user):
        """Test successful category deletion"""
        with client.application.app_context():
            category = Category(name='Empty Category')
            db.session.add(category)
            db.session.commit()
            category_id = category.id

        auth_user.login()
        response = client.post(url_for('products.delete_category', id=category_id))

        assert response.status_code == 302

        # Verify category was deactivated
        with client.application.app_context():
            category = Category.query.get(category_id)
            assert category.is_active is False

    def test_category_delete_with_products(self, client, auth_user):
        """Test category deletion with existing products"""
        with client.application.app_context():
            category = Category(name='Category with Products')
            db.session.add(category)
            db.session.commit()

            product = Product(
                name='Product',
                sku='PROD-001',
                price=100,
                category_id=category.id
            )
            db.session.add(product)
            db.session.commit()
            category_id = category.id

        auth_user.login()
        response = client.post(url_for('products.delete_category', id=category_id))

        # Should redirect back to category view with error
        assert response.status_code == 302

        # Verify category was NOT deactivated
        with client.application.app_context():
            category = Category.query.get(category_id)
            assert category.is_active is True


class TestProductViewsAuth:
    """Test authentication requirements for product views"""

    def test_product_views_require_auth(self, client):
        """Test that product views require authentication"""
        # Test various endpoints without authentication
        endpoints = [
            'products.index',
            'products.create',
            'products.categories_index',
            'products.create_category'
        ]

        for endpoint in endpoints:
            response = client.get(url_for(endpoint))
            # Should redirect to login page
            assert response.status_code == 302
            assert '/auth/login' in response.location

    def test_product_detail_views_require_auth(self, client):
        """Test that product detail views require authentication"""
        with client.application.app_context():
            category = Category(name='Test')
            db.session.add(category)
            db.session.commit()

            product = Product(
                name='Test Product',
                sku='TEST',
                price=100,
                category_id=category.id
            )
            db.session.add(product)
            db.session.commit()
            product_id = product.id
            category_id = category.id

        # Test endpoints that require specific IDs
        endpoints_with_ids = [
            ('products.view', {'id': product_id}),
            ('products.edit', {'id': product_id}),
            ('products.update_stock', {'id': product_id}),
            ('products.view_category', {'id': category_id}),
            ('products.edit_category', {'id': category_id})
        ]

        for endpoint, kwargs in endpoints_with_ids:
            response = client.get(url_for(endpoint, **kwargs))
            assert response.status_code == 302
            assert '/auth/login' in response.location