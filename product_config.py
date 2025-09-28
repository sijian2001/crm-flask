"""
Product management configuration module

This module provides configuration management for product-related settings,
following the same pattern as customer_config.py for consistency.
"""
from typing import Dict, Any, Optional
import os


class ProductConfig:
    """
    Configuration class for product management settings

    Provides centralized configuration for product features including
    pagination, validation rules, stock management, and search settings.
    """

    # Default configuration values
    _DEFAULT_CONFIG = {
        # ページネーション設定
        'pagination': {
            'per_page': 20,
            'max_per_page': 100,
            'orphans': 3
        },

        # 検索設定
        'search': {
            'min_length': 2,
            'max_results': 1000,
            'search_fields': ['name', 'sku', 'description']
        },

        # バリデーション設定
        'validation': {
            'name_max_length': 200,
            'sku_max_length': 50,
            'description_max_length': 2000,
            'price_max_digits': 10,
            'price_decimal_places': 2,
            'stock_max_value': 999999
        },

        # 在庫管理設定
        'inventory': {
            'default_min_stock_level': 5,
            'low_stock_warning_threshold': 10,
            'auto_reorder_enabled': False,
            'track_cost': True
        },

        # カテゴリ設定
        'category': {
            'max_depth': 5,
            'name_max_length': 100,
            'description_max_length': 1000,
            'allow_empty_categories': True
        },

        # 表示設定
        'display': {
            'show_inactive_products': False,
            'show_zero_stock_products': True,
            'default_sort_field': 'name',
            'default_sort_order': 'asc',
            'image_upload_enabled': False
        },

        # エクスポート設定
        'export': {
            'formats': ['csv', 'xlsx'],
            'max_export_records': 10000,
            'include_inactive': False
        }
    }

    # キャッシュされた設定
    _cached_config: Optional[Dict[str, Any]] = None
    _flask_app = None

    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """
        Get complete product configuration

        Returns cached configuration if available, otherwise loads from
        environment variables and defaults.

        Returns:
            Dict containing all product configuration settings
        """
        if cls._cached_config is None:
            cls._cached_config = cls._load_config()
        return cls._cached_config

    @classmethod
    def _load_config(cls) -> Dict[str, Any]:
        """
        Load configuration from environment variables with fallbacks to defaults

        Returns:
            Dict containing loaded configuration
        """
        config = cls._DEFAULT_CONFIG.copy()

        # 環境変数から設定を読み込み
        cls._update_from_env(config)

        # Flask設定から読み込み（利用可能な場合）
        if cls._flask_app:
            cls._update_from_flask_config(config)

        return config

    @classmethod
    def _update_from_env(cls, config: Dict[str, Any]) -> None:
        """
        Update configuration from environment variables

        Args:
            config: Configuration dictionary to update
        """
        # ページネーション設定
        if per_page := os.getenv('PRODUCT_PAGINATION_PER_PAGE'):
            config['pagination']['per_page'] = int(per_page)

        if max_per_page := os.getenv('PRODUCT_PAGINATION_MAX_PER_PAGE'):
            config['pagination']['max_per_page'] = int(max_per_page)

        # 検索設定
        if min_length := os.getenv('PRODUCT_SEARCH_MIN_LENGTH'):
            config['search']['min_length'] = int(min_length)

        # 在庫設定
        if min_stock := os.getenv('PRODUCT_DEFAULT_MIN_STOCK'):
            config['inventory']['default_min_stock_level'] = int(min_stock)

        if auto_reorder := os.getenv('PRODUCT_AUTO_REORDER'):
            config['inventory']['auto_reorder_enabled'] = auto_reorder.lower() == 'true'

    @classmethod
    def _update_from_flask_config(cls, config: Dict[str, Any]) -> None:
        """
        Update configuration from Flask app config

        Args:
            config: Configuration dictionary to update
        """
        if not cls._flask_app:
            return

        flask_config = cls._flask_app.config

        # Flask設定からの読み込み
        config['pagination']['per_page'] = flask_config.get(
            'PRODUCT_PAGINATION_PER_PAGE',
            config['pagination']['per_page']
        )

        config['search']['min_length'] = flask_config.get(
            'PRODUCT_SEARCH_MIN_LENGTH',
            config['search']['min_length']
        )

        config['inventory']['default_min_stock_level'] = flask_config.get(
            'PRODUCT_DEFAULT_MIN_STOCK',
            config['inventory']['default_min_stock_level']
        )

    @classmethod
    def get_pagination_config(cls) -> Dict[str, Any]:
        """Get pagination-specific configuration"""
        return cls.get_config()['pagination']

    @classmethod
    def get_search_config(cls) -> Dict[str, Any]:
        """Get search-specific configuration"""
        return cls.get_config()['search']

    @classmethod
    def get_validation_config(cls) -> Dict[str, Any]:
        """Get validation-specific configuration"""
        return cls.get_config()['validation']

    @classmethod
    def get_inventory_config(cls) -> Dict[str, Any]:
        """Get inventory-specific configuration"""
        return cls.get_config()['inventory']

    @classmethod
    def get_category_config(cls) -> Dict[str, Any]:
        """Get category-specific configuration"""
        return cls.get_config()['category']

    @classmethod
    def get_display_config(cls) -> Dict[str, Any]:
        """Get display-specific configuration"""
        return cls.get_config()['display']

    @classmethod
    def init_app(cls, app) -> None:
        """
        Initialize configuration with Flask app

        Args:
            app: Flask application instance
        """
        cls._flask_app = app
        cls._cached_config = None  # Clear cache to reload with Flask config

    @classmethod
    def reload_config(cls) -> None:
        """Reload configuration from sources"""
        cls._cached_config = None

    @classmethod
    def get_name_max_length(cls) -> int:
        """Get maximum length for product names"""
        return cls.get_validation_config()['name_max_length']

    @classmethod
    def get_sku_max_length(cls) -> int:
        """Get maximum length for product SKUs"""
        return cls.get_validation_config()['sku_max_length']

    @classmethod
    def get_description_max_length(cls) -> int:
        """Get maximum length for product descriptions"""
        return cls.get_validation_config()['description_max_length']

    @classmethod
    def get_default_per_page(cls) -> int:
        """Get default number of products per page"""
        return cls.get_pagination_config()['per_page']

    @classmethod
    def get_search_min_length(cls) -> int:
        """Get minimum length for search queries"""
        return cls.get_search_config()['min_length']

    @classmethod
    def get_default_min_stock_level(cls) -> int:
        """Get default minimum stock level for new products"""
        return cls.get_inventory_config()['default_min_stock_level']

    @classmethod
    def is_low_stock_warning_enabled(cls) -> bool:
        """Check if low stock warnings are enabled"""
        return cls.get_inventory_config()['low_stock_warning_threshold'] > 0

    @classmethod
    def get_low_stock_threshold(cls) -> int:
        """Get threshold for low stock warnings"""
        return cls.get_inventory_config()['low_stock_warning_threshold']