"""
Test cases for ProductService
"""
import pytest
from services import ProductService
from models import Product, Category


class TestProductService:
    """Test ProductService functionality"""

    def test_get_product_by_id(self, db_session, sample_product):
        """Test getting product by ID"""
        result = ProductService.get_product_by_id(sample_product.id)
        assert result == sample_product

        # Test non-existent ID
        result = ProductService.get_product_by_id(99999)
        assert result is None

    def test_get_product_by_sku(self, db_session, sample_product):
        """Test getting product by SKU"""
        result = ProductService.get_product_by_sku(sample_product.sku)
        assert result == sample_product

        # Test non-existent SKU
        result = ProductService.get_product_by_sku('NON-EXISTENT')
        assert result is None

        # Test inactive product should not be found
        sample_product.is_active = False
        db_session.commit()
        result = ProductService.get_product_by_sku(sample_product.sku)
        assert result is None

    def test_create_product_success(self, db_session, sample_category):
        """Test successful product creation"""
        success, product, error = ProductService.create_product(
            name='新規製品',
            sku='NEW-001',
            price=1500.00,
            category_id=sample_category.id,
            description='新規製品の説明',
            cost=1200.00,
            stock_quantity=50,
            min_stock_level=5
        )

        assert success is True
        assert product is not None
        assert error is None
        assert product.name == '新規製品'
        assert product.sku == 'NEW-001'
        assert product.price == 1500.00
        assert product.category_id == sample_category.id

    def test_create_product_duplicate_sku(self, db_session, sample_product):
        """Test product creation with duplicate SKU"""
        success, product, error = ProductService.create_product(
            name='重複SKU製品',
            sku=sample_product.sku,  # Duplicate SKU
            price=1000.00,
            category_id=sample_product.category_id
        )

        assert success is False
        assert product is None
        assert error == '指定されたSKUは既に使用されています。'

    def test_create_product_invalid_category(self, db_session):
        """Test product creation with invalid category"""
        success, product, error = ProductService.create_product(
            name='無効カテゴリ製品',
            sku='INVALID-001',
            price=1000.00,
            category_id=99999  # Non-existent category
        )

        assert success is False
        assert product is None
        assert error == '指定されたカテゴリが見つからないか、無効化されています。'

    def test_update_product_success(self, db_session, sample_product):
        """Test successful product update"""
        success, error = ProductService.update_product(
            product=sample_product,
            name='更新された製品名',
            price=2000.00,
            description='更新された説明'
        )

        assert success is True
        assert error is None
        assert sample_product.name == '更新された製品名'
        assert sample_product.price == 2000.00
        assert sample_product.description == '更新された説明'

    def test_update_product_inactive(self, db_session, sample_product):
        """Test updating inactive product"""
        sample_product.is_active = False
        db_session.commit()

        success, error = ProductService.update_product(
            product=sample_product,
            name='更新試行'
        )

        assert success is False
        assert error == '無効化された製品は編集できません。'

    def test_update_product_duplicate_sku(self, db_session, sample_category):
        """Test updating product with duplicate SKU"""
        # Create two products
        product1 = Product(
            name='製品1', sku='P001', price=100.00, category_id=sample_category.id
        )
        product2 = Product(
            name='製品2', sku='P002', price=200.00, category_id=sample_category.id
        )
        db_session.add_all([product1, product2])
        db_session.commit()

        # Try to update product2 with product1's SKU
        success, error = ProductService.update_product(
            product=product2,
            sku='P001'
        )

        assert success is False
        assert error == '指定されたSKUは既に使用されています。'

    def test_deactivate_product(self, db_session, sample_product):
        """Test product deactivation"""
        success, error = ProductService.deactivate_product(sample_product)

        assert success is True
        assert error is None
        assert sample_product.is_active is False

        # Test deactivating already inactive product
        success, error = ProductService.deactivate_product(sample_product)
        assert success is False
        assert error == '指定された製品は既に無効化されています。'

    def test_activate_product(self, db_session, sample_product):
        """Test product activation"""
        # First deactivate
        sample_product.is_active = False
        db_session.commit()

        success, error = ProductService.activate_product(sample_product)

        assert success is True
        assert error is None
        assert sample_product.is_active is True

        # Test activating already active product
        success, error = ProductService.activate_product(sample_product)
        assert success is False
        assert error == '指定された製品は既に有効化されています。'

    def test_update_stock_success(self, db_session, sample_product):
        """Test successful stock update"""
        success, error = ProductService.update_stock(sample_product, 150)

        assert success is True
        assert error is None
        assert sample_product.stock_quantity == 150

    def test_update_stock_inactive_product(self, db_session, sample_product):
        """Test updating stock of inactive product"""
        sample_product.is_active = False
        db_session.commit()

        success, error = ProductService.update_stock(sample_product, 150)

        assert success is False
        assert error == '無効化された製品の在庫は更新できません。'

    def test_update_stock_negative_quantity(self, db_session, sample_product):
        """Test updating stock with negative quantity"""
        success, error = ProductService.update_stock(sample_product, -10)

        assert success is False
        assert error == '在庫数量は0以上である必要があります。'

    def test_get_low_stock_products(self, db_session, sample_category):
        """Test getting low stock products"""
        # Create products with different stock levels
        low_stock = Product(
            name='低在庫製品', sku='LOW-001', price=100.00,
            category_id=sample_category.id, stock_quantity=3, min_stock_level=5
        )
        normal_stock = Product(
            name='通常在庫製品', sku='NORMAL-001', price=200.00,
            category_id=sample_category.id, stock_quantity=20, min_stock_level=5
        )
        exact_min = Product(
            name='最小在庫製品', sku='MIN-001', price=150.00,
            category_id=sample_category.id, stock_quantity=5, min_stock_level=5
        )
        db_session.add_all([low_stock, normal_stock, exact_min])
        db_session.commit()

        low_stock_products = ProductService.get_low_stock_products()
        low_stock_skus = [p.sku for p in low_stock_products]

        assert 'LOW-001' in low_stock_skus
        assert 'MIN-001' in low_stock_skus
        assert 'NORMAL-001' not in low_stock_skus

    def test_get_products_with_pagination(self, db_session, sample_category):
        """Test getting products with pagination"""
        # Create multiple products
        products = []
        for i in range(15):
            product = Product(
                name=f'製品{i+1}',
                sku=f'P{i+1:03d}',
                price=100.00 * (i + 1),
                category_id=sample_category.id
            )
            products.append(product)
        db_session.add_all(products)
        db_session.commit()

        # Test pagination
        pagination = ProductService.get_products_with_pagination(page=1, per_page=10)

        assert pagination.total == 15
        assert len(pagination.items) == 10
        assert pagination.pages == 2
        assert pagination.has_next is True

        # Test second page
        pagination = ProductService.get_products_with_pagination(page=2, per_page=10)
        assert len(pagination.items) == 5
        assert pagination.has_prev is True

    def test_get_products_with_search(self, db_session, sample_category):
        """Test getting products with search"""
        # Create products with different names
        product1 = Product(
            name='スマートフォン', sku='PHONE-001', price=50000.00,
            category_id=sample_category.id, description='最新のスマートフォンです'
        )
        product2 = Product(
            name='タブレット', sku='TABLET-001', price=30000.00,
            category_id=sample_category.id
        )
        db_session.add_all([product1, product2])
        db_session.commit()

        # Search by name
        pagination = ProductService.get_products_with_pagination(search='スマート')
        assert len(pagination.items) == 1
        assert pagination.items[0].name == 'スマートフォン'

        # Search by SKU
        pagination = ProductService.get_products_with_pagination(search='TABLET')
        assert len(pagination.items) == 1
        assert pagination.items[0].sku == 'TABLET-001'

        # Search by description
        pagination = ProductService.get_products_with_pagination(search='最新')
        assert len(pagination.items) == 1
        assert pagination.items[0].description == '最新のスマートフォンです'