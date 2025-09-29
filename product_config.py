"""
Product management configuration module

This module provides configuration management for product-related settings,
now extending BaseConfig for consistent configuration management.
"""
from typing import Dict, Any

from base_config import BaseConfig


class ProductConfig(BaseConfig):
    """
    Configuration class for product management settings

    Provides centralized configuration for product features including
    pagination, validation rules, stock management, and search settings.
    """

    def get_config_prefix(self) -> str:
        """Get configuration prefix for environment variables"""
        return 'PRODUCT_'

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values"""
        return {
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
                'stock_max_value': 100000,  # 業務要件に基づき100,000に変更（10万個まで）
                'price_max_value': 9999999.99  # 価格上限を追加（約1千万円まで）
            },

            # 在庫管理設定
            'inventory': {
                'default_min_stock_level': 10,  # デフォルト最小在庫を10個に増加
                'low_stock_warning_threshold': 20,  # 警告閾値を20個に増加
                'auto_reorder_enabled': False,
                'track_cost': True,
                'allow_negative_stock': False  # マイナス在庫を禁止
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

    # 便利メソッド（後方互換性のため）
    @classmethod
    def get_pagination_config(cls) -> Dict[str, Any]:
        """Get pagination-specific configuration"""
        instance = cls.get_instance()
        return instance.get_value('pagination', {})

    @classmethod
    def get_search_config(cls) -> Dict[str, Any]:
        """Get search-specific configuration"""
        instance = cls.get_instance()
        return instance.get_value('search', {})

    @classmethod
    def get_validation_config(cls) -> Dict[str, Any]:
        """Get validation-specific configuration"""
        instance = cls.get_instance()
        return instance.get_value('validation', {})

    @classmethod
    def get_inventory_config(cls) -> Dict[str, Any]:
        """Get inventory-specific configuration"""
        instance = cls.get_instance()
        return instance.get_value('inventory', {})

    @classmethod
    def get_category_config(cls) -> Dict[str, Any]:
        """Get category-specific configuration"""
        instance = cls.get_instance()
        return instance.get_value('category', {})

    @classmethod
    def get_display_config(cls) -> Dict[str, Any]:
        """Get display-specific configuration"""
        instance = cls.get_instance()
        return instance.get_value('display', {})

    @classmethod
    def get_name_max_length(cls) -> int:
        """Get maximum length for product names"""
        instance = cls.get_instance()
        return instance.get_value('validation.name_max_length', 200)

    @classmethod
    def get_sku_max_length(cls) -> int:
        """Get maximum length for product SKUs"""
        instance = cls.get_instance()
        return instance.get_value('validation.sku_max_length', 50)

    @classmethod
    def get_description_max_length(cls) -> int:
        """Get maximum length for product descriptions"""
        instance = cls.get_instance()
        return instance.get_value('validation.description_max_length', 2000)

    @classmethod
    def get_default_per_page(cls) -> int:
        """Get default number of products per page"""
        instance = cls.get_instance()
        return instance.get_value('pagination.per_page', 20)

    @classmethod
    def get_search_min_length(cls) -> int:
        """Get minimum length for search queries"""
        instance = cls.get_instance()
        return instance.get_value('search.min_length', 2)

    @classmethod
    def get_default_min_stock_level(cls) -> int:
        """Get default minimum stock level for new products"""
        instance = cls.get_instance()
        return instance.get_value('inventory.default_min_stock_level', 10)

    @classmethod
    def is_low_stock_warning_enabled(cls) -> bool:
        """Check if low stock warnings are enabled"""
        instance = cls.get_instance()
        return instance.get_value('inventory.low_stock_warning_threshold', 0) > 0

    @classmethod
    def get_low_stock_threshold(cls) -> int:
        """Get threshold for low stock warnings"""
        instance = cls.get_instance()
        return instance.get_value('inventory.low_stock_warning_threshold', 20)

    @classmethod
    def reload_config(cls) -> None:
        """Reload configuration from sources"""
        instance = cls.get_instance()
        instance.reload_config()