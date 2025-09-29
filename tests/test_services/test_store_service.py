"""
Test cases for StoreService

This module contains comprehensive tests for the StoreService class including
CRUD operations, search functionality, and business logic tests.
"""
import pytest
from datetime import date, timedelta

from models import db, Store
from services import StoreService


class TestStoreService:
    """Test cases for StoreService"""

    def test_get_stores_with_pagination_basic(self, app):
        """Test basic pagination functionality"""
        with app.app_context():
            # Create test stores
            for i in range(25):
                store = Store(
                    name=f"Test Store {i+1}",
                    address=f"123 Test St {i+1}",
                    status='active'
                )
                db.session.add(store)
            db.session.commit()

            # Test first page
            pagination, total_count = StoreService.get_stores_with_pagination(page=1, per_page=10)

            assert total_count == 25
            assert len(pagination.items) == 10
            assert pagination.page == 1
            assert pagination.pages == 3
            assert pagination.has_next is True
            assert pagination.has_prev is False

            # Test second page
            pagination, total_count = StoreService.get_stores_with_pagination(page=2, per_page=10)

            assert len(pagination.items) == 10
            assert pagination.page == 2
            assert pagination.has_next is True
            assert pagination.has_prev is True

    def test_get_stores_with_pagination_search(self, app):
        """Test pagination with search functionality"""
        with app.app_context():
            # Create test stores
            coffee_store = Store(name="Coffee Shop", address="123 Main St", status='active')
            tea_store = Store(name="Tea House", address="456 Tea Ave", status='active')
            restaurant = Store(name="Restaurant", address="789 Food St", status='active')

            db.session.add_all([coffee_store, tea_store, restaurant])
            db.session.commit()

            # Search for coffee
            pagination, total_count = StoreService.get_stores_with_pagination(search="Coffee")

            assert total_count == 1
            assert len(pagination.items) == 1
            assert pagination.items[0].name == "Coffee Shop"

            # Search for tea (case insensitive)
            pagination, total_count = StoreService.get_stores_with_pagination(search="tea")

            assert total_count == 1
            assert pagination.items[0].name == "Tea House"

    def test_get_stores_with_pagination_status_filter(self, app):
        """Test pagination with status filtering"""
        with app.app_context():
            # Create stores with different statuses
            active_store = Store(name="Active Store", address="123 Active St", status='active')
            inactive_store = Store(name="Inactive Store", address="123 Inactive St", status='inactive')
            temp_closed_store = Store(name="Temp Store", address="123 Temp St", status='temporarily_closed')

            db.session.add_all([active_store, inactive_store, temp_closed_store])
            db.session.commit()

            # Filter by active status
            pagination, total_count = StoreService.get_stores_with_pagination(status='active')

            assert total_count == 1
            assert pagination.items[0].name == "Active Store"

            # Filter by inactive status
            pagination, total_count = StoreService.get_stores_with_pagination(status='inactive')

            assert total_count == 1
            assert pagination.items[0].name == "Inactive Store"

    def test_get_stores_with_pagination_location_filter(self, app):
        """Test pagination with location filtering"""
        with app.app_context():
            # Create stores in different locations
            tokyo_store = Store(
                name="Tokyo Store",
                address="123 Tokyo St",
                location_prefecture="東京都",
                location_city="渋谷区",
                status='active'
            )
            osaka_store = Store(
                name="Osaka Store",
                address="123 Osaka St",
                location_prefecture="大阪府",
                location_city="大阪市",
                status='active'
            )

            db.session.add_all([tokyo_store, osaka_store])
            db.session.commit()

            # Filter by prefecture
            pagination, total_count = StoreService.get_stores_with_pagination(prefecture="東京都")

            assert total_count == 1
            assert pagination.items[0].name == "Tokyo Store"

            # Filter by city
            pagination, total_count = StoreService.get_stores_with_pagination(city="大阪市")

            assert total_count == 1
            assert pagination.items[0].name == "Osaka Store"

    def test_get_stores_with_pagination_sorting(self, app):
        """Test pagination with sorting"""
        with app.app_context():
            # Create stores with different names
            store_a = Store(name="Apple Store", address="123 A St", status='active')
            store_z = Store(name="Zebra Store", address="123 Z St", status='active')
            store_m = Store(name="Maple Store", address="123 M St", status='active')

            db.session.add_all([store_a, store_z, store_m])
            db.session.commit()

            # Sort by name ascending
            pagination, total_count = StoreService.get_stores_with_pagination(
                sort_by='name', sort_order='asc'
            )

            assert pagination.items[0].name == "Apple Store"
            assert pagination.items[-1].name == "Zebra Store"

            # Sort by name descending
            pagination, total_count = StoreService.get_stores_with_pagination(
                sort_by='name', sort_order='desc'
            )

            assert pagination.items[0].name == "Zebra Store"
            assert pagination.items[-1].name == "Apple Store"

    def test_get_store_by_id(self, app, sample_store_data):
        """Test getting store by ID"""
        with app.app_context():
            store = Store(**sample_store_data)
            db.session.add(store)
            db.session.commit()

            # Valid ID
            retrieved_store = StoreService.get_store_by_id(store.id)
            assert retrieved_store is not None
            assert retrieved_store.id == store.id
            assert retrieved_store.name == store.name

            # Invalid ID
            invalid_store = StoreService.get_store_by_id(99999)
            assert invalid_store is None

    def test_create_store_success(self, app):
        """Test successful store creation"""
        with app.app_context():
            success, store, message = StoreService.create_store(
                name="New Store",
                address="123 New St",
                phone="123-456-7890",
                email="new@store.com",
                status='active',
                location_prefecture="東京都",
                location_city="渋谷区"
            )

            assert success is True
            assert store is not None
            assert "正常に作成されました" in message
            assert store.name == "New Store"
            assert store.address == "123 New St"
            assert store.phone == "123-456-7890"
            assert store.email == "new@store.com"

    def test_create_store_missing_name(self, app):
        """Test store creation with missing name"""
        with app.app_context():
            success, store, message = StoreService.create_store(
                name="",
                address="123 Test St"
            )

            assert success is False
            assert store is None
            assert "店舗名は必須です" in message

    def test_create_store_missing_address(self, app):
        """Test store creation with missing address"""
        with app.app_context():
            success, store, message = StoreService.create_store(
                name="Test Store",
                address=""
            )

            assert success is False
            assert store is None
            assert "住所は必須です" in message

    def test_create_store_duplicate_name(self, app, sample_store_data):
        """Test store creation with duplicate name"""
        with app.app_context():
            # Create first store
            store1 = Store(**sample_store_data)
            db.session.add(store1)
            db.session.commit()

            # Try to create store with same name
            success, store, message = StoreService.create_store(
                name=sample_store_data['name'],
                address="Different Address"
            )

            assert success is False
            assert store is None
            assert "既に存在します" in message

    def test_update_store_success(self, app, sample_store_data):
        """Test successful store update"""
        with app.app_context():
            store = Store(**sample_store_data)
            db.session.add(store)
            db.session.commit()

            success, updated_store, message = StoreService.update_store(
                store_id=store.id,
                name="Updated Store Name",
                address="Updated Address",
                phone="987-654-3210",
                status='temporarily_closed'
            )

            assert success is True
            assert updated_store is not None
            assert "正常に更新されました" in message
            assert updated_store.name == "Updated Store Name"
            assert updated_store.address == "Updated Address"
            assert updated_store.phone == "987-654-3210"
            assert updated_store.status == 'temporarily_closed'

    def test_update_store_not_found(self, app):
        """Test updating non-existent store"""
        with app.app_context():
            success, store, message = StoreService.update_store(
                store_id=99999,
                name="Updated Name"
            )

            assert success is False
            assert store is None
            assert "店舗が見つかりません" in message

    def test_update_store_duplicate_name(self, app):
        """Test updating store with duplicate name"""
        with app.app_context():
            # Create two stores
            store1 = Store(name="Store 1", address="123 St 1")
            store2 = Store(name="Store 2", address="123 St 2")
            db.session.add_all([store1, store2])
            db.session.commit()

            # Try to update store2 with store1's name
            success, store, message = StoreService.update_store(
                store_id=store2.id,
                name="Store 1"
            )

            assert success is False
            assert store is None
            assert "既に存在します" in message

    def test_delete_store_success(self, app, sample_store_data):
        """Test successful store deletion"""
        with app.app_context():
            store = Store(**sample_store_data)
            db.session.add(store)
            db.session.commit()

            store_id = store.id
            success, message = StoreService.delete_store(store_id)

            assert success is True
            assert "正常に削除されました" in message

            # Verify store is deleted
            deleted_store = Store.query.get(store_id)
            assert deleted_store is None

    def test_delete_store_not_found(self, app):
        """Test deleting non-existent store"""
        with app.app_context():
            success, message = StoreService.delete_store(99999)

            assert success is False
            assert "店舗が見つかりません" in message

    def test_get_stores_by_status(self, app):
        """Test getting stores by status"""
        with app.app_context():
            # Create stores with different statuses
            active_store = Store(name="Active Store", address="123 Active St", status='active')
            inactive_store = Store(name="Inactive Store", address="123 Inactive St", status='inactive')

            db.session.add_all([active_store, inactive_store])
            db.session.commit()

            # Get active stores
            active_stores = StoreService.get_stores_by_status('active')
            assert len(active_stores) == 1
            assert active_stores[0].name == "Active Store"

            # Get inactive stores
            inactive_stores = StoreService.get_stores_by_status('inactive')
            assert len(inactive_stores) == 1
            assert inactive_stores[0].name == "Inactive Store"

    def test_get_active_stores(self, app):
        """Test getting active stores"""
        with app.app_context():
            # Create stores with different statuses
            active_store1 = Store(name="Active Store 1", address="123 Active St 1", status='active')
            active_store2 = Store(name="Active Store 2", address="123 Active St 2", status='active')
            inactive_store = Store(name="Inactive Store", address="123 Inactive St", status='inactive')

            db.session.add_all([active_store1, active_store2, inactive_store])
            db.session.commit()

            active_stores = StoreService.get_active_stores()
            assert len(active_stores) == 2

            active_names = [store.name for store in active_stores]
            assert "Active Store 1" in active_names
            assert "Active Store 2" in active_names

    def test_get_stores_by_location(self, app):
        """Test getting stores by location"""
        with app.app_context():
            # Create stores in different locations
            tokyo_store = Store(
                name="Tokyo Store",
                address="123 Tokyo St",
                location_prefecture="東京都",
                location_city="渋谷区"
            )
            osaka_store = Store(
                name="Osaka Store",
                address="123 Osaka St",
                location_prefecture="大阪府",
                location_city="大阪市"
            )

            db.session.add_all([tokyo_store, osaka_store])
            db.session.commit()

            # Get stores by prefecture
            tokyo_stores = StoreService.get_stores_by_location(prefecture="東京都")
            assert len(tokyo_stores) == 1
            assert tokyo_stores[0].name == "Tokyo Store"

            # Get stores by city
            osaka_stores = StoreService.get_stores_by_location(city="大阪市")
            assert len(osaka_stores) == 1
            assert osaka_stores[0].name == "Osaka Store"

    def test_search_stores(self, app):
        """Test store search functionality"""
        with app.app_context():
            # Create test stores
            coffee_store = Store(name="Coffee Shop", address="123 Main St")
            tea_store = Store(name="Tea House", address="456 Tea Ave")

            db.session.add_all([coffee_store, tea_store])
            db.session.commit()

            # Search for coffee
            coffee_results = StoreService.search_stores("Coffee")
            assert len(coffee_results) == 1
            assert coffee_results[0].name == "Coffee Shop"

            # Empty search
            empty_results = StoreService.search_stores("")
            assert len(empty_results) == 0

    def test_get_statistics(self, app):
        """Test getting store statistics"""
        with app.app_context():
            # Create stores with different statuses
            active_store = Store(name="Active Store", address="123 Active St", status='active')
            inactive_store = Store(name="Inactive Store", address="123 Inactive St", status='inactive')
            temp_closed_store = Store(name="Temp Store", address="123 Temp St", status='temporarily_closed')

            # Add prefecture data
            active_store.location_prefecture = "東京都"
            inactive_store.location_prefecture = "大阪府"
            temp_closed_store.location_prefecture = "東京都"

            # Add establishment dates
            active_store.establishment_date = date.today() - timedelta(days=365)
            inactive_store.establishment_date = date.today() - timedelta(days=730)

            db.session.add_all([active_store, inactive_store, temp_closed_store])
            db.session.commit()

            stats = StoreService.get_statistics()

            assert stats['total_stores'] == 3
            assert stats['active_stores'] == 1
            assert stats['inactive_stores'] == 1
            assert stats['temporarily_closed_stores'] == 1
            assert len(stats['prefecture_distribution']) >= 1
            assert stats['average_business_years'] > 0

    def test_get_prefectures(self, app):
        """Test getting list of prefectures"""
        with app.app_context():
            # Create stores in different prefectures
            tokyo_store = Store(
                name="Tokyo Store",
                address="123 Tokyo St",
                location_prefecture="東京都"
            )
            osaka_store = Store(
                name="Osaka Store",
                address="123 Osaka St",
                location_prefecture="大阪府"
            )

            db.session.add_all([tokyo_store, osaka_store])
            db.session.commit()

            prefectures = StoreService.get_prefectures()

            assert len(prefectures) == 2
            assert "東京都" in prefectures
            assert "大阪府" in prefectures

    def test_get_cities_by_prefecture(self, app):
        """Test getting cities by prefecture"""
        with app.app_context():
            # Create stores in Tokyo with different cities
            shibuya_store = Store(
                name="Shibuya Store",
                address="123 Shibuya St",
                location_prefecture="東京都",
                location_city="渋谷区"
            )
            shinjuku_store = Store(
                name="Shinjuku Store",
                address="123 Shinjuku St",
                location_prefecture="東京都",
                location_city="新宿区"
            )

            db.session.add_all([shibuya_store, shinjuku_store])
            db.session.commit()

            cities = StoreService.get_cities_by_prefecture("東京都")

            assert len(cities) == 2
            assert "渋谷区" in cities
            assert "新宿区" in cities

    def test_create_store_with_business_hours(self, app):
        """Test creating store with custom business hours"""
        with app.app_context():
            business_hours = {
                'mon': '10:00-20:00',
                'tue': '10:00-20:00',
                'wed': 'closed',
                'thu': '10:00-20:00',
                'fri': '10:00-20:00',
                'sat': '11:00-18:00',
                'sun': 'closed'
            }

            success, store, message = StoreService.create_store(
                name="Custom Hours Store",
                address="123 Custom St",
                business_hours=business_hours
            )

            assert success is True
            assert store.business_hours == business_hours

    def test_create_store_with_establishment_date(self, app):
        """Test creating store with specific establishment date"""
        with app.app_context():
            establishment_date = date(2020, 1, 1)

            success, store, message = StoreService.create_store(
                name="Established Store",
                address="123 Established St",
                establishment_date=establishment_date
            )

            assert success is True
            assert store.establishment_date == establishment_date
            assert store.business_years > 0