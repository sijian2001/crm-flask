"""
Tests for Product configuration management

Test coverage for ProductConfig class functionality and settings management.
"""
import pytest
import os
from unittest.mock import patch
from product_config import ProductConfig


class TestProductConfig:
    """Test cases for ProductConfig class"""

    def setup_method(self):
        """Setup for each test method"""
        # Clear cached config before each test
        ProductConfig._cached_config = None
        ProductConfig._flask_app = None

    def test_get_default_config(self):
        """Test getting default configuration"""
        config = ProductConfig.get_config()

        assert config is not None
        assert 'pagination' in config
        assert 'search' in config
        assert 'validation' in config
        assert 'inventory' in config
        assert 'category' in config
        assert 'display' in config
        assert 'export' in config

    def test_pagination_config(self):
        """Test pagination configuration"""
        pagination = ProductConfig.get_pagination_config()

        assert pagination['per_page'] == 20
        assert pagination['max_per_page'] == 100
        assert pagination['orphans'] == 3

    def test_search_config(self):
        """Test search configuration"""
        search = ProductConfig.get_search_config()

        assert search['min_length'] == 2
        assert search['max_results'] == 1000
        assert 'name' in search['search_fields']
        assert 'sku' in search['search_fields']
        assert 'description' in search['search_fields']

    def test_validation_config(self):
        """Test validation configuration"""
        validation = ProductConfig.get_validation_config()

        assert validation['name_max_length'] == 200
        assert validation['sku_max_length'] == 50
        assert validation['description_max_length'] == 2000
        assert validation['price_max_digits'] == 10
        assert validation['price_decimal_places'] == 2
        assert validation['stock_max_value'] == 999999

    def test_inventory_config(self):
        """Test inventory configuration"""
        inventory = ProductConfig.get_inventory_config()

        assert inventory['default_min_stock_level'] == 5
        assert inventory['low_stock_warning_threshold'] == 10
        assert inventory['auto_reorder_enabled'] is False
        assert inventory['track_cost'] is True

    def test_category_config(self):
        """Test category configuration"""
        category = ProductConfig.get_category_config()

        assert category['max_depth'] == 5
        assert category['name_max_length'] == 100
        assert category['description_max_length'] == 1000
        assert category['allow_empty_categories'] is True

    def test_display_config(self):
        """Test display configuration"""
        display = ProductConfig.get_display_config()

        assert display['show_inactive_products'] is False
        assert display['show_zero_stock_products'] is True
        assert display['default_sort_field'] == 'name'
        assert display['default_sort_order'] == 'asc'
        assert display['image_upload_enabled'] is False

    def test_config_caching(self):
        """Test configuration caching"""
        # First call should load config
        config1 = ProductConfig.get_config()

        # Second call should return cached config
        config2 = ProductConfig.get_config()

        assert config1 is config2  # Should be the same object

    def test_reload_config(self):
        """Test configuration reloading"""
        # Get initial config
        config1 = ProductConfig.get_config()

        # Reload config
        ProductConfig.reload_config()

        # Get config again
        config2 = ProductConfig.get_config()

        # Should be different objects but same content
        assert config1 is not config2
        assert config1 == config2

    @patch.dict(os.environ, {
        'PRODUCT_PAGINATION_PER_PAGE': '25',
        'PRODUCT_SEARCH_MIN_LENGTH': '3',
        'PRODUCT_DEFAULT_MIN_STOCK': '10',
        'PRODUCT_AUTO_REORDER': 'true'
    })
    def test_environment_variable_override(self):
        """Test configuration override from environment variables"""
        # Clear cache to force reload with env vars
        ProductConfig._cached_config = None

        config = ProductConfig.get_config()

        assert config['pagination']['per_page'] == 25
        assert config['search']['min_length'] == 3
        assert config['inventory']['default_min_stock_level'] == 10
        assert config['inventory']['auto_reorder_enabled'] is True

    def test_flask_app_integration(self, app):
        """Test Flask app integration"""
        app.config['PRODUCT_PAGINATION_PER_PAGE'] = 30
        app.config['PRODUCT_SEARCH_MIN_LENGTH'] = 4

        ProductConfig.init_app(app)

        config = ProductConfig.get_config()

        assert config['pagination']['per_page'] == 30
        assert config['search']['min_length'] == 4

    def test_convenience_methods(self):
        """Test convenience methods for common settings"""
        assert ProductConfig.get_name_max_length() == 200
        assert ProductConfig.get_sku_max_length() == 50
        assert ProductConfig.get_description_max_length() == 2000
        assert ProductConfig.get_default_per_page() == 20
        assert ProductConfig.get_search_min_length() == 2
        assert ProductConfig.get_default_min_stock_level() == 5

    def test_low_stock_warning_settings(self):
        """Test low stock warning configuration"""
        assert ProductConfig.is_low_stock_warning_enabled() is True
        assert ProductConfig.get_low_stock_threshold() == 10

    @patch.dict(os.environ, {'PRODUCT_PAGINATION_PER_PAGE': 'invalid'})
    def test_invalid_environment_variable(self):
        """Test handling of invalid environment variables"""
        ProductConfig._cached_config = None

        # Should not raise exception and fall back to default
        config = ProductConfig.get_config()
        assert config['pagination']['per_page'] == 20  # Default value

    def test_nested_config_structure(self):
        """Test that nested configuration structure is maintained"""
        config = ProductConfig.get_config()

        # Test that we can access nested values
        assert config['validation']['name_max_length'] == 200
        assert config['inventory']['default_min_stock_level'] == 5
        assert config['category']['max_depth'] == 5

    def test_export_config(self):
        """Test export configuration"""
        config = ProductConfig.get_config()
        export_config = config['export']

        assert 'csv' in export_config['formats']
        assert 'xlsx' in export_config['formats']
        assert export_config['max_export_records'] == 10000
        assert export_config['include_inactive'] is False

    def test_init_app_clears_cache(self, app):
        """Test that init_app clears cached configuration"""
        # Get initial config
        config1 = ProductConfig.get_config()

        # Initialize with Flask app
        ProductConfig.init_app(app)

        # Get config again - should be reloaded
        config2 = ProductConfig.get_config()

        # Cache should have been cleared and reloaded
        assert ProductConfig._flask_app == app

    @patch.dict(os.environ, {}, clear=True)
    def test_all_defaults_with_no_env_vars(self):
        """Test that all defaults are used when no environment variables are set"""
        ProductConfig._cached_config = None

        config = ProductConfig.get_config()

        # Should match all default values
        assert config['pagination']['per_page'] == 20
        assert config['search']['min_length'] == 2
        assert config['validation']['name_max_length'] == 200
        assert config['inventory']['default_min_stock_level'] == 5
        assert config['category']['max_depth'] == 5