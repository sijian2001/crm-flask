import pytest
from datetime import datetime
from models import Customer, db
from services.customer_service import CustomerService
from sqlalchemy.exc import IntegrityError


class TestCustomerService:
    """Customer service layer tests"""

    def test_get_customers_with_pagination_no_search(self, app):
        """Test getting paginated customers without search"""
        with app.app_context():
            # Create test customers
            customers = [
                Customer(first_name='太郎', last_name='田中', email=f'tanaka{i}@example.com')
                for i in range(15)
            ]
            db.session.add_all(customers)
            db.session.commit()

            # Get first page
            result = CustomerService.get_customers_with_pagination(page=1, per_page=10)

            assert result.total == 15
            assert len(result.items) == 10
            assert result.pages == 2
            assert result.has_next is True

            # Get second page
            result = CustomerService.get_customers_with_pagination(page=2, per_page=10)

            assert len(result.items) == 5
            assert result.has_prev is True

    def test_get_customers_with_pagination_with_search(self, app):
        """Test getting paginated customers with search"""
        with app.app_context():
            customers = [
                Customer(first_name='太郎', last_name='田中', email='tanaka@example.com', company='株式会社A'),
                Customer(first_name='花子', last_name='佐藤', email='sato@example.com', company='株式会社B'),
                Customer(first_name='次郎', last_name='鈴木', email='suzuki@example.com', company='株式会社田中')
            ]
            db.session.add_all(customers)
            db.session.commit()

            # Search by first name
            result = CustomerService.get_customers_with_pagination(search='太郎')
            assert len(result.items) == 1
            assert result.items[0].first_name == '太郎'

            # Search by company
            result = CustomerService.get_customers_with_pagination(search='田中')
            assert len(result.items) == 2  # 田中さんと株式会社田中

    def test_get_customers_pagination_excludes_inactive(self, app):
        """Test pagination excludes inactive customers"""
        with app.app_context():
            active_customer = Customer(first_name='太郎', last_name='田中', email='active@example.com')
            inactive_customer = Customer(first_name='花子', last_name='佐藤', email='inactive@example.com')
            inactive_customer.deactivate()

            db.session.add_all([active_customer, inactive_customer])
            db.session.commit()

            result = CustomerService.get_customers_with_pagination()
            assert len(result.items) == 1
            assert result.items[0].email == 'active@example.com'

    def test_get_customer_by_id_exists(self, app):
        """Test getting customer by ID when exists"""
        with app.app_context():
            customer = Customer(first_name='太郎', last_name='田中', email='test@example.com')
            db.session.add(customer)
            db.session.commit()
            customer_id = customer.id

            result = CustomerService.get_customer_by_id(customer_id)
            assert result is not None
            assert result.email == 'test@example.com'

    def test_get_customer_by_id_not_exists(self, app):
        """Test getting customer by ID when does not exist"""
        with app.app_context():
            result = CustomerService.get_customer_by_id(999999)
            assert result is None

    def test_create_customer_success(self, app):
        """Test successful customer creation"""
        with app.app_context():
            success, customer, error = CustomerService.create_customer(
                first_name='太郎',
                last_name='田中',
                email='create@example.com',
                phone='090-1234-5678',
                company='株式会社テスト'
            )

            assert success is True
            assert customer is not None
            assert error is None
            assert customer.full_name == '田中 太郎'
            assert customer.phone == '090-1234-5678'

    def test_create_customer_duplicate_email(self, app):
        """Test customer creation with duplicate email"""
        with app.app_context():
            # Create first customer
            existing_customer = Customer(first_name='既存', last_name='顧客', email='duplicate@example.com')
            db.session.add(existing_customer)
            db.session.commit()

            # Try to create duplicate
            success, customer, error = CustomerService.create_customer(
                first_name='新規',
                last_name='顧客',
                email='duplicate@example.com'
            )

            assert success is False
            assert customer is None
            assert 'メールアドレスが重複しています' in error

    def test_update_customer_success(self, app):
        """Test successful customer update"""
        with app.app_context():
            customer = Customer(first_name='太郎', last_name='田中', email='update@example.com')
            db.session.add(customer)
            db.session.commit()

            success, error = CustomerService.update_customer(
                customer=customer,
                first_name='次郎',
                last_name='田中',
                email='update@example.com',
                company='更新株式会社'
            )

            assert success is True
            assert error is None
            assert customer.first_name == '次郎'
            assert customer.company == '更新株式会社'

    def test_update_customer_inactive(self, app):
        """Test updating inactive customer"""
        with app.app_context():
            customer = Customer(first_name='太郎', last_name='田中', email='inactive@example.com')
            customer.deactivate()
            db.session.add(customer)
            db.session.commit()

            success, error = CustomerService.update_customer(
                customer=customer,
                first_name='次郎',
                last_name='田中',
                email='inactive@example.com'
            )

            assert success is False
            assert '無効化された顧客は編集できません' in error

    def test_update_customer_duplicate_email(self, app):
        """Test updating customer with duplicate email"""
        with app.app_context():
            customer1 = Customer(first_name='顧客1', last_name='テスト', email='customer1@example.com')
            customer2 = Customer(first_name='顧客2', last_name='テスト', email='customer2@example.com')
            db.session.add_all([customer1, customer2])
            db.session.commit()

            success, error = CustomerService.update_customer(
                customer=customer1,
                first_name='顧客1',
                last_name='テスト',
                email='customer2@example.com'  # Duplicate email
            )

            assert success is False
            assert 'メールアドレスが重複しています' in error

    def test_deactivate_customer_success(self, app):
        """Test successful customer deactivation"""
        with app.app_context():
            customer = Customer(first_name='太郎', last_name='田中', email='deactivate@example.com')
            db.session.add(customer)
            db.session.commit()

            success, error = CustomerService.deactivate_customer(customer)

            assert success is True
            assert error is None
            assert customer.is_active is False

    def test_deactivate_customer_already_inactive(self, app):
        """Test deactivating already inactive customer"""
        with app.app_context():
            customer = Customer(first_name='太郎', last_name='田中', email='already_inactive@example.com')
            customer.deactivate()
            db.session.add(customer)
            db.session.commit()

            success, error = CustomerService.deactivate_customer(customer)

            assert success is False
            assert '既に無効化されています' in error

    def test_activate_customer_success(self, app):
        """Test successful customer activation"""
        with app.app_context():
            customer = Customer(first_name='太郎', last_name='田中', email='activate@example.com')
            customer.deactivate()
            db.session.add(customer)
            db.session.commit()

            success, error = CustomerService.activate_customer(customer)

            assert success is True
            assert error is None
            assert customer.is_active is True

    def test_activate_customer_already_active(self, app):
        """Test activating already active customer"""
        with app.app_context():
            customer = Customer(first_name='太郎', last_name='田中', email='already_active@example.com')
            db.session.add(customer)
            db.session.commit()

            success, error = CustomerService.activate_customer(customer)

            assert success is False
            assert '既に有効化されています' in error

    def test_validate_customer_access_active(self, app):
        """Test validating access to active customer"""
        with app.app_context():
            customer = Customer(first_name='太郎', last_name='田中', email='active@example.com')
            db.session.add(customer)
            db.session.commit()

            can_access, warning = CustomerService.validate_customer_access(customer)

            assert can_access is True
            assert warning is None

    def test_validate_customer_access_inactive(self, app):
        """Test validating access to inactive customer"""
        with app.app_context():
            customer = Customer(first_name='太郎', last_name='田中', email='inactive@example.com')
            customer.deactivate()
            db.session.add(customer)
            db.session.commit()

            can_access, warning = CustomerService.validate_customer_access(customer)

            assert can_access is True
            assert '無効化されています' in warning