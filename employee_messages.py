"""
Employee management messages for internationalization support

This module provides centralized message strings for employee management.
In the future, these can be integrated with Flask-Babel for full i18n support.
"""

# Validation messages
VALIDATION_MESSAGES = {
    'employee_code_required': '従業員コードは必須です',
    'employee_code_duplicate': '従業員コード \'{code}\' は既に使用されています',
    'employee_code_invalid': '従業員コードは英数字、ハイフン、アンダースコアのみ使用できます',
    'employee_code_length': '従業員コードは3文字以上20文字以内で入力してください',
    'email_required': 'メールアドレスは必須です',
    'email_duplicate': 'メールアドレス \'{email}\' は既に使用されています',
    'email_invalid': 'メールアドレスの形式が正しくありません',
    'name_required': '氏名は必須です',
    'hire_date_required': '入社日は必須です',
    'hire_date_future': '入社日は未来の日付にできません',
    'store_required': '店舗を選択してください',
    'position_required': '役職を選択してください',
    'salary_level_range': '給与レベルは1から10の間で指定してください',
    'circular_reference': '循環参照が発生します',
}

# Success messages
SUCCESS_MESSAGES = {
    'employee_created': '従業員 \'{name}\' を登録しました',
    'employee_updated': '従業員情報を更新しました',
    'employee_deleted': '従業員を削除しました',
    'transfer_success': '従業員を異動しました',
    'promotion_success': '従業員を昇進させました',
}

# Error messages
ERROR_MESSAGES = {
    'employee_not_found': '従業員が見つかりません',
    'store_not_found': '指定された店舗が見つかりません',
    'position_not_found': '指定された役職が見つかりません',
    'department_not_found': '指定された部署が見つかりません',
    'transfer_failed': '異動処理中にエラーが発生しました',
    'promotion_failed': '昇進処理中にエラーが発生しました',
    'delete_has_subordinates': '部下がいる従業員は削除できません',
    'invalid_input': '入力値エラー: {error}',
    'database_error': 'データベースエラーが発生しました',
}

# Info messages
INFO_MESSAGES = {
    'select_store': '異動先店舗を選択してください',
    'select_position': '昇進先役職を選択してください',
    'confirm_delete': '本当に削除しますか？',
    'has_subordinates_warning': 'この従業員には部下がいます',
}


def get_validation_message(key: str, **kwargs) -> str:
    """
    Get validation message with optional formatting

    Args:
        key: Message key
        **kwargs: Format parameters

    Returns:
        Formatted message string
    """
    message = VALIDATION_MESSAGES.get(key, key)
    return message.format(**kwargs) if kwargs else message


def get_success_message(key: str, **kwargs) -> str:
    """
    Get success message with optional formatting

    Args:
        key: Message key
        **kwargs: Format parameters

    Returns:
        Formatted message string
    """
    message = SUCCESS_MESSAGES.get(key, key)
    return message.format(**kwargs) if kwargs else message


def get_error_message(key: str, **kwargs) -> str:
    """
    Get error message with optional formatting

    Args:
        key: Message key
        **kwargs: Format parameters

    Returns:
        Formatted message string
    """
    message = ERROR_MESSAGES.get(key, key)
    return message.format(**kwargs) if kwargs else message


def get_info_message(key: str, **kwargs) -> str:
    """
    Get info message with optional formatting

    Args:
        key: Message key
        **kwargs: Format parameters

    Returns:
        Formatted message string
    """
    message = INFO_MESSAGES.get(key, key)
    return message.format(**kwargs) if kwargs else message


# English translations (for future i18n support)
ENGLISH_MESSAGES = {
    # Validation
    'employee_code_required': 'Employee code is required',
    'employee_code_duplicate': 'Employee code \'{code}\' is already in use',
    'employee_code_invalid': 'Employee code can only contain alphanumeric characters, hyphens, and underscores',
    'employee_code_length': 'Employee code must be between 3 and 20 characters',
    'email_required': 'Email address is required',
    'email_duplicate': 'Email address \'{email}\' is already in use',
    'email_invalid': 'Invalid email address format',
    'name_required': 'Name is required',
    'hire_date_required': 'Hire date is required',
    'hire_date_future': 'Hire date cannot be in the future',
    'store_required': 'Please select a store',
    'position_required': 'Please select a position',
    'salary_level_range': 'Salary level must be between 1 and 10',
    'circular_reference': 'Circular reference detected',

    # Success
    'employee_created': 'Employee \'{name}\' has been registered',
    'employee_updated': 'Employee information has been updated',
    'employee_deleted': 'Employee has been deleted',
    'transfer_success': 'Employee has been transferred',
    'promotion_success': 'Employee has been promoted',

    # Error
    'employee_not_found': 'Employee not found',
    'store_not_found': 'Store not found',
    'position_not_found': 'Position not found',
    'department_not_found': 'Department not found',
    'transfer_failed': 'Error occurred during transfer',
    'promotion_failed': 'Error occurred during promotion',
    'delete_has_subordinates': 'Cannot delete employee with subordinates',
    'invalid_input': 'Input error: {error}',
    'database_error': 'Database error occurred',

    # Info
    'select_store': 'Please select a transfer destination store',
    'select_position': 'Please select a promotion position',
    'confirm_delete': 'Are you sure you want to delete?',
    'has_subordinates_warning': 'This employee has subordinates',
}