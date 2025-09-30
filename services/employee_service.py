"""
Employee service layer

This module provides business logic for employee management including CRUD operations,
organizational management, and HR analytics.
"""
from typing import Optional, Tuple, List, Dict, Any
from datetime import date, datetime
from collections import defaultdict

from sqlalchemy import or_, and_, desc, asc, func
from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy.orm import selectinload, joinedload

from models import db, Employee, Position, Department, Store


class EmployeeService:
    """
    Service class for employee-related business logic

    Handles all employee operations including CRUD, organizational management,
    HR analytics, and reporting with proper error handling and validation.
    """

    @staticmethod
    def get_employees_with_pagination(page: int = 1, per_page: Optional[int] = None,
                                    search: Optional[str] = None,
                                    store_id: Optional[int] = None,
                                    position_id: Optional[int] = None,
                                    department_id: Optional[int] = None,
                                    employment_status: Optional[str] = None,
                                    manager_id: Optional[int] = None,
                                    sort_by: str = 'full_name',
                                    sort_order: str = 'asc'):
        """
        Get employees with pagination, search, and filtering

        Args:
            page: Page number (1-based)
            per_page: Items per page
            search: Search term for name/code/email
            store_id: Filter by store
            position_id: Filter by position
            department_id: Filter by department
            employment_status: Filter by employment status
            manager_id: Filter by manager
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)

        Returns:
            Tuple of (pagination_object, total_count)
        """
        if per_page is None:
            per_page = 20

        # Build base query with eager loading to prevent N+1 problems
        query = Employee.query.options(
            joinedload(Employee.store),
            joinedload(Employee.position),
            joinedload(Employee.department),
            joinedload(Employee.manager)
        )

        # Apply search filter
        if search:
            search_pattern = f'%{search}%'
            query = query.filter(
                or_(
                    Employee.first_name.ilike(search_pattern),
                    Employee.last_name.ilike(search_pattern),
                    Employee.employee_code.ilike(search_pattern),
                    Employee.email.ilike(search_pattern)
                )
            )

        # Apply filters
        if store_id:
            query = query.filter(Employee.store_id == store_id)
        if position_id:
            query = query.filter(Employee.position_id == position_id)
        if department_id:
            query = query.filter(Employee.department_id == department_id)
        if employment_status:
            query = query.filter(Employee.employment_status == employment_status)
        if manager_id:
            query = query.filter(Employee.manager_id == manager_id)

        # Apply sorting
        if sort_by == 'full_name':
            sort_column = Employee.last_name
        else:
            sort_column = getattr(Employee, sort_by, Employee.last_name)

        if sort_order.lower() == 'desc':
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        # Get total count and paginated results
        total_count = query.count()
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return pagination, total_count

    @staticmethod
    def create_employee(employee_code: str, first_name: str, last_name: str,
                       email: str, hire_date: str, store_id: int, position_id: int,
                       **kwargs) -> Tuple[bool, Optional[Employee], str]:
        """
        Create new employee

        Args:
            employee_code: Unique employee code
            first_name: Employee first name
            last_name: Employee last name
            email: Employee email
            hire_date: Date of hiring
            store_id: Store ID
            position_id: Position ID
            **kwargs: Additional employee attributes

        Returns:
            Tuple of (success, employee_object, message)
        """
        try:
            # Validate required relationships
            store = Store.query.get(store_id)
            if not store:
                return False, None, "指定された店舗が見つかりません"

            position = Position.query.get(position_id)
            if not position or not position.is_active:
                return False, None, "指定された役職が見つかりません"

            # Check for duplicate employee code
            existing = Employee.query.filter_by(employee_code=employee_code).first()
            if existing:
                return False, None, f"従業員コード '{employee_code}' は既に使用されています"

            # Check for duplicate email
            if email:
                existing_email = Employee.query.filter_by(email=email).first()
                if existing_email:
                    return False, None, f"メールアドレス '{email}' は既に使用されています"

            # Validate department if provided
            department_id = kwargs.get('department_id')
            if department_id:
                department = Department.query.get(department_id)
                if not department or not department.is_active:
                    return False, None, "指定された部署が見つかりません"

            # Validate manager if provided
            manager_id = kwargs.get('manager_id')
            if manager_id:
                manager = Employee.query.get(manager_id)
                if not manager or not manager.is_active:
                    return False, None, "指定された上司が見つかりません"

            # Create employee
            employee = Employee(
                employee_code=employee_code,
                first_name=first_name,
                last_name=last_name,
                email=email,
                hire_date=hire_date,
                store_id=store_id,
                position_id=position_id,
                **kwargs
            )

            db.session.add(employee)
            db.session.commit()

            return True, employee, f"従業員 '{employee.full_name}' を正常に登録しました"

        except IntegrityError as e:
            db.session.rollback()
            return False, None, f"データベース整合性エラー: {str(e)}"
        except Exception as e:
            db.session.rollback()
            return False, None, f"従業員登録エラー: {str(e)}"

    @staticmethod
    def update_employee(employee_id: int, **kwargs) -> Tuple[bool, Optional[Employee], str]:
        """
        Update employee information

        Args:
            employee_id: Employee ID to update
            **kwargs: Fields to update

        Returns:
            Tuple of (success, employee_object, message)
        """
        try:
            employee = Employee.query.get(employee_id)
            if not employee:
                return False, None, "従業員が見つかりません"

            # Validate relationships if being updated
            if 'store_id' in kwargs:
                store = Store.query.get(kwargs['store_id'])
                if not store:
                    return False, None, "指定された店舗が見つかりません"

            if 'position_id' in kwargs:
                position = Position.query.get(kwargs['position_id'])
                if not position or not position.is_active:
                    return False, None, "指定された役職が見つかりません"

            if 'department_id' in kwargs and kwargs['department_id']:
                department = Department.query.get(kwargs['department_id'])
                if not department or not department.is_active:
                    return False, None, "指定された部署が見つかりません"

            if 'manager_id' in kwargs and kwargs['manager_id']:
                manager = Employee.query.get(kwargs['manager_id'])
                if not manager or not manager.is_active:
                    return False, None, "指定された上司が見つかりません"

                # Check for circular management reference
                if not employee.can_be_manager_of(manager):
                    return False, None, "循環参照となる上司の設定はできません"

            # Check for duplicate employee code if being changed
            if 'employee_code' in kwargs and kwargs['employee_code'] != employee.employee_code:
                existing = Employee.query.filter_by(employee_code=kwargs['employee_code']).first()
                if existing:
                    return False, None, f"従業員コード '{kwargs['employee_code']}' は既に使用されています"

            # Check for duplicate email if being changed
            if 'email' in kwargs and kwargs['email'] != employee.email:
                existing_email = Employee.query.filter_by(email=kwargs['email']).first()
                if existing_email:
                    return False, None, f"メールアドレス '{kwargs['email']}' は既に使用されています"

            # Update fields
            for key, value in kwargs.items():
                if hasattr(employee, key):
                    setattr(employee, key, value)

            employee.updated_at = datetime.utcnow()
            db.session.commit()

            return True, employee, f"従業員 '{employee.full_name}' の情報を正常に更新しました"

        except IntegrityError as e:
            db.session.rollback()
            return False, None, f"データベース整合性エラー: {str(e)}"
        except Exception as e:
            db.session.rollback()
            return False, None, f"従業員更新エラー: {str(e)}"

    @staticmethod
    def delete_employee(employee_id: int) -> Tuple[bool, str]:
        """
        Delete employee (soft delete by setting inactive status)

        Args:
            employee_id: Employee ID to delete

        Returns:
            Tuple of (success, message)
        """
        try:
            employee = Employee.query.get(employee_id)
            if not employee:
                return False, "従業員が見つかりません"

            # Check if employee has subordinates
            if employee.subordinate_count > 0:
                return False, f"部下が存在する従業員は削除できません。まず部下の上司を変更してください。"

            # Soft delete by setting status to terminated
            employee.employment_status = 'terminated'
            employee.updated_at = datetime.utcnow()
            db.session.commit()

            return True, f"従業員 '{employee.full_name}' を正常に削除しました"

        except Exception as e:
            db.session.rollback()
            return False, f"従業員削除エラー: {str(e)}"

    @staticmethod
    def get_employee_by_id(employee_id: int) -> Optional[Employee]:
        """
        Get employee by ID with eager loading

        Args:
            employee_id: Employee ID

        Returns:
            Employee object or None
        """
        return Employee.query.options(
            joinedload(Employee.store),
            joinedload(Employee.position),
            joinedload(Employee.department),
            joinedload(Employee.manager),
            selectinload(Employee.subordinates)
        ).get(employee_id)

    @staticmethod
    def get_employee_by_code(employee_code: str) -> Optional[Employee]:
        """
        Get employee by employee code

        Args:
            employee_code: Employee code

        Returns:
            Employee object or None
        """
        return Employee.query.filter_by(employee_code=employee_code).first()

    @staticmethod
    def search_employees(search_term: str, limit: int = 50) -> List[Employee]:
        """
        Search employees by name, code, or email

        Args:
            search_term: Search term
            limit: Maximum results to return

        Returns:
            List of matching employees
        """
        if not search_term or len(search_term) < 2:
            return []

        return Employee.search(search_term).filter(
            Employee.employment_status == 'active'
        ).limit(limit).all()

    @staticmethod
    def get_employees_by_store(store_id: int, active_only: bool = True) -> List[Employee]:
        """
        Get employees by store

        Args:
            store_id: Store ID
            active_only: Whether to include only active employees

        Returns:
            List of employees
        """
        query = Employee.get_by_store(store_id).options(
            joinedload(Employee.store),
            joinedload(Employee.position),
            joinedload(Employee.department),
            joinedload(Employee.manager)
        )
        if active_only:
            query = query.filter(Employee.employment_status == 'active')
        return query.order_by(Employee.last_name, Employee.first_name).all()

    @staticmethod
    def get_employees_by_manager(manager_id: int) -> List[Employee]:
        """
        Get direct subordinates of a manager

        Args:
            manager_id: Manager employee ID

        Returns:
            List of subordinate employees
        """
        return Employee.query.options(
            joinedload(Employee.store),
            joinedload(Employee.position),
            joinedload(Employee.department),
            joinedload(Employee.manager)
        ).filter(
            Employee.manager_id == manager_id,
            Employee.employment_status == 'active'
        ).order_by(Employee.last_name, Employee.first_name).all()

    @staticmethod
    def get_organizational_chart(store_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get organizational chart structure

        Args:
            store_id: Optional store ID to filter by

        Returns:
            List of organizational nodes
        """
        query = Employee.query.filter(Employee.employment_status == 'active')
        if store_id:
            query = query.filter(Employee.store_id == store_id)

        employees = query.options(
            selectinload(Employee.position),
            selectinload(Employee.subordinates)
        ).all()

        # Build organizational tree
        chart = []
        for employee in employees:
            if not employee.manager_id:  # Top level employees
                node = EmployeeService._build_org_node(employee)
                chart.append(node)

        return chart

    @staticmethod
    def _build_org_node(employee: Employee) -> Dict[str, Any]:
        """
        Build organizational chart node recursively

        Args:
            employee: Employee to build node for

        Returns:
            Organizational node dictionary
        """
        node = {
            'id': employee.id,
            'name': employee.full_name,
            'employee_code': employee.employee_code,
            'position': employee.position.name if employee.position else None,
            'department': employee.department.name if employee.department else None,
            'subordinates': []
        }

        for subordinate in employee.subordinates:
            if subordinate.employment_status == 'active':
                sub_node = EmployeeService._build_org_node(subordinate)
                node['subordinates'].append(sub_node)

        return node

    @staticmethod
    def get_statistics() -> Dict[str, Any]:
        """
        Get comprehensive employee statistics

        Returns:
            Dictionary containing various statistics
        """
        try:
            # Basic counts
            total_employees = Employee.query.count()
            active_employees = Employee.query.filter_by(employment_status='active').count()
            inactive_employees = total_employees - active_employees

            # Status breakdown
            status_counts = dict(
                db.session.query(Employee.employment_status, func.count(Employee.id))
                .group_by(Employee.employment_status).all()
            )

            # Store distribution
            store_distribution = db.session.query(
                Store.name,
                func.count(Employee.id).label('count')
            ).join(Employee).filter(
                Employee.employment_status == 'active'
            ).group_by(Store.id, Store.name).all()

            # Position distribution
            position_distribution = db.session.query(
                Position.name,
                func.count(Employee.id).label('count')
            ).join(Employee).filter(
                Employee.employment_status == 'active'
            ).group_by(Position.id, Position.name).all()

            # Department distribution
            department_distribution = db.session.query(
                Department.name,
                func.count(Employee.id).label('count')
            ).join(Employee).filter(
                Employee.employment_status == 'active',
                Employee.department_id.isnot(None)
            ).group_by(Department.id, Department.name).all()

            # Tenure analysis
            active_employees_obj = Employee.query.filter_by(employment_status='active').all()
            tenures = [emp.tenure_years for emp in active_employees_obj]
            avg_tenure = sum(tenures) / len(tenures) if tenures else 0

            # Tenure distribution
            tenure_ranges = {
                '1年未満': 0,
                '1-3年': 0,
                '3-5年': 0,
                '5-10年': 0,
                '10年以上': 0
            }

            for tenure in tenures:
                if tenure < 1:
                    tenure_ranges['1年未満'] += 1
                elif tenure < 3:
                    tenure_ranges['1-3年'] += 1
                elif tenure < 5:
                    tenure_ranges['3-5年'] += 1
                elif tenure < 10:
                    tenure_ranges['5-10年'] += 1
                else:
                    tenure_ranges['10年以上'] += 1

            return {
                'total_employees': total_employees,
                'active_employees': active_employees,
                'inactive_employees': inactive_employees,
                'status_breakdown': status_counts,
                'store_distribution': dict(store_distribution),
                'position_distribution': dict(position_distribution),
                'department_distribution': dict(department_distribution),
                'average_tenure': round(avg_tenure, 1),
                'tenure_distribution': tenure_ranges,
                'management_count': Employee.query.join(Position).filter(
                    Employee.employment_status == 'active',
                    Position.is_management == True
                ).count()
            }

        except Exception as e:
            return {
                'error': f"統計取得エラー: {str(e)}",
                'total_employees': 0,
                'active_employees': 0
            }

    @staticmethod
    def get_positions() -> List[Position]:
        """
        Get all active positions

        Returns:
            List of active positions
        """
        return Position.get_active_positions().all()

    @staticmethod
    def get_departments() -> List[Department]:
        """
        Get all active departments

        Returns:
            List of active departments
        """
        return Department.get_active_departments().all()

    @staticmethod
    def get_department_hierarchy() -> List[Dict[str, Any]]:
        """
        Get complete department hierarchy

        Returns:
            Hierarchical department structure
        """
        return Department.get_hierarchy_tree()

    @staticmethod
    def transfer_employee(employee_id: int, new_store_id: int,
                         new_position_id: Optional[int] = None,
                         new_department_id: Optional[int] = None,
                         new_manager_id: Optional[int] = None) -> Tuple[bool, str]:
        """
        Transfer employee to different store/position

        Args:
            employee_id: Employee to transfer
            new_store_id: New store ID
            new_position_id: New position ID (optional)
            new_department_id: New department ID (optional)
            new_manager_id: New manager ID (optional)

        Returns:
            Tuple of (success, message)
        """
        try:
            employee = Employee.query.get(employee_id)
            if not employee:
                return False, "従業員が見つかりません"

            if not employee.is_active:
                return False, "非アクティブな従業員は異動できません"

            # Validate new store
            new_store = Store.query.get(new_store_id)
            if not new_store or not new_store.is_active:
                return False, "指定された異動先店舗が見つかりません"

            old_store_name = employee.store.name
            employee.transfer_to_store(new_store_id, new_position_id, new_department_id, new_manager_id)
            db.session.commit()

            return True, f"従業員 '{employee.full_name}' を {old_store_name} から {new_store.name} に異動しました"

        except Exception as e:
            db.session.rollback()
            return False, f"異動処理エラー: {str(e)}"

    @staticmethod
    def get_managers_for_store(store_id: int) -> List[Employee]:
        """
        Get potential managers for a store

        Args:
            store_id: Store ID

        Returns:
            List of management-level employees in the store
        """
        return Employee.query.join(Position).filter(
            Employee.store_id == store_id,
            Employee.employment_status == 'active',
            Position.is_management == True
        ).order_by(Position.level, Employee.last_name).all()

    @staticmethod
    def promote_employee(employee_id: int, new_position_id: int) -> Tuple[bool, str]:
        """
        Promote employee to new position

        Args:
            employee_id: Employee to promote
            new_position_id: New position ID

        Returns:
            Tuple of (success, message)
        """
        try:
            employee = Employee.query.get(employee_id)
            if not employee:
                return False, "従業員が見つかりません"

            new_position = Position.query.get(new_position_id)
            if not new_position or not new_position.is_active:
                return False, "指定された役職が見つかりません"

            old_position_name = employee.position.name
            employee.position_id = new_position_id
            employee.updated_at = datetime.utcnow()
            db.session.commit()

            return True, f"従業員 '{employee.full_name}' を {old_position_name} から {new_position.name} に昇進させました"

        except Exception as e:
            db.session.rollback()
            return False, f"昇進処理エラー: {str(e)}"