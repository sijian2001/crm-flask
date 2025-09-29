"""
Test cases for Store Views

This module contains comprehensive tests for the store views including
HTTP endpoints, form handling, and authentication tests.
"""
import pytest
import json
from datetime import date

from models import db, Store, User


class TestStoreViews:
    """Test cases for Store Views"""

    def test_store_index_requires_login(self, app, client):
        """Test that store index requires authentication"""
        with app.app_context():
            response = client.get('/stores/')
            assert response.status_code == 302
            assert '/auth/login' in response.location

    def test_store_index_authenticated(self, app, client, sample_user):
        """Test store index with authenticated user"""
        with app.app_context():
            # Create test stores
            store1 = Store(name="Store 1", address="123 Test St 1", status='active')
            store2 = Store(name="Store 2", address="123 Test St 2", status='inactive')
            db.session.add_all([store1, store2])
            db.session.commit()

            # Login user
            client.post('/auth/login', data={
                'username': sample_user.username,
                'password': 'testpass'
            })

            response = client.get('/stores/')
            assert response.status_code == 200
            assert b'Store 1' in response.data
            assert b'Store 2' in response.data
            assert b'\xe5\xba\x97\xe8\x88\x97\xe7\xae\xa1\xe7\x90\x86' in response.data  # "店舗管理" in UTF-8

    def test_store_index_with_search(self, app, client, sample_user):
        """Test store index with search functionality"""
        with app.app_context():
            # Create test stores
            coffee_store = Store(name="Coffee Shop", address="123 Coffee St", status='active')
            tea_store = Store(name="Tea House", address="456 Tea Ave", status='active')
            db.session.add_all([coffee_store, tea_store])
            db.session.commit()

            # Login user
            client.post('/auth/login', data={
                'username': sample_user.username,
                'password': 'testpass'
            })

            # Search for coffee
            response = client.get('/stores/?search=Coffee')
            assert response.status_code == 200
            assert b'Coffee Shop' in response.data
            assert b'Tea House' not in response.data

    def test_store_index_with_status_filter(self, app, client, sample_user):
        """Test store index with status filtering"""
        with app.app_context():
            # Create stores with different statuses
            active_store = Store(name="Active Store", address="123 Active St", status='active')
            inactive_store = Store(name="Inactive Store", address="123 Inactive St", status='inactive')
            db.session.add_all([active_store, inactive_store])
            db.session.commit()

            # Login user
            client.post('/auth/login', data={
                'username': sample_user.username,
                'password': 'testpass'
            })

            # Filter by active status
            response = client.get('/stores/?status=active')
            assert response.status_code == 200
            assert b'Active Store' in response.data
            assert b'Inactive Store' not in response.data

    def test_store_view_success(self, app, client, sample_user, sample_store_data):
        """Test store detail view"""
        with app.app_context():
            store = Store(**sample_store_data)
            db.session.add(store)
            db.session.commit()

            # Login user
            client.post('/auth/login', data={
                'username': sample_user.username,
                'password': 'testpass'
            })

            response = client.get(f'/stores/view/{store.id}')
            assert response.status_code == 200
            assert store.name.encode() in response.data
            assert store.address.encode() in response.data

    def test_store_view_not_found(self, app, client, sample_user):
        """Test store detail view with non-existent store"""
        with app.app_context():
            # Login user
            client.post('/auth/login', data={
                'username': sample_user.username,
                'password': 'testpass'
            })

            response = client.get('/stores/view/99999')
            assert response.status_code == 302
            assert '/stores/' in response.location

    def test_store_create_get(self, app, client, sample_user):
        """Test store creation form display"""
        with app.app_context():
            # Login user
            client.post('/auth/login', data={
                'username': sample_user.username,
                'password': 'testpass'
            })

            response = client.get('/stores/create')
            assert response.status_code == 200
            assert b'\xe6\x96\xb0\xe8\xa6\x8f\xe5\xba\x97\xe8\x88\x97\xe7\x99\xbb\xe9\x8c\xb2' in response.data  # "新規店舗登録"

    def test_store_create_post_success(self, app, client, sample_user):
        """Test successful store creation"""
        with app.app_context():
            # Login user
            client.post('/auth/login', data={
                'username': sample_user.username,
                'password': 'testpass'
            })

            store_data = {
                'name': 'New Test Store',
                'address': '123 New Test St',
                'phone': '123-456-7890',
                'email': 'test@newstore.com',
                'location_prefecture': '東京都',
                'location_city': '渋谷区',
                'status': 'active',
                'establishment_date': '2023-01-01',
                'monday_hours': '09:00-18:00',
                'tuesday_hours': '09:00-18:00',
                'wednesday_hours': '09:00-18:00',
                'thursday_hours': '09:00-18:00',
                'friday_hours': '09:00-18:00',
                'saturday_hours': '10:00-17:00',
                'sunday_hours': 'closed',
                'closed_days': '日曜日'
            }

            response = client.post('/stores/create', data=store_data)
            assert response.status_code == 302

            # Verify store was created
            store = Store.query.filter_by(name='New Test Store').first()
            assert store is not None
            assert store.address == '123 New Test St'

    def test_store_create_post_missing_name(self, app, client, sample_user):
        """Test store creation with missing name"""
        with app.app_context():
            # Login user
            client.post('/auth/login', data={
                'username': sample_user.username,
                'password': 'testpass'
            })

            store_data = {
                'name': '',  # Missing name
                'address': '123 Test St'
            }

            response = client.post('/stores/create', data=store_data)
            assert response.status_code == 200  # Form validation error, stays on create page

    def test_store_edit_get(self, app, client, sample_user, sample_store_data):
        """Test store edit form display"""
        with app.app_context():
            store = Store(**sample_store_data)
            db.session.add(store)
            db.session.commit()

            # Login user
            client.post('/auth/login', data={
                'username': sample_user.username,
                'password': 'testpass'
            })

            response = client.get(f'/stores/edit/{store.id}')
            assert response.status_code == 200
            assert store.name.encode() in response.data

    def test_store_edit_post_success(self, app, client, sample_user, sample_store_data):
        """Test successful store update"""
        with app.app_context():
            store = Store(**sample_store_data)
            db.session.add(store)
            db.session.commit()

            # Login user
            client.post('/auth/login', data={
                'username': sample_user.username,
                'password': 'testpass'
            })

            update_data = {
                'name': 'Updated Store Name',
                'address': store.address,
                'phone': '987-654-3210',
                'email': store.email,
                'location_prefecture': store.location_prefecture,
                'location_city': store.location_city,
                'status': 'temporarily_closed',
                'establishment_date': store.establishment_date.isoformat() if store.establishment_date else '',
                'monday_hours': '10:00-19:00',
                'tuesday_hours': '10:00-19:00',
                'wednesday_hours': '10:00-19:00',
                'thursday_hours': '10:00-19:00',
                'friday_hours': '10:00-19:00',
                'saturday_hours': 'closed',
                'sunday_hours': 'closed',
                'closed_days': '土日祝'
            }

            response = client.post(f'/stores/edit/{store.id}', data=update_data)
            assert response.status_code == 302

            # Verify store was updated
            updated_store = Store.query.get(store.id)
            assert updated_store.name == 'Updated Store Name'
            assert updated_store.phone == '987-654-3210'
            assert updated_store.status == 'temporarily_closed'

    def test_store_edit_not_found(self, app, client, sample_user):
        """Test editing non-existent store"""
        with app.app_context():
            # Login user
            client.post('/auth/login', data={
                'username': sample_user.username,
                'password': 'testpass'
            })

            response = client.get('/stores/edit/99999')
            assert response.status_code == 302
            assert '/stores/' in response.location

    def test_store_delete_success(self, app, client, sample_user, sample_store_data):
        """Test successful store deletion"""
        with app.app_context():
            store = Store(**sample_store_data)
            db.session.add(store)
            db.session.commit()

            store_id = store.id

            # Login user
            client.post('/auth/login', data={
                'username': sample_user.username,
                'password': 'testpass'
            })

            response = client.post(f'/stores/delete/{store_id}')
            assert response.status_code == 302
            assert '/stores/' in response.location

            # Verify store was deleted
            deleted_store = Store.query.get(store_id)
            assert deleted_store is None

    def test_store_delete_not_found(self, app, client, sample_user):
        """Test deleting non-existent store"""
        with app.app_context():
            # Login user
            client.post('/auth/login', data={
                'username': sample_user.username,
                'password': 'testpass'
            })

            response = client.post('/stores/delete/99999')
            assert response.status_code == 302
            assert '/stores/' in response.location

    def test_store_search_api(self, app, client, sample_user):
        """Test store search API"""
        with app.app_context():
            # Create test stores
            coffee_store = Store(name="Coffee Shop", address="123 Coffee St", status='active')
            tea_store = Store(name="Tea House", address="456 Tea Ave", status='active')
            db.session.add_all([coffee_store, tea_store])
            db.session.commit()

            # Login user
            client.post('/auth/login', data={
                'username': sample_user.username,
                'password': 'testpass'
            })

            # Test search API
            response = client.get('/stores/search?q=Coffee')
            assert response.status_code == 200

            data = json.loads(response.data)
            assert 'stores' in data
            assert len(data['stores']) == 1
            assert data['stores'][0]['name'] == 'Coffee Shop'

    def test_store_get_cities_api(self, app, client, sample_user):
        """Test get cities API"""
        with app.app_context():
            # Create stores with cities
            tokyo_store = Store(
                name="Tokyo Store",
                address="123 Tokyo St",
                location_prefecture="東京都",
                location_city="渋谷区"
            )
            db.session.add(tokyo_store)
            db.session.commit()

            # Login user
            client.post('/auth/login', data={
                'username': sample_user.username,
                'password': 'testpass'
            })

            response = client.get('/stores/api/cities/東京都')
            assert response.status_code == 200

            data = json.loads(response.data)
            assert 'cities' in data
            assert '渋谷区' in data['cities']

    def test_store_get_statistics_api(self, app, client, sample_user):
        """Test get statistics API"""
        with app.app_context():
            # Create test stores
            active_store = Store(name="Active Store", address="123 Active St", status='active')
            inactive_store = Store(name="Inactive Store", address="123 Inactive St", status='inactive')
            db.session.add_all([active_store, inactive_store])
            db.session.commit()

            # Login user
            client.post('/auth/login', data={
                'username': sample_user.username,
                'password': 'testpass'
            })

            response = client.get('/stores/api/statistics')
            assert response.status_code == 200

            data = json.loads(response.data)
            assert 'total_stores' in data
            assert 'active_stores' in data
            assert data['total_stores'] == 2
            assert data['active_stores'] == 1

    def test_store_get_prefectures_api(self, app, client, sample_user):
        """Test get prefectures API"""
        with app.app_context():
            # Create stores with prefectures
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

            # Login user
            client.post('/auth/login', data={
                'username': sample_user.username,
                'password': 'testpass'
            })

            response = client.get('/stores/api/prefectures')
            assert response.status_code == 200

            data = json.loads(response.data)
            assert 'prefectures' in data
            assert '東京都' in data['prefectures']
            assert '大阪府' in data['prefectures']

    def test_store_context_processors(self, app, client, sample_user, sample_store_data):
        """Test store template context processors"""
        with app.app_context():
            store = Store(**sample_store_data)
            store.business_hours = {
                'mon': '09:00-18:00',
                'tue': '09:00-18:00',
                'wed': 'closed',
                'thu': '09:00-18:00',
                'fri': '09:00-18:00',
                'sat': '10:00-17:00',
                'sun': 'closed'
            }
            db.session.add(store)
            db.session.commit()

            # Login user
            client.post('/auth/login', data={
                'username': sample_user.username,
                'password': 'testpass'
            })

            response = client.get(f'/stores/view/{store.id}')
            assert response.status_code == 200

            # Check that Japanese day names are displayed
            assert '月' in response.data.decode('utf-8')
            assert '火' in response.data.decode('utf-8')

    def test_store_pagination(self, app, client, sample_user):
        """Test store list pagination"""
        with app.app_context():
            # Create many stores
            for i in range(25):
                store = Store(name=f"Store {i+1}", address=f"123 Test St {i+1}")
                db.session.add(store)
            db.session.commit()

            # Login user
            client.post('/auth/login', data={
                'username': sample_user.username,
                'password': 'testpass'
            })

            # Test first page
            response = client.get('/stores/?page=1')
            assert response.status_code == 200
            assert 'Store 1' in response.data.decode('utf-8')

            # Test second page
            response = client.get('/stores/?page=2')
            assert response.status_code == 200

    def test_store_sorting(self, app, client, sample_user):
        """Test store list sorting"""
        with app.app_context():
            # Create stores with different names
            store_z = Store(name="Zebra Store", address="123 Z St")
            store_a = Store(name="Apple Store", address="123 A St")
            db.session.add_all([store_z, store_a])
            db.session.commit()

            # Login user
            client.post('/auth/login', data={
                'username': sample_user.username,
                'password': 'testpass'
            })

            # Test ascending sort
            response = client.get('/stores/?sort_by=name&sort_order=asc')
            assert response.status_code == 200
            content = response.data.decode('utf-8')
            apple_pos = content.find('Apple Store')
            zebra_pos = content.find('Zebra Store')
            assert apple_pos < zebra_pos

            # Test descending sort
            response = client.get('/stores/?sort_by=name&sort_order=desc')
            assert response.status_code == 200
            content = response.data.decode('utf-8')
            apple_pos = content.find('Apple Store')
            zebra_pos = content.find('Zebra Store')
            assert zebra_pos < apple_pos


