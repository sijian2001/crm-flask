"""
Test cases for Category model
"""
import pytest
from models import Category, Product


class TestCategoryModel:
    """Test Category model functionality"""

    def test_category_creation(self, db_session):
        """Test category creation with required fields"""
        category = Category(
            name='テストカテゴリ',
            description='テスト用のカテゴリです'
        )
        db_session.add(category)
        db_session.commit()

        assert category.id is not None
        assert category.name == 'テストカテゴリ'
        assert category.description == 'テスト用のカテゴリです'
        assert category.parent_id is None
        assert category.is_active is True

    def test_category_hierarchy(self, db_session):
        """Test category hierarchy (parent-child relationship)"""
        # Create parent category
        parent = Category(name='親カテゴリ')
        db_session.add(parent)
        db_session.commit()

        # Create child category
        child = Category(name='子カテゴリ', parent_id=parent.id)
        db_session.add(child)
        db_session.commit()

        # Test relationships
        assert child.parent == parent
        assert child in parent.children
        assert child.parent_id == parent.id

    def test_full_path_property(self, db_session):
        """Test full_path property for hierarchical categories"""
        # Root category
        root = Category(name='電子機器')
        db_session.add(root)
        db_session.commit()

        # Level 1 category
        level1 = Category(name='スマートフォン', parent_id=root.id)
        db_session.add(level1)
        db_session.commit()

        # Level 2 category
        level2 = Category(name='iPhone', parent_id=level1.id)
        db_session.add(level2)
        db_session.commit()

        # Test full paths
        assert root.full_path == '電子機器'
        assert level1.full_path == '電子機器 > スマートフォン'
        assert level2.full_path == '電子機器 > スマートフォン > iPhone'

    def test_product_count_property(self, db_session, sample_category):
        """Test product_count property"""
        # Initially no products
        assert sample_category.product_count == 0

        # Add products
        product1 = Product(
            name='製品1', sku='P001', price=100.00,
            category_id=sample_category.id
        )
        product2 = Product(
            name='製品2', sku='P002', price=200.00,
            category_id=sample_category.id
        )
        db_session.add_all([product1, product2])
        db_session.commit()

        # Should count active products
        assert sample_category.product_count == 2

        # Deactivate one product
        product1.is_active = False
        db_session.commit()

        # Should only count active products
        assert sample_category.product_count == 1

    def test_get_all_children_recursive(self, db_session):
        """Test recursive retrieval of all child categories"""
        # Create hierarchy: parent -> child1, child2 -> grandchild1, grandchild2
        parent = Category(name='親')
        db_session.add(parent)
        db_session.commit()

        child1 = Category(name='子1', parent_id=parent.id)
        child2 = Category(name='子2', parent_id=parent.id)
        db_session.add_all([child1, child2])
        db_session.commit()

        grandchild1 = Category(name='孫1', parent_id=child1.id)
        grandchild2 = Category(name='孫2', parent_id=child2.id)
        db_session.add_all([grandchild1, grandchild2])
        db_session.commit()

        # Get all children recursively
        all_children = parent.get_all_children()
        child_names = [child.name for child in all_children]

        assert len(all_children) == 4
        assert '子1' in child_names
        assert '子2' in child_names
        assert '孫1' in child_names
        assert '孫2' in child_names

    def test_get_all_children_inactive_excluded(self, db_session):
        """Test that inactive children are excluded from get_all_children"""
        parent = Category(name='親')
        db_session.add(parent)
        db_session.commit()

        child_active = Category(name='アクティブ子', parent_id=parent.id)
        child_inactive = Category(name='非アクティブ子', parent_id=parent.id, is_active=False)
        db_session.add_all([child_active, child_inactive])
        db_session.commit()

        all_children = parent.get_all_children()
        child_names = [child.name for child in all_children]

        assert len(all_children) == 1
        assert 'アクティブ子' in child_names
        assert '非アクティブ子' not in child_names

    def test_deactivate_activate(self, sample_category):
        """Test category deactivation and activation"""
        # Initial state
        assert sample_category.is_active is True

        # Deactivate
        sample_category.deactivate()
        assert sample_category.is_active is False

        # Activate
        sample_category.activate()
        assert sample_category.is_active is True

    def test_category_product_relationship(self, db_session, sample_category):
        """Test relationship between category and products"""
        product1 = Product(
            name='関連製品1', sku='REL-001', price=100.00,
            category_id=sample_category.id
        )
        product2 = Product(
            name='関連製品2', sku='REL-002', price=200.00,
            category_id=sample_category.id
        )
        db_session.add_all([product1, product2])
        db_session.commit()

        # Test relationships
        assert len(sample_category.products) == 2
        assert product1 in sample_category.products
        assert product2 in sample_category.products
        assert product1.category == sample_category
        assert product2.category == sample_category

    def test_category_str_representation(self, sample_category):
        """Test string representation of category"""
        expected = f'<Category {sample_category.name}>'
        assert str(sample_category) == expected

    def test_category_deep_hierarchy(self, db_session):
        """Test deep category hierarchy creation"""
        categories = []
        parent_id = None

        # Create 5-level hierarchy
        for i in range(5):
            category = Category(
                name=f'レベル{i+1}',
                parent_id=parent_id
            )
            db_session.add(category)
            db_session.commit()
            categories.append(category)
            parent_id = category.id

        # Test full path of deepest category
        deepest = categories[-1]
        expected_path = ' > '.join([f'レベル{i+1}' for i in range(5)])
        assert deepest.full_path == expected_path

        # Test recursive children retrieval from root
        root = categories[0]
        all_children = root.get_all_children()
        assert len(all_children) == 4  # 4 descendants