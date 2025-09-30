"""
Employee Configuration Management

This module provides configuration management for employee-related settings
including pagination, validation rules, default values, and business logic parameters.
"""
import os
from typing import Dict, Any, Optional
from datetime import datetime

from base_config import BaseConfig


class EmployeeConfig(BaseConfig):
    """
    Employee management configuration class

    Extends BaseConfig to provide employee-specific configuration management
    including HR policies, validation rules, and system defaults.
    """

    def __init__(self, app=None):
        """
        Initialize EmployeeConfig

        Args:
            app: Flask application instance (optional)
        """
        super().__init__()
        self._config_prefix = 'EMPLOYEE'
        if app:
            self.init_app(app)

    def get_config_prefix(self) -> str:
        """
        Get configuration prefix for environment variables

        Returns:
            Configuration prefix string
        """
        return self._config_prefix

    def get_default_config(self) -> Dict[str, Any]:
        """
        Get default employee configuration

        Returns:
            Dictionary containing default employee configuration
        """
        return {
            # Pagination settings
            'pagination': {
                'per_page': 20,
                'max_per_page': 100,
                'show_page_info': True,
                'show_total_count': True
            },

            # Search and filtering
            'search': {
                'min_length': 2,
                'max_results': 1000,
                'search_fields': ['first_name', 'last_name', 'employee_code', 'email'],
                'enable_fuzzy_search': False
            },

            # Validation rules
            'validation': {
                'employee_code': {
                    'min_length': 3,
                    'max_length': 20,
                    'pattern': r'^[A-Za-z0-9\-_]+$',
                    'required': True
                },
                'name': {
                    'first_name_max_length': 50,
                    'last_name_max_length': 50,
                    'required': True
                },
                'email': {
                    'max_length': 120,
                    'required': False,
                    'unique': True
                },
                'phone': {
                    'max_length': 20,
                    'pattern': r'^[\d\-\(\)\+\s]*$',
                    'required': False
                },
                'salary_level': {
                    'min_value': 1,
                    'max_value': 10,
                    'default': 1
                }
            },

            # Employment settings
            'employment': {
                'valid_statuses': ['active', 'inactive', 'on_leave', 'terminated'],
                'default_status': 'active',
                'auto_calculate_tenure': True,
                'tenure_calculation_method': 'precise',  # 'precise' or 'approximate'
                'probation_period_months': 3
            },

            # Organizational settings
            'organization': {
                'max_hierarchy_depth': 10,
                'allow_circular_reporting': False,
                'require_manager_approval': True,
                'auto_assign_department': False,
                'department_required': False
            },

            # Position and salary settings
            'positions': {
                'management_levels': [1, 2, 3, 4, 5],  # Levels considered management
                'default_level': 999,
                'auto_calculate_salary_range': True,
                'salary_multiplier_per_level': 0.1
            },

            # Business rules
            'business_rules': {
                'min_retirement_age': 60,
                'max_employment_years': 40,
                'mandatory_retirement_age': 65,
                'annual_leave_days': 20,
                'sick_leave_days': 10
            },

            # Display settings
            'display': {
                'show_inactive_employees': True,
                'show_terminated_employees': False,
                'show_salary_information': True,
                'show_personal_information': True,
                'default_sort_field': 'last_name',
                'default_sort_order': 'asc',
                'avatar_initials': True,
                'show_tenure_in_months': True
            },

            # Export settings
            'export': {
                'enabled': True,
                'formats': ['csv', 'excel', 'pdf'],
                'max_records': 10000,
                'include_sensitive_data': False
            },

            # Security settings
            'security': {
                'mask_salary_for_non_managers': True,
                'mask_personal_info_for_non_hr': True,
                'audit_changes': True,
                'require_reason_for_changes': True
            },

            # Notification settings
            'notifications': {
                'birthday_reminders': True,
                'work_anniversary_reminders': True,
                'probation_end_reminders': True,
                'retirement_reminders': True,
                'days_before_birthday': 7,
                'days_before_anniversary': 14,
                'days_before_retirement': 90
            },

            # Integration settings
            'integration': {
                'payroll_system_enabled': False,
                'attendance_system_enabled': False,
                'hr_system_enabled': False,
                'sync_frequency_hours': 24
            },

            # Performance settings
            'performance': {
                'cache_statistics': True,
                'cache_timeout_minutes': 15,
                'batch_size': 100,
                'use_eager_loading': True
            }
        }

    def get_pagination_config(self) -> Dict[str, Any]:
        """
        Get pagination configuration

        Returns:
            Pagination settings
        """
        return self.get('pagination', {})

    def get_per_page(self) -> int:
        """
        Get default items per page with validation

        Returns:
            Number of items per page (validated to be between 1 and max_per_page)
        """
        value = int(os.environ.get(
            f'{self._config_prefix}_PAGINATION_PER_PAGE',
            self.get('pagination.per_page', 20)
        ))
        # Validate range: must be at least 1 and at most max_per_page
        return max(1, min(value, self.get_max_per_page()))

    def get_max_per_page(self) -> int:
        """
        Get maximum items per page with validation

        Returns:
            Maximum number of items per page (at least 1)
        """
        value = int(os.environ.get(
            f'{self._config_prefix}_PAGINATION_MAX_PER_PAGE',
            self.get('pagination.max_per_page', 100)
        ))
        # Ensure at least 1
        return max(1, value)

    def get_search_config(self) -> Dict[str, Any]:
        """
        Get search configuration

        Returns:
            Search settings
        """
        return self.get('search', {})

    def get_search_min_length(self) -> int:
        """
        Get minimum search term length

        Returns:
            Minimum characters required for search
        """
        return int(os.environ.get(
            f'{self._config_prefix}_SEARCH_MIN_LENGTH',
            self.get('search.min_length', 2)
        ))

    def get_validation_config(self) -> Dict[str, Any]:
        """
        Get validation configuration

        Returns:
            Validation rules
        """
        return self.get('validation', {})

    def get_employee_code_config(self) -> Dict[str, Any]:
        """
        Get employee code validation configuration

        Returns:
            Employee code validation rules
        """
        return self.get('validation.employee_code', {})

    def get_employment_statuses(self) -> list:
        """
        Get valid employment statuses

        Returns:
            List of valid employment status values
        """
        env_statuses = os.environ.get(f'{self._config_prefix}_VALID_STATUSES')
        if env_statuses:
            return env_statuses.split(',')
        return self.get('employment.valid_statuses', ['active', 'inactive', 'on_leave', 'terminated'])

    def get_default_employment_status(self) -> str:
        """
        Get default employment status

        Returns:
            Default employment status
        """
        return os.environ.get(
            f'{self._config_prefix}_DEFAULT_STATUS',
            self.get('employment.default_status', 'active')
        )

    def get_management_levels(self) -> list:
        """
        Get position levels considered as management

        Returns:
            List of management position levels
        """
        env_levels = os.environ.get(f'{self._config_prefix}_MANAGEMENT_LEVELS')
        if env_levels:
            return [int(level.strip()) for level in env_levels.split(',')]
        return self.get('positions.management_levels', [1, 2, 3, 4, 5])

    def get_salary_level_range(self) -> tuple:
        """
        Get salary level range

        Returns:
            Tuple of (min_level, max_level)
        """
        min_level = int(os.environ.get(
            f'{self._config_prefix}_SALARY_MIN_LEVEL',
            self.get('validation.salary_level.min_value', 1)
        ))
        max_level = int(os.environ.get(
            f'{self._config_prefix}_SALARY_MAX_LEVEL',
            self.get('validation.salary_level.max_value', 10)
        ))
        return (min_level, max_level)

    def is_tenure_auto_calculated(self) -> bool:
        """
        Check if tenure should be automatically calculated

        Returns:
            True if tenure is auto-calculated
        """
        return os.environ.get(
            f'{self._config_prefix}_AUTO_CALCULATE_TENURE',
            str(self.get('employment.auto_calculate_tenure', True))
        ).lower() == 'true'

    def get_probation_period_months(self) -> int:
        """
        Get probation period in months

        Returns:
            Probation period in months
        """
        return int(os.environ.get(
            f'{self._config_prefix}_PROBATION_PERIOD_MONTHS',
            self.get('employment.probation_period_months', 3)
        ))

    def is_circular_reporting_allowed(self) -> bool:
        """
        Check if circular reporting is allowed

        Returns:
            True if circular reporting is allowed
        """
        return os.environ.get(
            f'{self._config_prefix}_ALLOW_CIRCULAR_REPORTING',
            str(self.get('organization.allow_circular_reporting', False))
        ).lower() == 'true'

    def get_display_config(self) -> Dict[str, Any]:
        """
        Get display configuration

        Returns:
            Display settings
        """
        return self.get('display', {})

    def should_show_inactive_employees(self) -> bool:
        """
        Check if inactive employees should be shown

        Returns:
            True if inactive employees should be shown
        """
        return os.environ.get(
            f'{self._config_prefix}_SHOW_INACTIVE',
            str(self.get('display.show_inactive_employees', True))
        ).lower() == 'true'

    def should_show_salary_information(self) -> bool:
        """
        Check if salary information should be shown

        Returns:
            True if salary information should be shown
        """
        return os.environ.get(
            f'{self._config_prefix}_SHOW_SALARY',
            str(self.get('display.show_salary_information', True))
        ).lower() == 'true'

    def get_export_config(self) -> Dict[str, Any]:
        """
        Get export configuration

        Returns:
            Export settings
        """
        return self.get('export', {})

    def is_export_enabled(self) -> bool:
        """
        Check if export functionality is enabled

        Returns:
            True if export is enabled
        """
        return os.environ.get(
            f'{self._config_prefix}_EXPORT_ENABLED',
            str(self.get('export.enabled', True))
        ).lower() == 'true'

    def get_security_config(self) -> Dict[str, Any]:
        """
        Get security configuration

        Returns:
            Security settings
        """
        return self.get('security', {})

    def should_audit_changes(self) -> bool:
        """
        Check if changes should be audited

        Returns:
            True if changes should be audited
        """
        return os.environ.get(
            f'{self._config_prefix}_AUDIT_CHANGES',
            str(self.get('security.audit_changes', True))
        ).lower() == 'true'

    def get_notification_config(self) -> Dict[str, Any]:
        """
        Get notification configuration

        Returns:
            Notification settings
        """
        return self.get('notifications', {})

    def are_birthday_reminders_enabled(self) -> bool:
        """
        Check if birthday reminders are enabled

        Returns:
            True if birthday reminders are enabled
        """
        return os.environ.get(
            f'{self._config_prefix}_BIRTHDAY_REMINDERS',
            str(self.get('notifications.birthday_reminders', True))
        ).lower() == 'true'

    def get_cache_timeout_minutes(self) -> int:
        """
        Get cache timeout in minutes

        Returns:
            Cache timeout in minutes
        """
        return int(os.environ.get(
            f'{self._config_prefix}_CACHE_TIMEOUT',
            self.get('performance.cache_timeout_minutes', 15)
        ))

    def validate_employee_code(self, code: str) -> tuple:
        """
        Validate employee code against configuration rules

        Args:
            code: Employee code to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not code:
            return False, "従業員コードは必須です"

        config = self.get_employee_code_config()

        # Length validation
        min_length = config.get('min_length', 3)
        max_length = config.get('max_length', 20)

        if len(code) < min_length:
            return False, f"従業員コードは{min_length}文字以上で入力してください"

        if len(code) > max_length:
            return False, f"従業員コードは{max_length}文字以下で入力してください"

        # Pattern validation
        import re
        pattern = config.get('pattern', r'^[A-Za-z0-9\-_]+$')
        if not re.match(pattern, code):
            return False, "従業員コードは英数字、ハイフン、アンダースコアのみ使用可能です"

        return True, ""

    def get_salary_range_for_level(self, level: int, position_min: Optional[int] = None,
                                 position_max: Optional[int] = None) -> tuple:
        """
        Calculate salary range for given level

        Args:
            level: Salary level (1-10)
            position_min: Position minimum salary (optional)
            position_max: Position maximum salary (optional)

        Returns:
            Tuple of (min_salary, max_salary) in thousands
        """
        if not position_min:
            position_min = 200  # Default minimum
        if not position_max:
            position_max = 800  # Default maximum

        multiplier = 1 + (level - 1) * self.get('positions.salary_multiplier_per_level', 0.1)

        min_salary = int(position_min * multiplier)
        max_salary = int(position_max * multiplier)

        return (min_salary, max_salary)

    def format_salary_range(self, min_salary: int, max_salary: int) -> str:
        """
        Format salary range for display

        Args:
            min_salary: Minimum salary in thousands
            max_salary: Maximum salary in thousands

        Returns:
            Formatted salary range string
        """
        if min_salary and max_salary:
            return f"{min_salary}万円 - {max_salary}万円"
        elif min_salary:
            return f"{min_salary}万円以上"
        elif max_salary:
            return f"{max_salary}万円以下"
        else:
            return "未設定"

    def get_age_from_date(self, birth_date) -> Optional[int]:
        """
        Calculate age from birth date

        Args:
            birth_date: Birth date

        Returns:
            Age in years or None
        """
        if not birth_date:
            return None

        from datetime import date
        today = date.today()
        age = today.year - birth_date.year

        # Adjust if birthday hasn't occurred this year
        if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
            age -= 1

        return age

    def init_app_instance(self, app):
        """
        Initialize this config instance with Flask app

        Args:
            app: Flask application instance
        """
        self.app = app

    @classmethod
    def init_app(cls, app):
        """
        Initialize EmployeeConfig with Flask app

        Args:
            app: Flask application instance
        """
        if not hasattr(app, 'extensions'):
            app.extensions = {}

        # Create instance without passing app to avoid recursion
        config_instance = cls()
        config_instance.init_app_instance(app)
        app.extensions['employee_config'] = config_instance

        # Register template functions
        @app.template_global()
        def employee_config():
            return app.extensions['employee_config']

        return app.extensions['employee_config']