class TestStoreFormsIntegration:
    """Test store forms integration with views"""

    def test_store_form_business_hours_integration(self, app, client, sample_user):
        """Test business hours form integration"""
        with app.app_context():
            # Login user
            client.post('/auth/login', data={
                'username': sample_user.username,
                'password': 'testpass'
            })

            store_data = {
                'name': 'Hours Test Store',
                'address': '123 Hours St',
                'status': 'active',
                'monday_hours': '09:00-18:00',
                'tuesday_hours': '09:00-18:00',
                'wednesday_hours': 'closed',
                'thursday_hours': '09:00-18:00',
                'friday_hours': '09:00-18:00',
                'saturday_hours': '10:00-17:00',
                'sunday_hours': 'closed'
            }

            response = client.post('/stores/create', data=store_data)
            assert response.status_code == 302

            # Verify business hours were saved correctly
            store = Store.query.filter_by(name='Hours Test Store').first()
            assert store is not None
            assert store.business_hours['mon'] == '09:00-18:00'
            assert store.business_hours['wed'] == 'closed'
            assert store.business_hours['sun'] == 'closed'

    def test_store_form_validation_integration(self, app, client, sample_user):
        """Test form validation integration"""
        with app.app_context():
            # Login user
            client.post('/auth/login', data={
                'username': sample_user.username,
                'password': 'testpass'
            })

            # Test with invalid email
            store_data = {
                'name': 'Validation Test Store',
                'address': '123 Validation St',
                'email': 'invalid-email',  # Invalid email format
                'status': 'active'
            }

            response = client.post('/stores/create', data=store_data)
            assert response.status_code == 200  # Should stay on form due to validation error

            # Verify store was not created
            store = Store.query.filter_by(name='Validation Test Store').first()
            assert store is None