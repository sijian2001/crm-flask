import pytest
from unittest.mock import patch, MagicMock
from utils.error_handlers import (
    handle_customer_operation_success,
    handle_customer_operation_error,
    log_customer_access,
    CustomerOperationResult,
    validate_customer_operation
)
from models import Customer


class TestErrorHandlers:
    """Test error handling utilities"""

    @patch('utils.error_handlers.flash')
    @patch('utils.error_handlers.logger')
    @patch('utils.error_handlers.current_user')
    def test_handle_customer_operation_success_created(self, mock_user, mock_logger, mock_flash):
        """Test successful customer creation handling"""
        mock_user.username = 'testuser'

        handle_customer_operation_success('created', '田中 太郎')

        mock_logger.info.assert_called_once_with('Customer 田中 太郎 created by user testuser')
        mock_flash.assert_called_once_with('顧客「田中 太郎」を登録しました。', 'success')

    @patch('utils.error_handlers.flash')
    @patch('utils.error_handlers.logger')
    @patch('utils.error_handlers.current_user')
    def test_handle_customer_operation_success_updated(self, mock_user, mock_logger, mock_flash):
        """Test successful customer update handling"""
        mock_user.username = 'testuser'

        handle_customer_operation_success('updated', '田中 太郎')

        mock_logger.info.assert_called_once_with('Customer 田中 太郎 updated by user testuser')
        mock_flash.assert_called_once_with('顧客「田中 太郎」の情報を更新しました。', 'success')

    @patch('utils.error_handlers.flash')
    @patch('utils.error_handlers.logger')
    @patch('utils.error_handlers.current_user')
    def test_handle_customer_operation_success_deactivated(self, mock_user, mock_logger, mock_flash):
        """Test successful customer deactivation handling"""
        mock_user.username = 'testuser'

        handle_customer_operation_success('deactivated', '田中 太郎')

        mock_logger.info.assert_called_once_with('Customer 田中 太郎 deactivated by user testuser')
        mock_flash.assert_called_once_with('顧客「田中 太郎」を無効化しました。', 'info')

    @patch('utils.error_handlers.flash')
    @patch('utils.error_handlers.logger')
    @patch('utils.error_handlers.current_user')
    def test_handle_customer_operation_success_with_custom_message(self, mock_user, mock_logger, mock_flash):
        """Test successful operation with custom message"""
        mock_user.username = 'testuser'

        custom_message = 'カスタムメッセージです。'
        handle_customer_operation_success('created', '田中 太郎', custom_message)

        mock_flash.assert_called_once_with(custom_message, 'success')

    @patch('utils.error_handlers.flash')
    @patch('utils.error_handlers.logger')
    @patch('utils.error_handlers.current_user')
    def test_handle_customer_operation_error_with_customer_name(self, mock_user, mock_logger, mock_flash):
        """Test error handling with customer name"""
        mock_user.username = 'testuser'

        handle_customer_operation_error('creation', 'メールアドレスが重複しています。', '田中 太郎')

        mock_logger.error.assert_called_once_with(
            'Customer creation failed for 田中 太郎: メールアドレスが重複しています。 by user testuser'
        )
        mock_flash.assert_called_once_with('顧客登録中にエラーが発生しました。メールアドレスが重複しています。', 'error')

    @patch('utils.error_handlers.flash')
    @patch('utils.error_handlers.logger')
    @patch('utils.error_handlers.current_user')
    def test_handle_customer_operation_error_without_customer_name(self, mock_user, mock_logger, mock_flash):
        """Test error handling without customer name"""
        mock_user.username = 'testuser'

        handle_customer_operation_error('update', 'システムエラーが発生しました。')

        mock_logger.error.assert_called_once_with(
            'Customer update failed: システムエラーが発生しました。 by user testuser'
        )
        mock_flash.assert_called_once_with('顧客情報更新中にエラーが発生しました。システムエラーが発生しました。', 'error')

    @patch('utils.error_handlers.flash')
    @patch('utils.error_handlers.logger')
    @patch('utils.error_handlers.current_user')
    def test_handle_customer_operation_error_warning_category(self, mock_user, mock_logger, mock_flash):
        """Test error handling with warning category for '既に' messages"""
        mock_user.username = 'testuser'

        handle_customer_operation_error('activation', '指定された顧客は既に有効化されています。', '田中 太郎')

        mock_flash.assert_called_once_with(
            '顧客有効化中にエラーが発生しました。指定された顧客は既に有効化されています。',
            'warning'
        )

    @patch('utils.error_handlers.logger')
    @patch('utils.error_handlers.current_user')
    def test_log_customer_access(self, mock_user, mock_logger):
        """Test customer access logging"""
        mock_user.username = 'testuser'

        log_customer_access('田中 太郎', 'viewed')

        mock_logger.info.assert_called_once_with('Customer 田中 太郎 viewed by user testuser')

    @patch('utils.error_handlers.logger')
    @patch('utils.error_handlers.current_user')
    def test_log_customer_access_default_operation(self, mock_user, mock_logger):
        """Test customer access logging with default operation"""
        mock_user.username = 'testuser'

        log_customer_access('田中 太郎')

        mock_logger.info.assert_called_once_with('Customer 田中 太郎 viewed by user testuser')


