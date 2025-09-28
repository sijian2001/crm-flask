"""
Category service layer

This module provides business logic for category management including hierarchical operations,
validation, and relationship handling.
"""
from typing import Optional, Tuple, List
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, and_, desc, asc, func
from sqlalchemy.orm import selectinload, subqueryload
from models import db, Product, Category
from product_config import ProductConfig


class CategoryService:
    """
    Service class for category-related business logic

    Handles category operations including hierarchical management,
    validation, and relationship handling.
    """

    @staticmethod
    def get_categories_with_pagination(page: int = 1, per_page: Optional[int] = None,
                                     search: Optional[str] = None,
                                     parent_id: Optional[int] = None):
        """
        Get paginated categories with optional search and parent filtering

        Optimized to prevent N+1 queries by using subqueryload for relationships
        and calculating product_count efficiently.

        Args:
            page: Page number (1-based)
            per_page: Items per page
            search: Search query string
            parent_id: Filter by parent category ID

        Returns:
            Pagination object with filtered categories
        """
        if per_page is None:
            per_page = ProductConfig.get_default_per_page()

        # Base query for active categories with eager loading
        query = (
            Category.query
            .filter_by(is_active=True)
            .options(
                # Load parent relationship to avoid N+1 for full_path
                selectinload(Category.parent),
                # Load children relationship for hierarchy display
                selectinload(Category.children)
            )
        )

        # Apply search filter
        if search and len(search.strip()) >= ProductConfig.get_search_min_length():
            search_term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Category.name.ilike(search_term),
                    Category.description.ilike(search_term)
                )
            )

        # Apply parent filter
        if parent_id is not None:
            query = query.filter_by(parent_id=parent_id)

        # Order by name
        query = query.order_by(asc(Category.name))

        return query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

    @staticmethod
    def get_categories_with_product_counts(category_ids: List[int] = None) -> List[tuple]:
        """
        Get categories with their product counts in a single optimized query

        This method prevents N+1 queries by using a single JOIN query to fetch
        categories along with their product counts.

        Args:
            category_ids: Optional list of category IDs to filter

        Returns:
            List of tuples (category, product_count)
        """
        query = (
            db.session.query(
                Category,
                func.count(Product.id).label('product_count')
            )
            .outerjoin(Product, and_(
                Product.category_id == Category.id,
                Product.is_active == True
            ))
            .filter(Category.is_active == True)
            .group_by(Category.id)
        )

        if category_ids:
            query = query.filter(Category.id.in_(category_ids))

        return query.all()

    @staticmethod
    def get_category_by_id(category_id: int) -> Optional[Category]:
        """
        Get category by ID

        Args:
            category_id: Category ID

        Returns:
            Category instance or None if not found
        """
        return Category.query.get(category_id)

    @staticmethod
    def get_root_categories() -> List[Category]:
        """
        Get all root categories (categories without parent)

        Returns:
            List of root categories
        """
        return Category.query.filter_by(parent_id=None, is_active=True).order_by(Category.name).all()

    @staticmethod
    def create_category(name: str, description: Optional[str] = None,
                       parent_id: Optional[int] = None) -> Tuple[bool, Optional[Category], Optional[str]]:
        """
        Create a new category

        Args:
            name: Category name
            description: Category description
            parent_id: Parent category ID

        Returns:
            Tuple of (success, category, error_message)
        """
        try:
            # Validate parent category if specified
            if parent_id is not None:
                parent = Category.query.get(parent_id)
                if not parent or not parent.is_active:
                    return False, None, "指定された親カテゴリが見つからないか、無効化されています。"

                # Check depth limit
                depth = CategoryService._get_category_depth(parent)
                if depth >= ProductConfig.get_category_config()['max_depth']:
                    return False, None, f"カテゴリの階層が深すぎます（最大{ProductConfig.get_category_config()['max_depth']}階層）。"

            # Create new category
            category = Category(
                name=name,
                description=description,
                parent_id=parent_id
            )

            db.session.add(category)
            db.session.commit()
            return True, category, None

        except IntegrityError:
            db.session.rollback()
            return False, None, "データベースエラーが発生しました。"
        except Exception as e:
            db.session.rollback()
            return False, None, f"カテゴリ作成中にエラーが発生しました: {str(e)}"

    @staticmethod
    def update_category(category: Category, **kwargs) -> Tuple[bool, Optional[str]]:
        """
        Update category information

        Args:
            category: Category instance to update
            **kwargs: Fields to update

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Validate category is active
            if not category.is_active:
                return False, "無効化されたカテゴリは編集できません。"

            # Check parent change doesn't create circular reference
            if 'parent_id' in kwargs and kwargs['parent_id'] != category.parent_id:
                if CategoryService._would_create_circular_reference(category, kwargs['parent_id']):
                    return False, "親カテゴリの設定により循環参照が発生します。"

            # Update category
            for key, value in kwargs.items():
                if hasattr(category, key) and key not in ['id', 'created_at']:
                    setattr(category, key, value)
            category.updated_at = db.func.now()

            db.session.commit()
            return True, None

        except Exception as e:
            db.session.rollback()
            return False, f"カテゴリ更新中にエラーが発生しました: {str(e)}"

    @staticmethod
    def deactivate_category(category: Category) -> Tuple[bool, Optional[str]]:
        """
        Deactivate a category (soft delete)

        Args:
            category: Category instance to deactivate

        Returns:
            Tuple of (success, error_message)
        """
        try:
            if not category.is_active:
                return False, "指定されたカテゴリは既に無効化されています。"

            # Check if category has active products
            if category.product_count > 0:
                return False, "アクティブな製品が存在するカテゴリは無効化できません。"

            category.deactivate()
            db.session.commit()
            return True, None

        except Exception as e:
            db.session.rollback()
            return False, f"カテゴリ無効化中にエラーが発生しました: {str(e)}"

    @staticmethod
    def _get_category_depth(category: Category) -> int:
        """
        Get the depth of a category in the hierarchy

        Args:
            category: Category instance

        Returns:
            Depth level (0 for root categories)
        """
        depth = 0
        current = category
        while current.parent_id is not None:
            depth += 1
            current = current.parent
            if depth > 10:  # Prevent infinite loop
                break
        return depth

    @staticmethod
    def _would_create_circular_reference(category: Category, new_parent_id: Optional[int]) -> bool:
        """
        Check if setting a new parent would create a circular reference

        Args:
            category: Category to check
            new_parent_id: Proposed new parent ID

        Returns:
            True if circular reference would be created
        """
        if new_parent_id is None:
            return False

        # Check if new parent is a descendant of current category
        new_parent = Category.query.get(new_parent_id)
        if not new_parent:
            return False

        current = new_parent
        checked_ids = set()
        while current.parent_id is not None:
            if current.parent_id == category.id:
                return True
            if current.parent_id in checked_ids:  # Prevent infinite loop
                break
            checked_ids.add(current.parent_id)
            current = current.parent

        return False