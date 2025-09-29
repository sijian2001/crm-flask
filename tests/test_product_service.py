"""
Tests for Product and Category service layers

Test coverage for business logic, validation, and service operations.
"""
import pytest
from decimal import Decimal
from models import db, Product, Category
from services.product_service import ProductService, CategoryService
from product_config import ProductConfig


class TestProductService:
    """Test cases for ProductService"""

    def test_get_products_with_pagination(self, app):
        """Test paginated product retrieval"""
        with app.app_context():
            category = Category(name="Electronics")
            db.session.add(category)
            db.session.commit()

            # Create test products
            products = []
            for i in range(25):
                product = Product(
                    name=f"Product {i}",
                    sku=f"SKU{i:03d}",
                    price=Decimal(f"{100 + i}.00"),
                    category_id=category.id,
                    stock_quantity=10 + i,
                    min_stock_level=5
                )
                products.append(product)

            db.session.add_all(products)
            db.session.commit()

            # Test pagination
            pagination = ProductService.get_products_with_pagination(page=1, per_page=10)
            assert len(pagination.items) == 10
            assert pagination.total == 25
            assert pagination.pages == 3

    def test_get_products_with_search(self, app):
        """Test product search functionality"""
        with app.app_context():
            category = Category(name="Electronics")
            db.session.add(category)
            db.session.commit()

            # Create test products
            product1 = Product(
                name="iPhone 15", sku="IPHONE15", price=999,
                category_id=category.id, description="Apple smartphone"
            )
            product2 = Product(
                name="Samsung Galaxy", sku="SAMSUNG", price=899,
                category_id=category.id, description="Android phone"
            )
            product3 = Product(
                name="Laptop Pro", sku="LAPTOP", price=1299,
                category_id=category.id, description="High-performance laptop"
            )

            db.session.add_all([product1, product2, product3])
            db.session.commit()

            # Test search by name
            pagination = ProductService.get_products_with_pagination(search="iPhone")
            assert len(pagination.items) == 1
            assert pagination.items[0].name == "iPhone 15"

            # Test search by SKU
            pagination = ProductService.get_products_with_pagination(search="SAMSUNG")
            assert len(pagination.items) == 1
            assert pagination.items[0].name == "Samsung Galaxy"

            # Test search by description
            pagination = ProductService.get_products_with_pagination(search="smartphone")
            assert len(pagination.items) == 1
            assert pagination.items[0].name == "iPhone 15"

    def test_get_products_with_category_filter(self, app):
        """Test product filtering by category"""
        with app.app_context():
            category1 = Category(name="Electronics")
            category2 = Category(name="Books")
            db.session.add_all([category1, category2])
            db.session.commit()

            product1 = Product(
                name="Phone", sku="PHONE", price=500, category_id=category1.id
            )
            product2 = Product(
                name="Novel", sku="NOVEL", price=20, category_id=category2.id
            )

            db.session.add_all([product1, product2])
            db.session.commit()

            # Test category filter
            pagination = ProductService.get_products_with_pagination(category_id=category1.id)
            assert len(pagination.items) == 1
            assert pagination.items[0].name == "Phone"

    def test_get_products_low_stock_filter(self, app):
        """Test low stock product filtering"""
        with app.app_context():
            category = Category(name="Electronics")
            db.session.add(category)
            db.session.commit()

            # Normal stock product
            product1 = Product(
                name="Product 1", sku="P1", price=100,
                category_id=category.id, stock_quantity=20, min_stock_level=10
            )
            # Low stock product
            product2 = Product(
                name="Product 2", sku="P2", price=100,
                category_id=category.id, stock_quantity=5, min_stock_level=10
            )

            db.session.add_all([product1, product2])
            db.session.commit()

            # Test low stock filter
            pagination = ProductService.get_products_with_pagination(low_stock_only=True)
            assert len(pagination.items) == 1
            assert pagination.items[0].name == "Product 2"

    def test_get_product_by_id(self, app):
        """Test product retrieval by ID"""
        with app.app_context():
            category = Category(name="Electronics")
            db.session.add(category)
            db.session.commit()

            product = Product(
                name="Test Product", sku="TEST", price=100, category_id=category.id
            )
            db.session.add(product)
            db.session.commit()

            retrieved = ProductService.get_product_by_id(product.id)
            assert retrieved == product

            # Test non-existent ID
            assert ProductService.get_product_by_id(99999) is None

    def test_get_product_by_sku(self, app):
        """Test product retrieval by SKU"""
        with app.app_context():
            category = Category(name="Electronics")
            db.session.add(category)
            db.session.commit()

            product = Product(
                name="Test Product", sku="UNIQUE-SKU", price=100, category_id=category.id
            )
            db.session.add(product)
            db.session.commit()

            retrieved = ProductService.get_product_by_sku("UNIQUE-SKU")
            assert retrieved == product

            # Test non-existent SKU
            assert ProductService.get_product_by_sku("NONEXISTENT") is None

    def test_create_product_success(self, app):
        """Test successful product creation"""
        with app.app_context():
            category = Category(name="Electronics")
            db.session.add(category)
            db.session.commit()

            success, product, error = ProductService.create_product(
                name="New Product",
                sku="NEW-SKU",
                price=299.99,
                category_id=category.id,
                description="A new product",
                cost=200.00,
                stock_quantity=15,
                min_stock_level=5
            )

            assert success is True
            assert product is not None
            assert error is None
            assert product.name == "New Product"
            assert product.sku == "NEW-SKU"
            assert product.price == Decimal("299.99")

    def test_create_product_invalid_category(self, app):
        """Test product creation with invalid category"""
        with app.app_context():
            success, product, error = ProductService.create_product(
                name="New Product",
                sku="NEW-SKU",
                price=299.99,
                category_id=99999  # Non-existent category
            )

            assert success is False
            assert product is None
            assert "カテゴリが見つからない" in error

    def test_create_product_duplicate_sku(self, app):
        """Test product creation with duplicate SKU"""
        with app.app_context():
            category = Category(name="Electronics")
            db.session.add(category)
            db.session.commit()

            # Create first product
            product1 = Product(
                name="Product 1", sku="DUPLICATE", price=100, category_id=category.id
            )
            db.session.add(product1)
            db.session.commit()

            # Try to create second product with same SKU
            success, product, error = ProductService.create_product(
                name="Product 2",
                sku="DUPLICATE",
                price=200,
                category_id=category.id
            )

            assert success is False
            assert product is None
            assert "SKUは既に使用されています" in error

    def test_update_product_success(self, app):
        """Test successful product update"""
        with app.app_context():
            category = Category(name="Electronics")
            db.session.add(category)
            db.session.commit()

            product = Product(
                name="Original", sku="ORIG", price=100, category_id=category.id
            )
            db.session.add(product)
            db.session.commit()

            success, error = ProductService.update_product(
                product=product,
                name="Updated Name",
                price=Decimal("150.00")
            )

            assert success is True
            assert error is None
            assert product.name == "Updated Name"
            assert product.price == Decimal("150.00")

    def test_update_product_inactive(self, app):
        """Test updating inactive product"""
        with app.app_context():
            category = Category(name="Electronics")
            db.session.add(category)
            db.session.commit()

            product = Product(
                name="Product", sku="SKU", price=100, category_id=category.id
            )
            product.is_active = False
            db.session.add(product)
            db.session.commit()

            success, error = ProductService.update_product(product=product, name="New Name")

            assert success is False
            assert "無効化された製品は編集できません" in error

    def test_deactivate_product(self, app):
        """Test product deactivation"""
        with app.app_context():
            category = Category(name="Electronics")
            db.session.add(category)
            db.session.commit()

            product = Product(
                name="Product", sku="SKU", price=100, category_id=category.id
            )
            db.session.add(product)
            db.session.commit()

            success, error = ProductService.deactivate_product(product)

            assert success is True
            assert error is None
            assert product.is_active is False

    def test_activate_product(self, app):
        """Test product activation"""
        with app.app_context():
            category = Category(name="Electronics")
            db.session.add(category)
            db.session.commit()

            product = Product(
                name="Product", sku="SKU", price=100, category_id=category.id
            )
            product.is_active = False
            db.session.add(product)
            db.session.commit()

            success, error = ProductService.activate_product(product)

            assert success is True
            assert error is None
            assert product.is_active is True

    def test_update_stock(self, app):
        """Test stock quantity update"""
        with app.app_context():
            category = Category(name="Electronics")
            db.session.add(category)
            db.session.commit()

            product = Product(
                name="Product", sku="SKU", price=100,
                category_id=category.id, stock_quantity=10
            )
            db.session.add(product)
            db.session.commit()

            success, error = ProductService.update_stock(product, 25)

            assert success is True
            assert error is None
            assert product.stock_quantity == 25

    def test_update_stock_negative(self, app):
        """Test stock update with negative value"""
        with app.app_context():
            category = Category(name="Electronics")
            db.session.add(category)
            db.session.commit()

            product = Product(
                name="Product", sku="SKU", price=100, category_id=category.id
            )
            db.session.add(product)
            db.session.commit()

            success, error = ProductService.update_stock(product, -5)

            assert success is False
            assert "在庫数量は0以上である必要があります" in error

    def test_get_low_stock_products(self, app):
        """Test low stock products retrieval"""
        with app.app_context():
            category = Category(name="Electronics")
            db.session.add(category)
            db.session.commit()

            # Normal stock
            product1 = Product(
                name="Product 1", sku="P1", price=100,
                category_id=category.id, stock_quantity=20, min_stock_level=10
            )
            # Low stock
            product2 = Product(
                name="Product 2", sku="P2", price=100,
                category_id=category.id, stock_quantity=5, min_stock_level=10
            )
            # Out of stock
            product3 = Product(
                name="Product 3", sku="P3", price=100,
                category_id=category.id, stock_quantity=0, min_stock_level=5
            )

            db.session.add_all([product1, product2, product3])
            db.session.commit()

            low_stock_products = ProductService.get_low_stock_products()
            assert len(low_stock_products) == 2
            assert product2 in low_stock_products
            assert product3 in low_stock_products


