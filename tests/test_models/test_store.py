"""
Test cases for Store model

This module contains comprehensive tests for the Store model including
CRUD operations, business logic, and validation tests.
"""
import pytest
from datetime import date, datetime, timedelta

from models import db, Store


class TestStoreModel:
    """Test cases for Store model"""

    def test_store_creation(self, app, sample_store_data):
        """Test basic store creation"""
        with app.app_context():
            store = Store(**sample_store_data)
            db.session.add(store)
            db.session.commit()

            assert store.id is not None
            assert store.name == sample_store_data['name']
            assert store.address == sample_store_data['address']
            assert store.status == 'active'

    def test_store_creation_with_minimal_data(self, app):
        """Test store creation with minimal required data"""
        with app.app_context():
            store = Store(
                name="Minimal Store",
                address="123 Test St"
            )
            db.session.add(store)
            db.session.commit()

            assert store.id is not None
            assert store.name == "Minimal Store"
            assert store.address == "123 Test St"
            assert store.status == 'active'
            assert store.business_hours is not None
            assert store.establishment_date is not None

    def test_store_business_years_calculation(self, app):
        """Test business years calculation"""
        with app.app_context():
            # Store established 2 years ago
            establishment_date = date.today() - timedelta(days=730)

            store = Store(
                name="Old Store",
                address="123 Old St",
                establishment_date=establishment_date
            )
            db.session.add(store)
            db.session.commit()

            # Should be approximately 2 years
            assert abs(store.business_years - 2.0) < 0.1

    def test_store_business_years_no_date(self, app):
        """Test business years calculation with no establishment date"""
        with app.app_context():
            store = Store(
                name="New Store",
                address="123 New St",
                establishment_date=None
            )
            db.session.add(store)
            db.session.commit()

            assert store.business_years == 0.0

    def test_store_is_active_property(self, app, sample_store_data):
        """Test is_active property"""
        with app.app_context():
            # Active store
            store = Store(**sample_store_data)
            store.status = 'active'
            db.session.add(store)
            db.session.commit()

            assert store.is_active is True

            # Inactive store
            store.status = 'inactive'
            db.session.commit()

            assert store.is_active is False

    def test_store_is_temporarily_closed_property(self, app, sample_store_data):
        """Test is_temporarily_closed property"""
        with app.app_context():
            store = Store(**sample_store_data)
            store.status = 'temporarily_closed'
            db.session.add(store)
            db.session.commit()

            assert store.is_temporarily_closed is True

            store.status = 'active'
            db.session.commit()

            assert store.is_temporarily_closed is False

    def test_store_location_full_property(self, app):
        """Test location_full property"""
        with app.app_context():
            # Store with both prefecture and city
            store = Store(
                name="Full Location Store",
                address="123 Full St",
                location_prefecture="東京都",
                location_city="渋谷区"
            )
            db.session.add(store)
            db.session.commit()

            assert store.location_full == "東京都, 渋谷区"

            # Store with only prefecture
            store.location_city = None
            db.session.commit()

            assert store.location_full == "東京都"

            # Store with no location
            store.location_prefecture = None
            db.session.commit()

            assert store.location_full == ""

    def test_store_closed_days_list_property(self, app, sample_store_data):
        """Test closed_days_list property"""
        with app.app_context():
            store = Store(**sample_store_data)
            store.closed_days = "sun, mon, tue"
            db.session.add(store)
            db.session.commit()

            closed_list = store.closed_days_list
            assert "sun" in closed_list
            assert "mon" in closed_list
            assert "tue" in closed_list
            assert len(closed_list) == 3

            # Empty closed days
            store.closed_days = ""
            db.session.commit()

            assert store.closed_days_list == []

    def test_store_is_open_on_day(self, app, sample_store_data):
        """Test is_open_on_day method"""
        with app.app_context():
            business_hours = {
                'mon': '09:00-18:00',
                'tue': '09:00-18:00',
                'wed': 'closed',
                'thu': '09:00-18:00',
                'fri': '09:00-18:00',
                'sat': '10:00-17:00',
                'sun': 'closed'
            }

            store = Store(**sample_store_data)
            store.business_hours = business_hours
            db.session.add(store)
            db.session.commit()

            assert store.is_open_on_day('mon') is True
            assert store.is_open_on_day('wed') is False
            assert store.is_open_on_day('sun') is False

    def test_store_get_hours_for_day(self, app, sample_store_data):
        """Test get_hours_for_day method"""
        with app.app_context():
            business_hours = {
                'mon': '09:00-18:00',
                'tue': '09:00-18:00',
                'wed': 'closed',
                'thu': '09:00-18:00',
                'fri': '09:00-18:00',
                'sat': '10:00-17:00',
                'sun': 'closed'
            }

            store = Store(**sample_store_data)
            store.business_hours = business_hours
            db.session.add(store)
            db.session.commit()

            assert store.get_hours_for_day('mon') == '09:00-18:00'
            assert store.get_hours_for_day('wed') == 'Closed'
            assert store.get_hours_for_day('sat') == '10:00-17:00'

    def test_store_update_status(self, app, sample_store_data):
        """Test update_status method"""
        with app.app_context():
            store = Store(**sample_store_data)
            db.session.add(store)
            db.session.commit()

            original_updated_at = store.updated_at

            # Valid status update
            store.update_status('temporarily_closed')
            assert store.status == 'temporarily_closed'
            assert store.updated_at > original_updated_at

            # Invalid status update (should not change)
            store.update_status('invalid_status')
            assert store.status == 'temporarily_closed'

    def test_store_update_business_hours(self, app, sample_store_data):
        """Test update_business_hours method"""
        with app.app_context():
            store = Store(**sample_store_data)
            db.session.add(store)
            db.session.commit()

            original_updated_at = store.updated_at

            new_hours = {
                'mon': '10:00-19:00',
                'tue': '10:00-19:00',
                'wed': '10:00-19:00',
                'thu': '10:00-19:00',
                'fri': '10:00-19:00',
                'sat': 'closed',
                'sun': 'closed'
            }

            store.update_business_hours(new_hours)
            assert store.business_hours == new_hours
            assert store.updated_at > original_updated_at

            # Invalid input (should not change)
            store.update_business_hours("invalid")
            assert store.business_hours == new_hours

    def test_store_to_dict(self, app, sample_store_data):
        """Test to_dict method"""
        with app.app_context():
            store = Store(**sample_store_data)
            db.session.add(store)
            db.session.commit()

            store_dict = store.to_dict()

            assert isinstance(store_dict, dict)
            assert store_dict['id'] == store.id
            assert store_dict['name'] == store.name
            assert store_dict['address'] == store.address
            assert store_dict['status'] == store.status
            assert 'business_years' in store_dict
            assert 'is_active' in store_dict
            assert 'location_full' in store_dict

    def test_store_str_representation(self, app, sample_store_data):
        """Test string representation methods"""
        with app.app_context():
            store = Store(**sample_store_data)
            db.session.add(store)
            db.session.commit()

            str_repr = str(store)
            repr_repr = repr(store)

            assert store.name in str_repr
            assert store.status in str_repr
            assert store.name in repr_repr
            assert str(store.id) in repr_repr

    def test_store_get_by_status_classmethod(self, app):
        """Test get_by_status class method"""
        with app.app_context():
            # Create stores with different statuses
            active_store = Store(name="Active Store", address="123 Active St", status='active')
            inactive_store = Store(name="Inactive Store", address="123 Inactive St", status='inactive')
            temp_closed_store = Store(name="Temp Closed Store", address="123 Temp St", status='temporarily_closed')

            db.session.add_all([active_store, inactive_store, temp_closed_store])
            db.session.commit()

            # Test filtering by status
            active_stores = Store.get_by_status('active').all()
            inactive_stores = Store.get_by_status('inactive').all()
            temp_closed_stores = Store.get_by_status('temporarily_closed').all()

            assert len(active_stores) == 1
            assert len(inactive_stores) == 1
            assert len(temp_closed_stores) == 1
            assert active_stores[0].name == "Active Store"

    def test_store_get_active_stores_classmethod(self, app):
        """Test get_active_stores class method"""
        with app.app_context():
            # Create stores with different statuses
            active_store1 = Store(name="Active Store 1", address="123 Active St", status='active')
            active_store2 = Store(name="Active Store 2", address="456 Active St", status='active')
            inactive_store = Store(name="Inactive Store", address="123 Inactive St", status='inactive')

            db.session.add_all([active_store1, active_store2, inactive_store])
            db.session.commit()

            active_stores = Store.get_active_stores().all()

            assert len(active_stores) == 2
            active_names = [store.name for store in active_stores]
            assert "Active Store 1" in active_names
            assert "Active Store 2" in active_names

    def test_store_get_by_location_classmethod(self, app):
        """Test get_by_location class method"""
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
            shibuya_store = Store(
                name="Another Shibuya Store",
                address="456 Shibuya St",
                location_prefecture="東京都",
                location_city="渋谷区"
            )

            db.session.add_all([tokyo_store, osaka_store, shibuya_store])
            db.session.commit()

            # Test filtering by prefecture
            tokyo_stores = Store.get_by_location(prefecture="東京都").all()
            assert len(tokyo_stores) == 2

            # Test filtering by city
            shibuya_stores = Store.get_by_location(city="渋谷区").all()
            assert len(shibuya_stores) == 2

            # Test filtering by both prefecture and city
            tokyo_shibuya_stores = Store.get_by_location(prefecture="東京都", city="渋谷区").all()
            assert len(tokyo_shibuya_stores) == 2

    def test_store_search_classmethod(self, app):
        """Test search class method"""
        with app.app_context():
            # Create stores with different names and addresses
            store1 = Store(name="Coffee Shop", address="123 Main St, Tokyo")
            store2 = Store(name="Tea House", address="456 Tea St, Osaka")
            store3 = Store(name="Cafe Tokyo", address="789 Cafe Ave, Tokyo")

            db.session.add_all([store1, store2, store3])
            db.session.commit()

            # Search by name
            coffee_stores = Store.search("Coffee").all()
            assert len(coffee_stores) == 1
            assert coffee_stores[0].name == "Coffee Shop"

            # Search by address
            tokyo_stores = Store.search("Tokyo").all()
            assert len(tokyo_stores) == 2

            # Empty search
            all_stores = Store.search("").all()
            assert len(all_stores) == 3

            # No matches
            no_matches = Store.search("nonexistent").all()
            assert len(no_matches) == 0

    def test_store_default_business_hours(self, app):
        """Test default business hours generation"""
        with app.app_context():
            store = Store(name="Test Store", address="123 Test St")
            db.session.add(store)
            db.session.commit()

            default_hours = store.business_hours
            assert isinstance(default_hours, dict)
            assert 'mon' in default_hours
            assert 'sun' in default_hours
            assert default_hours['mon'] == '09:00-18:00'
            assert default_hours['sun'] == 'closed'

    def test_store_timestamps(self, app, sample_store_data):
        """Test creation and update timestamps"""
        with app.app_context():
            store = Store(**sample_store_data)
            db.session.add(store)
            db.session.commit()

            assert store.created_at is not None
            assert store.updated_at is not None
            assert isinstance(store.created_at, datetime)
            assert isinstance(store.updated_at, datetime)

            original_updated_at = store.updated_at

            # Update store
            store.name = "Updated Store Name"
            db.session.commit()

            # updated_at should change automatically
            assert store.updated_at > original_updated_at