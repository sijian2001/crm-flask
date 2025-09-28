from typing import List


class CustomerConfig:
    """Customer management configuration class"""

    # Pagination settings
    ITEMS_PER_PAGE = 10
    MAX_ITEMS_PER_PAGE = 100

    # Search configuration
    SEARCH_FIELDS = ['first_name', 'last_name', 'email', 'company']

    # Field length limits (corresponds to database constraints)
    FIELD_LIMITS = {
        'first_name': 50,
        'last_name': 50,
        'email': 120,
        'phone': 20,
        'company': 100,
        'notes': 1000
    }

    # Form validation settings
    EMAIL_DOMAIN_VALIDATION = True
    PHONE_FORMAT_VALIDATION = False  # Set to True to enable strict phone validation

    # Export settings
    EXPORT_FORMATS = ['csv', 'excel', 'pdf']
    MAX_EXPORT_RECORDS = 1000

    # Security settings
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
        if app_config:
            return app_config.get('CUSTOMER_ITEMS_PER_PAGE', cls.ITEMS_PER_PAGE)
        return cls.ITEMS_PER_PAGE

    @classmethod
    def get_search_fields(cls, app_config=None) -> List[str]:
        """
        Get search fields from Flask config or use default

        Args:
            app_config: Flask application config object

        Returns:
            List of searchable field names
        """
        if app_config:
            return app_config.get('CUSTOMER_SEARCH_FIELDS', cls.SEARCH_FIELDS)
        return cls.SEARCH_FIELDS

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
        if app_config:
            limits = app_config.get('CUSTOMER_FIELD_LIMITS', cls.FIELD_LIMITS)
            return limits.get(field_name, cls.FIELD_LIMITS.get(field_name, 255))
        return cls.FIELD_LIMITS.get(field_name, 255)

    @classmethod
    def is_audit_enabled(cls, app_config=None) -> bool:
        """
        Check if audit logging is enabled

        Args:
            app_config: Flask application config object

        Returns:
            True if audit logging is enabled
        """
        if app_config:
            return app_config.get('CUSTOMER_ENABLE_AUDIT_LOG', cls.ENABLE_AUDIT_LOG)
        return cls.ENABLE_AUDIT_LOG