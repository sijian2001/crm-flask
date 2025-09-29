from typing import Dict, Any, List

from base_config import BaseConfig


class CustomerConfig(BaseConfig):
    """Customer management configuration class"""

    def get_config_prefix(self) -> str:
        """Get configuration prefix for environment variables"""
        return 'CUSTOMER_'

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values"""
        return {
            # Pagination settings
            'pagination': {
                'items_per_page': 10,
                'max_items_per_page': 100
            },

            # Search configuration
            'search': {
                'fields': ['first_name', 'last_name', 'email', 'company']
            },

            # Field length limits (corresponds to database constraints)
            'field_limits': {
                'first_name': 50,
                'last_name': 50,
                'email': 120,
                'phone': 20,
                'company': 100,
                'notes': 1000
            },

            # Form validation settings
            'validation': {
                'email_domain_validation': True,
                'phone_format_validation': False  # Set to True to enable strict phone validation
            },

            # Export settings
            'export': {
                'formats': ['csv', 'excel', 'pdf'],
                'max_export_records': 1000
            },

            # Security settings
            'security': {
                'enable_audit_log': True,
                'log_customer_access': True
            }
        }

    # 後方互換性のためのクラス属性（廃止予定）
    ITEMS_PER_PAGE = 10
    MAX_ITEMS_PER_PAGE = 100
    SEARCH_FIELDS = ['first_name', 'last_name', 'email', 'company']
    FIELD_LIMITS = {
        'first_name': 50,
        'last_name': 50,
        'email': 120,
        'phone': 20,
        'company': 100,
        'notes': 1000
    }
    EMAIL_DOMAIN_VALIDATION = True
    PHONE_FORMAT_VALIDATION = False
    EXPORT_FORMATS = ['csv', 'excel', 'pdf']
    MAX_EXPORT_RECORDS = 1000
    ENABLE_AUDIT_LOG = True
    LOG_CUSTOMER_ACCESS = True

    @classmethod
    def get_items_per_page(cls, app_config=None) -> int:
        """
        Get items per page from Flask config or use default

        Args:
            app_config: Flask application config object

        Returns:
            Number of items per page
        """
        instance = cls.get_instance()
        return instance.get_value('pagination.items_per_page', cls.ITEMS_PER_PAGE)

    @classmethod
    def get_search_fields(cls, app_config=None) -> List[str]:
        """
        Get search fields from Flask config or use default

        Args:
            app_config: Flask application config object

        Returns:
            List of searchable field names
        """
        instance = cls.get_instance()
        return instance.get_value('search.fields', cls.SEARCH_FIELDS)

    @classmethod
    def get_field_limit(cls, field_name: str, app_config=None) -> int:
        """
        Get field length limit

        Args:
            field_name: Name of the field
            app_config: Flask application config object

        Returns:
            Maximum length for the field
        """
        instance = cls.get_instance()
        limits = instance.get_value('field_limits', cls.FIELD_LIMITS)
        return limits.get(field_name, 255)

    @classmethod
    def is_audit_enabled(cls, app_config=None) -> bool:
        """
        Check if audit logging is enabled

        Args:
            app_config: Flask application config object

        Returns:
            True if audit logging is enabled
        """
        instance = cls.get_instance()
        return instance.get_value('security.enable_audit_log', cls.ENABLE_AUDIT_LOG)