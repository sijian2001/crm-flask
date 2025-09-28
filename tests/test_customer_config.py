import pytest
from customer_config import CustomerConfig


class TestCustomerConfig:
    """Customer configuration tests"""

    def test_default_config_values(self):
        """Test default configuration values"""
        assert CustomerConfig.ITEMS_PER_PAGE == 10
        assert CustomerConfig.MAX_ITEMS_PER_PAGE == 100
        assert CustomerConfig.SEARCH_FIELDS == ['first_name', 'last_name', 'email', 'company']
        assert CustomerConfig.ENABLE_AUDIT_LOG is True

    def test_field_limits(self):
        """Test field length limits"""
        expected_limits = {
            'first_name': 50,
            'last_name': 50,
            'email': 120,
            'phone': 20,
            'company': 100,
            'notes': 1000
        }
        assert CustomerConfig.FIELD_LIMITS == expected_limits

    def test_get_items_per_page_default(self):
        """Test get_items_per_page with default values"""
        result = CustomerConfig.get_items_per_page()
        assert result == 10

    def test_get_items_per_page_with_config(self):
        """Test get_items_per_page with Flask config"""
        mock_config = {'CUSTOMER_ITEMS_PER_PAGE': 20}
        result = CustomerConfig.get_items_per_page(mock_config)
        assert result == 20

    def test_get_items_per_page_fallback(self):
        """Test get_items_per_page fallback when config key is missing"""
        mock_config = {}
        result = CustomerConfig.get_items_per_page(mock_config)
        assert result == 10

    def test_get_search_fields_default(self):
        """Test get_search_fields with default values"""
        result = CustomerConfig.get_search_fields()
        assert result == ['first_name', 'last_name', 'email', 'company']

    def test_get_search_fields_with_config(self):
        """Test get_search_fields with Flask config"""
        custom_fields = ['first_name', 'email']
        mock_config = {'CUSTOMER_SEARCH_FIELDS': custom_fields}
        result = CustomerConfig.get_search_fields(mock_config)
        assert result == custom_fields

    def test_get_search_fields_fallback(self):
        """Test get_search_fields fallback when config key is missing"""
        mock_config = {}
        result = CustomerConfig.get_search_fields(mock_config)
        assert result == ['first_name', 'last_name', 'email', 'company']

    def test_get_field_limit_existing_field(self):
        """Test get_field_limit for existing field"""
        result = CustomerConfig.get_field_limit('first_name')
        assert result == 50

    def test_get_field_limit_non_existing_field(self):
        """Test get_field_limit for non-existing field"""
        result = CustomerConfig.get_field_limit('unknown_field')
        assert result == 255  # Default value

    def test_get_field_limit_with_config(self):
        """Test get_field_limit with Flask config"""
        custom_limits = {'first_name': 100}
        mock_config = {'CUSTOMER_FIELD_LIMITS': custom_limits}
        result = CustomerConfig.get_field_limit('first_name', mock_config)
        assert result == 100

    def test_get_field_limit_config_fallback(self):
        """Test get_field_limit fallback when field not in config"""
        custom_limits = {}
        mock_config = {'CUSTOMER_FIELD_LIMITS': custom_limits}
        result = CustomerConfig.get_field_limit('first_name', mock_config)
        assert result == 50  # Default from CustomerConfig.FIELD_LIMITS

    def test_is_audit_enabled_default(self):
        """Test is_audit_enabled with default values"""
        result = CustomerConfig.is_audit_enabled()
        assert result is True

    def test_is_audit_enabled_with_config_true(self):
        """Test is_audit_enabled with Flask config set to True"""
        mock_config = {'CUSTOMER_ENABLE_AUDIT_LOG': True}
        result = CustomerConfig.is_audit_enabled(mock_config)
        assert result is True

    def test_is_audit_enabled_with_config_false(self):
        """Test is_audit_enabled with Flask config set to False"""
        mock_config = {'CUSTOMER_ENABLE_AUDIT_LOG': False}
        result = CustomerConfig.is_audit_enabled(mock_config)
        assert result is False

    def test_is_audit_enabled_fallback(self):
        """Test is_audit_enabled fallback when config key is missing"""
        mock_config = {}
        result = CustomerConfig.is_audit_enabled(mock_config)
        assert result is True