class TestCategoryService:
    """Test cases for CategoryService"""

    def test_get_categories_with_pagination(self, app):
        """Test paginated category retrieval"""
        with app.app_context():
            # Create test categories
            categories = []
            for i in range(15):
                category = Category(name=f"Category {i}")
                categories.append(category)

            db.session.add_all(categories)
            db.session.commit()

            pagination = CategoryService.get_categories_with_pagination(page=1, per_page=10)
            assert len(pagination.items) == 10
            assert pagination.total == 15

    def test_get_categories_with_search(self, app):
        """Test category search functionality"""
        with app.app_context():
            category1 = Category(name="Electronics", description="Electronic devices")
            category2 = Category(name="Books", description="Reading materials")
            category3 = Category(name="Electronic Books", description="Digital reading")

            db.session.add_all([category1, category2, category3])
            db.session.commit()

            # Search by name
            pagination = CategoryService.get_categories_with_pagination(search="Electronic")
            assert len(pagination.items) == 2

    def test_get_category_by_id(self, app):
        """Test category retrieval by ID"""
        with app.app_context():
            category = Category(name="Test Category")
            db.session.add(category)
            db.session.commit()

            retrieved = CategoryService.get_category_by_id(category.id)
            assert retrieved == category

    def test_get_root_categories(self, app):
        """Test root categories retrieval"""
        with app.app_context():
            root1 = Category(name="Electronics")
            root2 = Category(name="Books")
            db.session.add_all([root1, root2])
            db.session.commit()

            child = Category(name="Smartphones", parent_id=root1.id)
            db.session.add(child)
            db.session.commit()

            roots = CategoryService.get_root_categories()
            assert len(roots) == 2
            assert root1 in roots
            assert root2 in roots
            assert child not in roots

    def test_create_category_success(self, app):
        """Test successful category creation"""
        with app.app_context():
            success, category, error = CategoryService.create_category(
                name="New Category",
                description="A new category"
            )

            assert success is True
            assert category is not None
            assert error is None
            assert category.name == "New Category"

    def test_create_category_with_parent(self, app):
        """Test category creation with parent"""
        with app.app_context():
            parent = Category(name="Parent")
            db.session.add(parent)
            db.session.commit()

            success, category, error = CategoryService.create_category(
                name="Child",
                parent_id=parent.id
            )

            assert success is True
            assert category.parent == parent
            assert category in parent.children

    def test_create_category_invalid_parent(self, app):
        """Test category creation with invalid parent"""
        with app.app_context():
            success, category, error = CategoryService.create_category(
                name="Child",
                parent_id=99999  # Non-existent parent
            )

            assert success is False
            assert category is None
            assert "親カテゴリが見つからない" in error

    def test_update_category_success(self, app):
        """Test successful category update"""
        with app.app_context():
            category = Category(name="Original", description="Original desc")
            db.session.add(category)
            db.session.commit()

            success, error = CategoryService.update_category(
                category=category,
                name="Updated",
                description="Updated desc"
            )

            assert success is True
            assert error is None
            assert category.name == "Updated"
            assert category.description == "Updated desc"

    def test_update_category_inactive(self, app):
        """Test updating inactive category"""
        with app.app_context():
            category = Category(name="Category")
            category.is_active = False
            db.session.add(category)
            db.session.commit()

            success, error = CategoryService.update_category(
                category=category,
                name="New Name"
            )

            assert success is False
            assert "無効化されたカテゴリは編集できません" in error

    def test_deactivate_category_success(self, app):
        """Test successful category deactivation"""
        with app.app_context():
            category = Category(name="Category")
            db.session.add(category)
            db.session.commit()

            success, error = CategoryService.deactivate_category(category)

            assert success is True
            assert error is None
            assert category.is_active is False

    def test_deactivate_category_with_products(self, app):
        """Test category deactivation with existing products"""
        with app.app_context():
            category = Category(name="Category")
            db.session.add(category)
            db.session.commit()

            product = Product(
                name="Product", sku="SKU", price=100, category_id=category.id
            )
            db.session.add(product)
            db.session.commit()

            success, error = CategoryService.deactivate_category(category)

            assert success is False
            assert "アクティブな製品が存在する" in error