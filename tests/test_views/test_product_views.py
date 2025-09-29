"""
Test cases for Product views
"""
import pytest
from flask import url_for
from models import Product, Category


class TestProductViews:
    """Test Product view functionality"""

    def test_product_index_requires_auth(self, client):
        """Test that product index requires authentication"""
        response = client.get('/products/')
        assert response.status_code == 302
        assert '/auth/login' in response.location

    def test_product_index_authenticated(self, authenticated_client, db_session, sample_product):
        """Test product index with authenticated user"""
        response = authenticated_client.get('/products/')
        assert response.status_code == 200
        assert sample_product.name.encode() in response.data
        assert 'CRM システム'.encode() in response.data

    def test_product_view_detail(self, authenticated_client, db_session, sample_product):
        """Test product detail view"""
        response = authenticated_client.get(f'/products/{sample_product.id}')
        assert response.status_code == 200
        assert sample_product.name.encode() in response.data
        assert sample_product.sku.encode() in response.data
        assert str(sample_product.price).encode() in response.data

    def test_product_view_not_found(self, authenticated_client, db_session):
        """Test product detail view with non-existent product"""
        response = authenticated_client.get('/products/99999')
        assert response.status_code == 404

    def test_product_create_get(self, authenticated_client, db_session):
        """Test product creation form display"""
        response = authenticated_client.get('/products/create')
        assert response.status_code == 200
        assert '製品作成'.encode() in response.data or '新規製品'.encode() in response.data

    def test_product_create_post_success(self, authenticated_client, db_session, sample_category):
        """Test successful product creation"""
        data = {
            'name': '新規テスト製品',
            'sku': 'NEW-TEST-001',
            'price': '1500.00',
            'category_id': sample_category.id,
            'description': '新規作成のテスト製品',
            'cost': '1200.00',
            'stock_quantity': '50',
            'min_stock_level': '5'
        }
        response = authenticated_client.post('/products/create', data=data, follow_redirects=True)
        assert response.status_code == 200

        # Check if product was created
        product = Product.query.filter_by(sku='NEW-TEST-001').first()
        assert product is not None
        assert product.name == '新規テスト製品'

    def test_product_create_post_duplicate_sku(self, authenticated_client, db_session, sample_product):
        """Test product creation with duplicate SKU"""
        data = {
            'name': '重複SKU製品',
            'sku': sample_product.sku,  # Duplicate SKU
            'price': '1000.00',
            'category_id': sample_product.category_id
        }
        response = authenticated_client.post('/products/create', data=data)
        assert response.status_code == 200
        # Should stay on create page with error

    def test_product_edit_get(self, authenticated_client, db_session, sample_product):
        """Test product edit form display"""
        response = authenticated_client.get(f'/products/{sample_product.id}/edit')
        assert response.status_code == 200
        assert sample_product.name.encode() in response.data

    def test_product_edit_post_success(self, authenticated_client, db_session, sample_product):
        """Test successful product edit"""
        data = {
            'name': '更新されたテスト製品',
            'sku': sample_product.sku,
            'price': '2000.00',
            'category_id': sample_product.category_id,
            'description': '更新された説明',
            'stock_quantity': str(sample_product.stock_quantity),
            'min_stock_level': str(sample_product.min_stock_level)
        }
        response = authenticated_client.post(f'/products/{sample_product.id}/edit',
                                           data=data, follow_redirects=True)
        assert response.status_code == 200

        # Check if product was updated
        db_session.refresh(sample_product)
        assert sample_product.name == '更新されたテスト製品'
        assert float(sample_product.price) == 2000.00

    def test_product_delete(self, authenticated_client, db_session, sample_product):
        """Test product deletion (deactivation)"""
        response = authenticated_client.post(f'/products/{sample_product.id}/delete',
                                           follow_redirects=True)
        assert response.status_code == 200

        # Check if product was deactivated
        db_session.refresh(sample_product)
        assert sample_product.is_active is False

    def test_product_activate(self, authenticated_client, db_session, sample_product):
        """Test product activation"""
        # First deactivate the product
        sample_product.is_active = False
        db_session.commit()

        response = authenticated_client.post(f'/products/{sample_product.id}/activate',
                                           follow_redirects=True)
        assert response.status_code == 200

        # Check if product was activated
        db_session.refresh(sample_product)
        assert sample_product.is_active is True

    def test_update_stock_get(self, authenticated_client, db_session, sample_product):
        """Test stock update form display"""
        response = authenticated_client.get(f'/products/{sample_product.id}/update_stock')
        assert response.status_code == 200
        assert str(sample_product.stock_quantity).encode() in response.data

    def test_update_stock_post_success(self, authenticated_client, db_session, sample_product):
        """Test successful stock update"""
        data = {
            'stock_quantity': '150'
        }
        response = authenticated_client.post(f'/products/{sample_product.id}/update_stock',
                                           data=data, follow_redirects=True)
        assert response.status_code == 200

        # Check if stock was updated
        db_session.refresh(sample_product)
        assert sample_product.stock_quantity == 150

    def test_product_search(self, authenticated_client, db_session, sample_category):
        """Test product search functionality"""
        # Create multiple products
        product1 = Product(
            name='検索テスト製品1', sku='SEARCH-001', price=1000.00,
            category_id=sample_category.id
        )
        product2 = Product(
            name='別の製品', sku='OTHER-001', price=2000.00,
            category_id=sample_category.id
        )
        db_session.add_all([product1, product2])
        db_session.commit()

        # Search for specific product
        response = authenticated_client.get('/products/?search=検索テスト')
        assert response.status_code == 200
        assert '検索テスト製品1'.encode() in response.data
        assert '別の製品'.encode() not in response.data

    def test_product_category_filter(self, authenticated_client, db_session):
        """Test product filtering by category"""
        # Create categories and products
        category1 = Category(name='カテゴリ1')
        category2 = Category(name='カテゴリ2')
        db_session.add_all([category1, category2])
        db_session.commit()

        product1 = Product(
            name='カテゴリ1製品', sku='CAT1-001', price=1000.00,
            category_id=category1.id
        )
        product2 = Product(
            name='カテゴリ2製品', sku='CAT2-001', price=2000.00,
            category_id=category2.id
        )
        db_session.add_all([product1, product2])
        db_session.commit()

        # Filter by category
        response = authenticated_client.get(f'/products/?category_id={category1.id}')
        assert response.status_code == 200
        assert 'カテゴリ1製品'.encode() in response.data
        assert 'カテゴリ2製品'.encode() not in response.data

    def test_low_stock_filter(self, authenticated_client, db_session, sample_category):
        """Test low stock filter"""
        # Create products with different stock levels
        low_stock = Product(
            name='低在庫製品', sku='LOW-001', price=100.00,
            category_id=sample_category.id, stock_quantity=3, min_stock_level=5
        )
        normal_stock = Product(
            name='通常在庫製品', sku='NORMAL-001', price=200.00,
            category_id=sample_category.id, stock_quantity=20, min_stock_level=5
        )
        db_session.add_all([low_stock, normal_stock])
        db_session.commit()

        # Filter for low stock only
        response = authenticated_client.get('/products/?low_stock_only=True')
        assert response.status_code == 200
        assert '低在庫製品'.encode() in response.data
        assert '通常在庫製品'.encode() not in response.data