class TestCustomerOperationResult:
    """Test CustomerOperationResult class"""

    def test_customer_operation_result_success(self):
        """Test successful operation result"""
        customer = MagicMock()
        customer.full_name = '田中 太郎'

        result = CustomerOperationResult(success=True, customer=customer)

        assert result.success is True
        assert result.customer == customer
        assert result.error_message is None

    def test_customer_operation_result_failure(self):
        """Test failed operation result"""
        result = CustomerOperationResult(success=False, error_message='エラーが発生しました')

        assert result.success is False
        assert result.customer is None
        assert result.error_message == 'エラーが発生しました'

    @patch('utils.error_handlers.handle_customer_operation_success')
    def test_handle_result_success(self, mock_success_handler):
        """Test handling successful result"""
        customer = MagicMock()
        customer.full_name = '田中 太郎'

        result = CustomerOperationResult(success=True, customer=customer)
        result.handle_result('created')

        mock_success_handler.assert_called_once_with('created', '田中 太郎')

    @patch('utils.error_handlers.handle_customer_operation_error')
    def test_handle_result_failure(self, mock_error_handler):
        """Test handling failed result"""
        customer = MagicMock()
        customer.full_name = '田中 太郎'

        result = CustomerOperationResult(success=False, customer=customer, error_message='エラーです')
        result.handle_result('update')

        mock_error_handler.assert_called_once_with('update', 'エラーです', '田中 太郎')


class TestValidateCustomerOperation:
    """Test validate_customer_operation function"""

    def test_validate_customer_operation_customer_not_found(self):
        """Test validation when customer is None"""
        is_valid, error_message = validate_customer_operation(None, 'edit')

        assert is_valid is False
        assert error_message == '指定された顧客が見つかりません。'

    def test_validate_customer_operation_inactive_customer_edit(self, app):
        """Test validation for editing inactive customer"""
        with app.app_context():
            customer = Customer(first_name='太郎', last_name='田中', email='test@example.com')
            customer.deactivate()

            is_valid, error_message = validate_customer_operation(customer, 'edit')

            assert is_valid is False
            assert error_message == '無効化された顧客は編集できません。'

    def test_validate_customer_operation_inactive_customer_delete(self, app):
        """Test validation for deleting inactive customer"""
        with app.app_context():
            customer = Customer(first_name='太郎', last_name='田中', email='test@example.com')
            customer.deactivate()

            is_valid, error_message = validate_customer_operation(customer, 'delete')

            assert is_valid is False
            assert error_message == '無効化された顧客は削除できません。'

    def test_validate_customer_operation_active_customer(self, app):
        """Test validation for active customer"""
        with app.app_context():
            customer = Customer(first_name='太郎', last_name='田中', email='test@example.com')

            is_valid, error_message = validate_customer_operation(customer, 'edit')

            assert is_valid is True
            assert error_message is None

    def test_validate_customer_operation_unknown_operation_inactive(self, app):
        """Test validation for unknown operation on inactive customer"""
        with app.app_context():
            customer = Customer(first_name='太郎', last_name='田中', email='test@example.com')
            customer.deactivate()

            is_valid, error_message = validate_customer_operation(customer, 'unknown')

            assert is_valid is True  # Unknown operations are not restricted
            assert error_message is None

    def test_validate_customer_operation_unknown_operation_active(self, app):
        """Test validation for unknown operation on active customer"""
        with app.app_context():
            customer = Customer(first_name='太郎', last_name='田中', email='test@example.com')

            is_valid, error_message = validate_customer_operation(customer, 'unknown')

            assert is_valid is True
            assert error_message is None