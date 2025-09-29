"""
Store management configuration module

This module provides configuration management for store-related settings,
extending BaseConfig for consistent configuration management.
"""
from typing import Dict, Any

from base_config import BaseConfig


class StoreConfig(BaseConfig):
    """
    Configuration class for store management settings

    Provides centralized configuration for store features including
    pagination, validation rules, business status management, and search settings.
    """

    def get_config_prefix(self) -> str:
        """Get configuration prefix for environment variables"""
        return 'STORE_'

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
                'search_fields': ['name', 'address', 'location_prefecture', 'location_city']
            },

            # バリデーション設定
            'validation': {
                'name_max_length': 200,
                'address_max_length': 500,
                'phone_max_length': 20,
                'email_max_length': 120,
                'prefecture_max_length': 50,
                'city_max_length': 100,
                'closed_days_max_length': 50
            },

            # 営業時間設定
            'business_hours': {
                'default_weekday_hours': '09:00-18:00',
                'default_weekend_hours': '10:00-17:00',
                'closed_indicator': 'closed',
                'valid_statuses': ['active', 'temporarily_closed', 'inactive']
            },

            # 地域設定
            'location': {
                'enable_prefecture_filter': True,
                'enable_city_filter': True,
                'auto_complete_cities': True
            },

            # 表示設定
            'display': {
                'show_inactive_stores': True,
                'show_temp_closed_stores': True,
                'default_sort_field': 'name',
                'default_sort_order': 'asc',
                'show_business_years': True,
                'show_statistics': True
            },

            # エクスポート設定
            'export': {
                'formats': ['csv', 'xlsx'],
                'max_export_records': 10000,
                'include_inactive': False,
                'include_business_hours': True
            },

            # API設定
            'api': {
                'enable_search_api': True,
                'enable_statistics_api': True,
                'enable_location_api': True,
                'max_api_results': 50
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
    def get_business_hours_config(cls) -> Dict[str, Any]:
        """Get business hours-specific configuration"""
        instance = cls.get_instance()
        return instance.get_value('business_hours', {})

    @classmethod
    def get_location_config(cls) -> Dict[str, Any]:
        """Get location-specific configuration"""
        instance = cls.get_instance()
        return instance.get_value('location', {})

    @classmethod
    def get_display_config(cls) -> Dict[str, Any]:
        """Get display-specific configuration"""
        instance = cls.get_instance()
        return instance.get_value('display', {})

    @classmethod
    def get_export_config(cls) -> Dict[str, Any]:
        """Get export-specific configuration"""
        instance = cls.get_instance()
        return instance.get_value('export', {})

    @classmethod
    def get_api_config(cls) -> Dict[str, Any]:
        """Get API-specific configuration"""
        instance = cls.get_instance()
        return instance.get_value('api', {})

    # 個別設定値のゲッター
    @classmethod
    def get_name_max_length(cls) -> int:
        """Get maximum length for store names"""
        instance = cls.get_instance()
        return instance.get_value('validation.name_max_length', 200)

    @classmethod
    def get_address_max_length(cls) -> int:
        """Get maximum length for store addresses"""
        instance = cls.get_instance()
        return instance.get_value('validation.address_max_length', 500)

    @classmethod
    def get_phone_max_length(cls) -> int:
        """Get maximum length for phone numbers"""
        instance = cls.get_instance()
        return instance.get_value('validation.phone_max_length', 20)

    @classmethod
    def get_email_max_length(cls) -> int:
        """Get maximum length for email addresses"""
        instance = cls.get_instance()
        return instance.get_value('validation.email_max_length', 120)

    @classmethod
    def get_default_per_page(cls) -> int:
        """Get default number of stores per page"""
        instance = cls.get_instance()
        return instance.get_value('pagination.per_page', 20)

    @classmethod
    def get_search_min_length(cls) -> int:
        """Get minimum length for search queries"""
        instance = cls.get_instance()
        return instance.get_value('search.min_length', 2)

    @classmethod
    def get_search_fields(cls) -> list:
        """Get list of searchable fields"""
        instance = cls.get_instance()
        return instance.get_value('search.search_fields', ['name', 'address'])

    @classmethod
    def get_valid_statuses(cls) -> list:
        """Get list of valid business statuses"""
        instance = cls.get_instance()
        return instance.get_value('business_hours.valid_statuses', ['active', 'temporarily_closed', 'inactive'])

    @classmethod
    def get_default_weekday_hours(cls) -> str:
        """Get default weekday business hours"""
        instance = cls.get_instance()
        return instance.get_value('business_hours.default_weekday_hours', '09:00-18:00')

    @classmethod
    def get_default_weekend_hours(cls) -> str:
        """Get default weekend business hours"""
        instance = cls.get_instance()
        return instance.get_value('business_hours.default_weekend_hours', '10:00-17:00')

    @classmethod
    def get_closed_indicator(cls) -> str:
        """Get closed indicator string"""
        instance = cls.get_instance()
        return instance.get_value('business_hours.closed_indicator', 'closed')

    @classmethod
    def is_prefecture_filter_enabled(cls) -> bool:
        """Check if prefecture filtering is enabled"""
        instance = cls.get_instance()
        return instance.get_value('location.enable_prefecture_filter', True)

    @classmethod
    def is_city_filter_enabled(cls) -> bool:
        """Check if city filtering is enabled"""
        instance = cls.get_instance()
        return instance.get_value('location.enable_city_filter', True)

    @classmethod
    def is_auto_complete_cities_enabled(cls) -> bool:
        """Check if city auto-completion is enabled"""
        instance = cls.get_instance()
        return instance.get_value('location.auto_complete_cities', True)

    @classmethod
    def should_show_inactive_stores(cls) -> bool:
        """Check if inactive stores should be shown"""
        instance = cls.get_instance()
        return instance.get_value('display.show_inactive_stores', True)

    @classmethod
    def should_show_temp_closed_stores(cls) -> bool:
        """Check if temporarily closed stores should be shown"""
        instance = cls.get_instance()
        return instance.get_value('display.show_temp_closed_stores', True)

    @classmethod
    def should_show_business_years(cls) -> bool:
        """Check if business years should be displayed"""
        instance = cls.get_instance()
        return instance.get_value('display.show_business_years', True)

    @classmethod
    def should_show_statistics(cls) -> bool:
        """Check if statistics should be displayed"""
        instance = cls.get_instance()
        return instance.get_value('display.show_statistics', True)

    @classmethod
    def get_default_sort_field(cls) -> str:
        """Get default sort field"""
        instance = cls.get_instance()
        return instance.get_value('display.default_sort_field', 'name')

    @classmethod
    def get_default_sort_order(cls) -> str:
        """Get default sort order"""
        instance = cls.get_instance()
        return instance.get_value('display.default_sort_order', 'asc')

    @classmethod
    def get_max_export_records(cls) -> int:
        """Get maximum number of records for export"""
        instance = cls.get_instance()
        return instance.get_value('export.max_export_records', 10000)

    @classmethod
    def should_include_inactive_in_export(cls) -> bool:
        """Check if inactive stores should be included in exports"""
        instance = cls.get_instance()
        return instance.get_value('export.include_inactive', False)

    @classmethod
    def should_include_business_hours_in_export(cls) -> bool:
        """Check if business hours should be included in exports"""
        instance = cls.get_instance()
        return instance.get_value('export.include_business_hours', True)

    @classmethod
    def is_search_api_enabled(cls) -> bool:
        """Check if search API is enabled"""
        instance = cls.get_instance()
        return instance.get_value('api.enable_search_api', True)

    @classmethod
    def is_statistics_api_enabled(cls) -> bool:
        """Check if statistics API is enabled"""
        instance = cls.get_instance()
        return instance.get_value('api.enable_statistics_api', True)

    @classmethod
    def is_location_api_enabled(cls) -> bool:
        """Check if location API is enabled"""
        instance = cls.get_instance()
        return instance.get_value('api.enable_location_api', True)

    @classmethod
    def get_max_api_results(cls) -> int:
        """Get maximum number of results for API calls"""
        instance = cls.get_instance()
        return instance.get_value('api.max_api_results', 50)

    @classmethod
    def reload_config(cls) -> None:
        """Reload configuration from sources"""
        instance = cls.get_instance()
        instance.reload_config()

    @classmethod
    def validate_store_config(cls) -> Dict[str, str]:
        """
        Validate store-specific configuration

        Returns:
            Dictionary of validation errors (empty if valid)
        """
        instance = cls.get_instance()
        errors = instance.validate_config()

        # Store-specific validations
        config = instance.get_config()

        # Validate pagination settings
        per_page = config.get('pagination', {}).get('per_page', 20)
        if per_page <= 0 or per_page > 1000:
            errors['pagination.per_page'] = 'Per page must be between 1 and 1000'

        # Validate search settings
        min_length = config.get('search', {}).get('min_length', 2)
        if min_length < 1 or min_length > 10:
            errors['search.min_length'] = 'Search minimum length must be between 1 and 10'

        # Validate business hour statuses
        valid_statuses = config.get('business_hours', {}).get('valid_statuses', [])
        required_statuses = ['active', 'temporarily_closed', 'inactive']
        for status in required_statuses:
            if status not in valid_statuses:
                errors['business_hours.valid_statuses'] = f'Missing required status: {status}'

        return errors