class TestCategoryViews:
    """Test Category view functionality"""

    def test_category_index(self, authenticated_client, db_session, sample_category):
        """Test category index view"""
        response = authenticated_client.get('/products/categories/')
        assert response.status_code == 200
        assert sample_category.name.encode() in response.data

    def test_category_view_detail(self, authenticated_client, db_session, sample_category):
        """Test category detail view"""
        response = authenticated_client.get(f'/products/categories/{sample_category.id}')
        assert response.status_code == 200
        assert sample_category.name.encode() in response.data

    def test_category_create_get(self, authenticated_client, db_session):
        """Test category creation form display"""
        response = authenticated_client.get('/products/categories/create')
        assert response.status_code == 200
        assert 'カテゴリ作成'.encode() in response.data or '新規カテゴリ'.encode() in response.data

    def test_category_create_post_success(self, authenticated_client, db_session):
        """Test successful category creation"""
        data = {
            'name': '新規テストカテゴリ',
            'description': '新規作成のテストカテゴリです',
            'parent_id': '0'  # No parent
        }
        response = authenticated_client.post('/products/categories/create',
                                           data=data, follow_redirects=True)
        assert response.status_code == 200

        # Check if category was created
        category = Category.query.filter_by(name='新規テストカテゴリ').first()
        assert category is not None

    def test_category_edit_get(self, authenticated_client, db_session, sample_category):
        """Test category edit form display"""
        response = authenticated_client.get(f'/products/categories/{sample_category.id}/edit')
        assert response.status_code == 200
        assert sample_category.name.encode() in response.data

    def test_category_delete(self, authenticated_client, db_session, sample_category):
        """Test category deletion"""
        response = authenticated_client.post(f'/products/categories/{sample_category.id}/delete',
                                           follow_redirects=True)
        assert response.status_code == 200

        # Check if category was deactivated
        db_session.refresh(sample_category)
        assert sample_category.is_active is False