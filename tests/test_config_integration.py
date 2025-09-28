import pytest
from models import Customer, db
from services.customer_service import CustomerService


class TestConfigIntegration:
    """Test integration between configuration and application functionality"""

    def test_pagination_uses_config(self, app):
        """Test that pagination uses configuration settings"""
        with app.app_context():
            # Override config for testing
            app.config['CUSTOMER_ITEMS_PER_PAGE'] = 5

            # Create test customers
            customers = [
                Customer(first_name='太郎', last_name=f'田中{i}', email=f'tanaka{i}@example.com')
                for i in range(12)
            ]
            db.session.add_all(customers)
            db.session.commit()

            # Test pagination uses config value
            result = CustomerService.get_customers_with_pagination(page=1)
            assert len(result.items) == 5  # Should use config value, not default 10
            assert result.total == 12
            assert result.pages == 3  # 12 items / 5 per page = 3 pages

    def test_search_fields_uses_config(self, app):
        """Test that search functionality uses configuration"""
        with app.app_context():
            # Override config to search only first_name and email
            app.config['CUSTOMER_SEARCH_FIELDS'] = ['first_name', 'email']

            # Create test customers
            customers = [
                Customer(first_name='太郎', last_name='田中', email='tanaka@example.com', company='株式会社A'),
                Customer(first_name='花子', last_name='佐藤', email='hanako@example.com', company='株式会社太郎')
            ]
            db.session.add_all(customers)
            db.session.commit()

            # Search for '太郎' - should find both customers
            # 1. first_name matches '太郎'
            # 2. company contains '太郎' but since company is not in search fields, this shouldn't match
            result = CustomerService.get_customers_with_pagination(search='太郎')
            assert len(result.items) == 1  # Only first customer should match
            assert result.items[0].first_name == '太郎'

    def test_default_config_when_not_set(self, app):
        """Test default configuration when Flask config is not set"""
        with app.app_context():
            # Remove custom config if exists
            if 'CUSTOMER_ITEMS_PER_PAGE' in app.config:
                del app.config['CUSTOMER_ITEMS_PER_PAGE']

            # Create test customers
            customers = [
                Customer(first_name='太郎', last_name=f'田中{i}', email=f'default{i}@example.com')
                for i in range(15)
            ]
            db.session.add_all(customers)
            db.session.commit()

            # Should use default value (10)
            result = CustomerService.get_customers_with_pagination(page=1)
            assert len(result.items) == 10  # Default value
            assert result.total == 15
            assert result.pages == 2  # 15 items / 10 per page = 2 pages