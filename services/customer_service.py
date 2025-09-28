from typing import Optional, Tuple, List
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy.pagination import Pagination
from flask import current_app
from models import Customer, db
from customer_config import CustomerConfig
import logging

logger = logging.getLogger('customer_service')


class CustomerService:
    """Customer business logic service"""

    @staticmethod
    def get_customers_with_pagination(
        page: int = 1,
        per_page: Optional[int] = None,
        search: Optional[str] = None
    ) -> Pagination:
        """
        Get paginated list of active customers with optional search

        Args:
            page: Page number (default: 1)
            per_page: Items per page (uses config if None)
            search: Search term for filtering (optional)

        Returns:
            Pagination object containing customers
        """
        if per_page is None:
            per_page = CustomerConfig.get_items_per_page(current_app.config)
        query = Customer.query.filter_by(is_active=True)

        if search:
            search_query = f"%{search}%"
            search_fields = CustomerConfig.get_search_fields(current_app.config)

            # Build dynamic OR conditions based on configured search fields
            search_conditions = []
            for field in search_fields:
                if hasattr(Customer, field):
                    search_conditions.append(
                        getattr(Customer, field).ilike(search_query)
                    )

            if search_conditions:
                query = query.filter(or_(*search_conditions))

        return query.order_by(Customer.updated_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

    @staticmethod
    def get_customer_by_id(customer_id: int) -> Optional[Customer]:
        """
        Get customer by ID

        Args:
            customer_id: Customer ID

        Returns:
            Customer object or None if not found
        """
        return Customer.query.get(customer_id)

    @staticmethod
    def create_customer(
        first_name: str,
        last_name: str,
        email: str,
        phone: Optional[str] = None,
        company: Optional[str] = None,
        address: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Tuple[bool, Optional[Customer], Optional[str]]:
        """
        Create new customer

        Args:
            first_name: Customer first name
            last_name: Customer last name
            email: Customer email
            phone: Customer phone (optional)
            company: Customer company (optional)
            address: Customer address (optional)
            notes: Customer notes (optional)

        Returns:
            Tuple of (success: bool, customer: Customer|None, error_message: str|None)
        """
        try:
            customer = Customer(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                company=company,
                address=address,
                notes=notes
            )

            db.session.add(customer)
            db.session.commit()

            logger.info(f'New customer created: {customer.full_name}')
            return True, customer, None

        except IntegrityError:
            db.session.rollback()
            logger.error(f'Customer creation failed: email {email} already exists')
            return False, None, 'メールアドレスが重複しています。'
        except Exception as e:
            db.session.rollback()
            logger.error(f'Unexpected error during customer creation: {str(e)}')
            return False, None, '予期しないエラーが発生しました。'

    @staticmethod
    def update_customer(
        customer: Customer,
        first_name: str,
        last_name: str,
        email: str,
        phone: Optional[str] = None,
        company: Optional[str] = None,
        address: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Update existing customer

        Args:
            customer: Customer object to update
            first_name: Updated first name
            last_name: Updated last name
            email: Updated email
            phone: Updated phone (optional)
            company: Updated company (optional)
            address: Updated address (optional)
            notes: Updated notes (optional)

        Returns:
            Tuple of (success: bool, error_message: str|None)
        """
        if not customer.is_active:
            return False, '無効化された顧客は編集できません。'

        try:
            customer.update_info(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                company=company,
                address=address,
                notes=notes
            )

            db.session.commit()

            logger.info(f'Customer {customer.full_name} updated')
            return True, None

        except IntegrityError:
            db.session.rollback()
            logger.error(f'Customer update failed: email {email} already exists')
            return False, 'メールアドレスが重複しています。'
        except Exception as e:
            db.session.rollback()
            logger.error(f'Unexpected error during customer update: {str(e)}')
            return False, '予期しないエラーが発生しました。'

    @staticmethod
    def deactivate_customer(customer: Customer) -> Tuple[bool, Optional[str]]:
        """
        Deactivate customer (soft delete)

        Args:
            customer: Customer object to deactivate

        Returns:
            Tuple of (success: bool, error_message: str|None)
        """
        if not customer.is_active:
            return False, '指定された顧客は既に無効化されています。'

        try:
            customer.deactivate()
            db.session.commit()

            logger.info(f'Customer {customer.full_name} deactivated')
            return True, None

        except Exception as e:
            db.session.rollback()
            logger.error(f'Customer deactivation failed: {str(e)}')
            return False, '顧客無効化中にエラーが発生しました。'

    @staticmethod
    def activate_customer(customer: Customer) -> Tuple[bool, Optional[str]]:
        """
        Activate customer

        Args:
            customer: Customer object to activate

        Returns:
            Tuple of (success: bool, error_message: str|None)
        """
        if customer.is_active:
            return False, '指定された顧客は既に有効化されています。'

        try:
            customer.activate()
            db.session.commit()

            logger.info(f'Customer {customer.full_name} activated')
            return True, None

        except Exception as e:
            db.session.rollback()
            logger.error(f'Customer activation failed: {str(e)}')
            return False, '顧客有効化中にエラーが発生しました。'

    @staticmethod
    def validate_customer_access(customer: Customer) -> Tuple[bool, Optional[str]]:
        """
        Validate if customer can be accessed/viewed

        Args:
            customer: Customer object to validate

        Returns:
            Tuple of (can_access: bool, warning_message: str|None)
        """
        if not customer.is_active:
            return True, '指定された顧客は無効化されています。'
        return True, None