"""
Product service layer

This module provides business logic for product management including CRUD operations,
search, filtering, and inventory management.
"""
from typing import Optional, Tuple, List

from sqlalchemy import or_, and_, desc, asc, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload, subqueryload

from models import db, Product, Category
from product_config import ProductConfig


class ProductService:
    """
    Service class for product-related business logic

    Handles all product operations including CRUD, search, filtering,
    and inventory management with proper error handling and validation.
    """

    @staticmethod
    def get_products_with_pagination(page: int = 1, per_page: Optional[int] = None,
                                   search: Optional[str] = None,
                                   category_id: Optional[int] = None,
                                   low_stock_only: bool = False,
                                   sort_by: str = 'name',
                                   sort_order: str = 'asc'):
        """
        Get paginated products with optional search and filtering

        Args:
            page: Page number (1-based)
            per_page: Items per page (uses config default if None)
            search: Search query string
            category_id: Filter by category ID
            low_stock_only: Show only low stock products
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Pagination object with filtered and sorted products
        """
        if per_page is None:
            per_page = ProductConfig.get_default_per_page()

        # Base query for active products
        query = Product.query.filter_by(is_active=True)

        # Apply search filter
        if search and len(search.strip()) >= ProductConfig.get_search_min_length():
            search_term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                    Product.sku.ilike(search_term)
                )
            )

        # Apply category filter
        if category_id:
            query = query.filter_by(category_id=category_id)

        # Apply low stock filter
        if low_stock_only:
            query = query.filter(Product.stock_quantity <= Product.min_stock_level)

        # Apply sorting
        if sort_order.lower() == 'desc':
            sort_func = desc
        else:
            sort_func = asc

        if hasattr(Product, sort_by):
            query = query.order_by(sort_func(getattr(Product, sort_by)))
        else:
            query = query.order_by(asc(Product.name))

        return query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

    @staticmethod
    def get_product_by_id(product_id: int) -> Optional[Product]:
        """
        Get product by ID

        Args:
            product_id: Product ID

        Returns:
            Product instance or None if not found
        """
        return Product.query.get(product_id)

    @staticmethod
    def get_product_by_sku(sku: str) -> Optional[Product]:
        """
        Get product by SKU

        Args:
            sku: Product SKU

        Returns:
            Product instance or None if not found
        """
        return Product.query.filter_by(sku=sku, is_active=True).first()

    @staticmethod
    def create_product(name: str, sku: str, price: float, category_id: int,
                      description: Optional[str] = None, cost: Optional[float] = None,
                      stock_quantity: int = 0, min_stock_level: Optional[int] = None) -> Tuple[bool, Optional[Product], Optional[str]]:
        """
        Create a new product

        Args:
            name: Product name
            sku: Product SKU (must be unique)
            price: Product price
            category_id: Category ID
            description: Product description
            cost: Product cost
            stock_quantity: Initial stock quantity
            min_stock_level: Minimum stock level

        Returns:
            Tuple of (success, product, error_message)
        """
        try:
            # Validate category exists
            category = Category.query.get(category_id)
            if not category or not category.is_active:
                return False, None, "指定されたカテゴリが見つからないか、無効化されています。"

            # Set default min stock level if not provided
            if min_stock_level is None:
                min_stock_level = ProductConfig.get_default_min_stock_level()

            # Check for duplicate SKU
            existing_product = Product.query.filter_by(sku=sku).first()
            if existing_product:
                return False, None, "指定されたSKUは既に使用されています。"

            # Create new product
            product = Product(
                name=name,
                sku=sku,
                price=price,
                category_id=category_id,
                description=description,
                cost=cost,
                stock_quantity=stock_quantity,
                min_stock_level=min_stock_level
            )

            db.session.add(product)
            db.session.commit()
            return True, product, None

        except IntegrityError:
            db.session.rollback()
            return False, None, "データベースエラーが発生しました。SKUが重複している可能性があります。"
        except Exception as e:
            db.session.rollback()
            return False, None, f"製品作成中にエラーが発生しました: {str(e)}"

    @staticmethod
    def update_product(product: Product, **kwargs) -> Tuple[bool, Optional[str]]:
        """
        Update product information

        Args:
            product: Product instance to update
            **kwargs: Fields to update

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Validate product is active
            if not product.is_active:
                return False, "無効化された製品は編集できません。"

            # Check for SKU uniqueness if updating SKU
            if 'sku' in kwargs and kwargs['sku'] != product.sku:
                existing_product = Product.query.filter_by(sku=kwargs['sku']).first()
                if existing_product and existing_product.id != product.id:
                    return False, "指定されたSKUは既に使用されています。"

            # Check category exists if updating category
            if 'category_id' in kwargs:
                category = Category.query.get(kwargs['category_id'])
                if not category or not category.is_active:
                    return False, "指定されたカテゴリが見つからないか、無効化されています。"

            # Update product
            product.update_info(**kwargs)
            db.session.commit()
            return True, None

        except IntegrityError:
            db.session.rollback()
            return False, "データベースエラーが発生しました。SKUが重複している可能性があります。"
        except Exception as e:
            db.session.rollback()
            return False, f"製品更新中にエラーが発生しました: {str(e)}"

    @staticmethod
    def deactivate_product(product: Product) -> Tuple[bool, Optional[str]]:
        """
        Deactivate a product (soft delete)

        Args:
            product: Product instance to deactivate

        Returns:
            Tuple of (success, error_message)
        """
        try:
            if not product.is_active:
                return False, "指定された製品は既に無効化されています。"

            product.deactivate()
            db.session.commit()
            return True, None

        except Exception as e:
            db.session.rollback()
            return False, f"製品無効化中にエラーが発生しました: {str(e)}"

    @staticmethod
    def activate_product(product: Product) -> Tuple[bool, Optional[str]]:
        """
        Activate a product

        Args:
            product: Product instance to activate

        Returns:
            Tuple of (success, error_message)
        """
        try:
            if product.is_active:
                return False, "指定された製品は既に有効化されています。"

            product.activate()
            db.session.commit()
            return True, None

        except Exception as e:
            db.session.rollback()
            return False, f"製品有効化中にエラーが発生しました: {str(e)}"

    @staticmethod
    def update_stock(product: Product, quantity: int) -> Tuple[bool, Optional[str]]:
        """
        Update product stock quantity

        Args:
            product: Product instance
            quantity: New stock quantity

        Returns:
            Tuple of (success, error_message)
        """
        try:
            if not product.is_active:
                return False, "無効化された製品の在庫は更新できません。"

            if quantity < 0:
                return False, "在庫数量は0以上である必要があります。"

            product.update_stock(quantity)
            db.session.commit()
            return True, None

        except Exception as e:
            db.session.rollback()
            return False, f"在庫更新中にエラーが発生しました: {str(e)}"

    @staticmethod
    def get_low_stock_products() -> List[Product]:
        """
        Get products with low stock levels

        Returns:
            List of products with stock at or below minimum level
        """
        return Product.query.filter(
            and_(
                Product.is_active == True,
                Product.stock_quantity <= Product.min_stock_level
            )
        ).all()


