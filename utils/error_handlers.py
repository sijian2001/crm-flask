"""
Common error handling utilities for customer and product operations
"""
from typing import Optional, Tuple
from flask import flash
from flask_login import current_user
import logging

logger = logging.getLogger('error_handlers')


def handle_customer_operation_success(
    operation: str,
    customer_name: str,
    message_template: str = None
) -> None:
    """
    Handle successful customer operations with logging and user feedback

    Args:
        operation: Operation type (created, updated, deactivated, activated)
        customer_name: Full name of the customer
        message_template: Custom message template (optional)
    """
    # Log the operation
    logger.info(f'Customer {customer_name} {operation} by user {current_user.username}')

    # Default messages for different operations
    default_messages = {
        'created': f'顧客「{customer_name}」を登録しました。',
        'updated': f'顧客「{customer_name}」の情報を更新しました。',
        'deactivated': f'顧客「{customer_name}」を無効化しました。',
        'activated': f'顧客「{customer_name}」を有効化しました。'
    }

    # Use custom message or default
    message = message_template if message_template else default_messages.get(operation, f'顧客「{customer_name}」の操作が完了しました。')

    # Flash success message
    flash_category = 'success' if operation in ['created', 'updated', 'activated'] else 'info'
    flash(message, flash_category)


def handle_product_operation_success(
    operation: str,
    product_name: str,
    message_template: str = None
) -> None:
    """
    Handle successful product operations with logging and user feedback

    Args:
        operation: Operation type (created, updated, deactivated, activated, stock_updated)
        product_name: Name of the product
        message_template: Custom message template (optional)
    """
    # Log the operation
    logger.info(f'Product {product_name} {operation} by user {current_user.username}')

    # Default messages for different operations
    default_messages = {
        'created': f'製品「{product_name}」を登録しました。',
        'updated': f'製品「{product_name}」の情報を更新しました。',
        'deactivated': f'製品「{product_name}」を無効化しました。',
        'activated': f'製品「{product_name}」を有効化しました。',
        'stock_updated': f'製品「{product_name}」の在庫を更新しました。'
    }

    # Use custom message or default
    message = message_template if message_template else default_messages.get(operation, f'製品「{product_name}」の操作が完了しました。')

    # Flash success message
    flash_category = 'success' if operation in ['created', 'updated', 'activated', 'stock_updated'] else 'info'
    flash(message, flash_category)


def handle_category_operation_success(
    operation: str,
    category_name: str,
    message_template: str = None
) -> None:
    """
    Handle successful category operations with logging and user feedback

    Args:
        operation: Operation type (created, updated, deactivated)
        category_name: Name of the category
        message_template: Custom message template (optional)
    """
    # Log the operation
    logger.info(f'Category {category_name} {operation} by user {current_user.username}')

    # Default messages for different operations
    default_messages = {
        'created': f'カテゴリ「{category_name}」を登録しました。',
        'updated': f'カテゴリ「{category_name}」の情報を更新しました。',
        'deactivated': f'カテゴリ「{category_name}」を無効化しました。'
    }

    # Use custom message or default
    message = message_template if message_template else default_messages.get(operation, f'カテゴリ「{category_name}」の操作が完了しました。')

    # Flash success message
    flash_category = 'success' if operation in ['created', 'updated'] else 'info'
    flash(message, flash_category)


def handle_customer_operation_error(
    operation: str,
    error_message: str,
    customer_name: Optional[str] = None
) -> None:
    """
    Handle customer operation errors with logging and user feedback

    Args:
        operation: Operation type (creation, update, deletion, etc.)
        error_message: Specific error message from service layer
        customer_name: Customer name for logging (optional)
    """
    # Log the error
    if customer_name:
        logger.error(f'Customer {operation} failed for {customer_name}: {error_message} by user {current_user.username}')
    else:
        logger.error(f'Customer {operation} failed: {error_message} by user {current_user.username}')

    # Determine flash category based on error type
    flash_category = 'warning' if '既に' in error_message else 'error'

    # Map operation to user-friendly prefix
    operation_prefixes = {
        'creation': '顧客登録中に',
        'update': '顧客情報更新中に',
        'deletion': '顧客削除中に',
        'activation': '顧客有効化中に',
        'deactivation': '顧客無効化中に'
    }

    # Build user message
    prefix = operation_prefixes.get(operation, '操作中に')
    user_message = f'{prefix}エラーが発生しました。{error_message}'

    flash(user_message, flash_category)


def log_customer_access(customer_name: str, operation: str = 'viewed') -> None:
    """
    Log customer access for audit purposes

    Args:
        customer_name: Full name of the customer
        operation: Type of access (viewed, accessed, etc.)
    """
    logger.info(f'Customer {customer_name} {operation} by user {current_user.username}')


class CustomerOperationResult:
    """
    Standardized result object for customer operations
    """

    def __init__(self, success: bool, customer=None, error_message: Optional[str] = None):
        self.success = success
        self.customer = customer
        self.error_message = error_message

    def handle_result(self, operation: str) -> None:
        """
        Handle the operation result with appropriate logging and user feedback

        Args:
            operation: Operation type for proper messaging
        """
        if self.success and self.customer:
            handle_customer_operation_success(operation, self.customer.full_name)
        elif not self.success and self.error_message:
            customer_name = self.customer.full_name if self.customer else None
            handle_customer_operation_error(operation, self.error_message, customer_name)


def validate_customer_operation(customer, operation: str) -> Tuple[bool, Optional[str]]:
    """
    Common validation for customer operations

    Args:
        customer: Customer object
        operation: Operation type (edit, delete, etc.)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not customer:
        return False, '指定された顧客が見つかりません。'

    if operation in ['edit', 'delete'] and not customer.is_active:
        operation_names = {
            'edit': '編集',
            'delete': '削除'
        }
        op_name = operation_names.get(operation, '操作')
        return False, f'無効化された顧客は{op_name}できません。'

    return True, None


def validate_product_operation(product, operation: str) -> Tuple[bool, Optional[str]]:
    """
    Common validation for product operations

    Args:
        product: Product object
        operation: Operation type (edit, delete, stock_update, etc.)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not product:
        return False, '指定された製品が見つかりません。'

    if operation in ['edit', 'delete', 'stock_update'] and not product.is_active:
        operation_names = {
            'edit': '編集',
            'delete': '削除',
            'stock_update': '在庫更新'
        }
        op_name = operation_names.get(operation, '操作')
        return False, f'無効化された製品は{op_name}できません。'

    return True, None


def validate_category_operation(category, operation: str) -> Tuple[bool, Optional[str]]:
    """
    Common validation for category operations

    Args:
        category: Category object
        operation: Operation type (edit, delete, etc.)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not category:
        return False, '指定されたカテゴリが見つかりません。'

    if operation in ['edit', 'delete'] and not category.is_active:
        operation_names = {
            'edit': '編集',
            'delete': '削除'
        }
        op_name = operation_names.get(operation, '操作')
        return False, f'無効化されたカテゴリは{op_name}できません。'

    # カテゴリ削除時の追加チェック
    if operation == 'delete' and hasattr(category, 'product_count') and category.product_count > 0:
        return False, 'アクティブな製品が存在するカテゴリは削除できません。'

    return True, None