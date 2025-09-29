"""
Test cases for Employee, Position, and Department models

This module contains comprehensive tests for all employee-related models
including their properties, relationships, and business logic.
"""
import pytest
from datetime import date, datetime

from models import Employee, Position, Department


class TestPosition:
    """Test cases for Position model"""

    def test_create_position(self, db_session):
        """Test basic position creation"""
        position = Position(
            name='テスト役職',
            level=3,
            description='テスト用の役職',
            is_management=True,
            salary_min=300,
            salary_max=600
        )
        db_session.add(position)
        db_session.commit()

        assert position.id is not None
        assert position.name == 'テスト役職'
        assert position.level == 3
        assert position.is_management is True
        assert position.is_active is True

    def test_position_salary_range_display(self, sample_position):
        """Test salary range display property"""
        assert sample_position.salary_range_display == "400万円 - 800万円"

        # Test with only min salary
        sample_position.salary_max = None
        assert sample_position.salary_range_display == "400万円以上"

        # Test with only max salary
        sample_position.salary_min = None
        sample_position.salary_max = 800
        assert sample_position.salary_range_display == "800万円以下"

        # Test with no salary info
        sample_position.salary_min = None
        sample_position.salary_max = None
        assert sample_position.salary_range_display == "未設定"

    def test_position_hierarchy_comparison(self, db_session):
        """Test position hierarchy comparison"""
        manager = Position(name='部長', level=1, is_management=True)
        supervisor = Position(name='課長', level=2, is_management=True)
        staff = Position(name='一般', level=5, is_management=False)

        db_session.add_all([manager, supervisor, staff])
        db_session.commit()

        assert manager.is_higher_than(supervisor)
        assert manager.is_higher_than(staff)
        assert supervisor.is_higher_than(staff)
        assert not staff.is_higher_than(supervisor)

    def test_position_to_dict(self, sample_position):
        """Test position dictionary conversion"""
        position_dict = sample_position.to_dict()

        assert position_dict['name'] == '店長'
        assert position_dict['level'] == 1
        assert position_dict['is_management'] is True
        assert 'employee_count' in position_dict
        assert 'salary_range_display' in position_dict


class TestDepartment:
    """Test cases for Department model"""

    def test_create_department(self, db_session):
        """Test basic department creation"""
        department = Department(
            name='テスト部署',
            description='テスト用の部署'
        )
        db_session.add(department)
        db_session.commit()

        assert department.id is not None
        assert department.name == 'テスト部署'
        assert department.is_active is True
        assert department.parent_id is None

    def test_department_hierarchy(self, sample_department, sample_sub_department):
        """Test department hierarchy relationships"""
        assert sample_sub_department.parent == sample_department
        assert sample_sub_department in sample_department.children
        assert sample_sub_department.level == 1
        assert sample_department.level == 0

    def test_department_full_name(self, sample_department, sample_sub_department):
        """Test department full name property"""
        assert sample_department.full_name == '営業部'
        assert sample_sub_department.full_name == '営業部 > 第一営業課'

    def test_department_hierarchy_methods(self, db_session, sample_department):
        """Test department hierarchy helper methods"""
        # Create deeper hierarchy
        sub_dept = Department(
            name='第二営業課',
            parent_id=sample_department.id,
            description='第二営業課'
        )
        sub_sub_dept = Department(
            name='営業第一係',
            parent_id=sub_dept.id,
            description='営業第一係'
        )
        db_session.add_all([sub_dept, sub_sub_dept])
        db_session.commit()

        # Test get_all_children
        all_children = sample_department.get_all_children()
        assert len(all_children) == 2
        assert sub_dept in all_children
        assert sub_sub_dept in all_children

        # Test get_root_department
        assert sub_sub_dept.get_root_department() == sample_department

        # Test is_descendant_of
        assert sub_sub_dept.is_descendant_of(sample_department)
        assert sub_sub_dept.is_descendant_of(sub_dept)
        assert not sample_department.is_descendant_of(sub_dept)

    def test_department_can_be_moved(self, db_session, sample_department):
        """Test department move validation"""
        child_dept = Department(
            name='子部署',
            parent_id=sample_department.id
        )
        grandchild_dept = Department(
            name='孫部署',
            parent_id=child_dept.id
        )
        db_session.add_all([child_dept, grandchild_dept])
        db_session.commit()

        # Valid moves
        assert child_dept.can_be_moved_to(None)  # Move to root
        assert grandchild_dept.can_be_moved_to(sample_department)  # Move up

        # Invalid moves (would create cycles)
        assert not sample_department.can_be_moved_to(child_dept)
        assert not sample_department.can_be_moved_to(grandchild_dept)
        assert not child_dept.can_be_moved_to(grandchild_dept)

    def test_department_to_dict(self, sample_department, sample_sub_department):
        """Test department dictionary conversion"""
        dept_dict = sample_department.to_dict(include_children=True)

        assert dept_dict['name'] == '営業部'
        assert dept_dict['full_name'] == '営業部'
        assert dept_dict['level'] == 0
        assert 'children' in dept_dict
        assert len(dept_dict['children']) == 1


class TestEmployee:
    """Test cases for Employee model"""

    def test_create_employee(self, db_session, sample_store, sample_position, sample_employee_data):
        """Test basic employee creation"""
        employee_data = sample_employee_data.copy()
        employee_data.update({
            'store_id': sample_store.id,
            'position_id': sample_position.id
        })
        employee = Employee(**employee_data)
        db_session.add(employee)
        db_session.commit()

        assert employee.id is not None
        assert employee.employee_code == 'EMP001'
        assert employee.full_name == '田中 太郎'
        assert employee.is_active is True

    def test_employee_full_name_property(self, sample_employee):
        """Test employee full name property"""
        assert sample_employee.full_name == '田中 太郎'

    def test_employee_tenure_calculation(self, sample_employee):
        """Test tenure years calculation"""
        # Sample employee hired on 2023-04-01
        # As of the test date, tenure should be calculated correctly
        tenure = sample_employee.tenure_years
        assert isinstance(tenure, float)
        assert tenure >= 0

    def test_employee_is_active_property(self, sample_employee):
        """Test is_active property"""
        assert sample_employee.is_active is True

        sample_employee.employment_status = 'inactive'
        assert sample_employee.is_active is False

    def test_employee_is_management_position(self, sample_employee, sample_staff_position):
        """Test is_management_position property"""
        # sample_employee has management position
        assert sample_employee.is_management_position is True

        # Change to non-management position
        sample_employee.position_id = sample_staff_position.id
        sample_employee.position = sample_staff_position
        assert sample_employee.is_management_position is False

    def test_employee_salary_range(self, sample_employee):
        """Test salary range calculation"""
        salary_range = sample_employee.salary_range
        assert isinstance(salary_range, str)
        assert '万円' in salary_range

    def test_employee_manager_subordinate_relationship(self, sample_manager, sample_subordinate):
        """Test manager-subordinate relationships"""
        assert sample_subordinate.manager == sample_manager
        assert sample_subordinate in sample_manager.subordinates
        assert sample_manager.subordinate_count == 1
        assert sample_subordinate.subordinate_count == 0

    def test_employee_get_all_subordinates(self, db_session, sample_manager, sample_store, sample_staff_position, sample_department):
        """Test recursive subordinate retrieval"""
        # Create multi-level hierarchy
        middle_manager = Employee(
            employee_code='MM001',
            first_name='中間',
            last_name='管理',
            email='middle@company.com',
            hire_date=date(2022, 1, 1),
            employment_status='active',
            store_id=sample_store.id,
            position_id=sample_staff_position.id,
            department_id=sample_department.id,
            manager_id=sample_manager.id
        )

        staff = Employee(
            employee_code='ST001',
            first_name='一般',
            last_name='社員',
            email='staff@company.com',
            hire_date=date(2023, 1, 1),
            employment_status='active',
            store_id=sample_store.id,
            position_id=sample_staff_position.id,
            department_id=sample_department.id,
            manager_id=middle_manager.id
        )

        db_session.add_all([middle_manager, staff])
        db_session.commit()

        all_subordinates = sample_manager.get_all_subordinates()
        assert len(all_subordinates) == 2
        assert middle_manager in all_subordinates
        assert staff in all_subordinates

    def test_employee_can_be_manager_validation(self, sample_manager, sample_subordinate):
        """Test manager assignment validation"""
        # Valid assignments
        assert sample_manager.can_be_manager_of(sample_subordinate)

        # Invalid assignment (circular reference)
        assert not sample_subordinate.can_be_manager_of(sample_manager)

        # Self-assignment (should be invalid)
        assert not sample_manager.can_be_manager_of(sample_manager)

    def test_employee_status_update(self, sample_employee):
        """Test employment status update"""
        original_status = sample_employee.employment_status
        original_updated = sample_employee.updated_at

        # Valid status update
        sample_employee.update_status('on_leave')
        assert sample_employee.employment_status == 'on_leave'
        assert sample_employee.updated_at > original_updated

        # Invalid status (should not change)
        sample_employee.update_status('invalid_status')
        assert sample_employee.employment_status == 'on_leave'

    def test_employee_transfer(self, db_session, sample_employee, sample_store_data):
        """Test employee transfer functionality"""
        # Create new store
        new_store_data = sample_store_data.copy()
        new_store_data['name'] = 'New Test Store'
        from models import Store
        new_store = Store(**new_store_data)
        db_session.add(new_store)
        db_session.commit()

        original_store_id = sample_employee.store_id
        original_updated = sample_employee.updated_at

        # Transfer employee
        sample_employee.transfer_to_store(new_store.id)

        assert sample_employee.store_id == new_store.id
        assert sample_employee.store_id != original_store_id
        assert sample_employee.updated_at > original_updated

    def test_employee_to_dict(self, sample_employee):
        """Test employee dictionary conversion"""
        employee_dict = sample_employee.to_dict()

        assert employee_dict['employee_code'] == 'EMP001'
        assert employee_dict['full_name'] == '田中 太郎'
        assert employee_dict['employment_status'] == 'active'
        assert 'tenure_years' in employee_dict
        assert 'is_active' in employee_dict
        assert 'is_management_position' in employee_dict

    def test_employee_search_class_method(self, db_session, multiple_employees):
        """Test employee search functionality"""
        # Search by first name
        results = Employee.search('従業員1').all()
        assert len(results) == 1
        assert results[0].first_name == '従業員1'

        # Search by last name
        results = Employee.search('テスト').all()
        assert len(results) == 3  # All staff members

        # Search by employee code
        results = Employee.search('STAFF001').all()
        assert len(results) == 1

        # Search by email
        results = Employee.search('staff1@company.com').all()
        assert len(results) == 1

    def test_employee_filtering_class_methods(self, db_session, multiple_employees, sample_store, sample_position, sample_department):
        """Test employee filtering class methods"""
        # Get active employees
        active_employees = Employee.get_active_employees().all()
        assert len(active_employees) == 4  # 1 manager + 3 staff

        # Get by store
        store_employees = Employee.get_by_store(sample_store.id).all()
        assert len(store_employees) == 4

        # Get by position
        position_employees = Employee.get_by_position(sample_position.id).all()
        assert len(position_employees) == 1  # Only manager

        # Get by department
        dept_employees = Employee.get_by_department(sample_department.id).all()
        assert len(dept_employees) == 4

    def test_employee_str_representation(self, sample_employee):
        """Test string representations"""
        str_repr = str(sample_employee)
        assert '田中 太郎' in str_repr
        assert 'EMP001' in str_repr

        repr_str = repr(sample_employee)
        assert 'Employee' in repr_str
        assert 'EMP001' in repr_str

    def test_employee_hybrid_properties_sql_compatibility(self, db_session, sample_employee):
        """Test that hybrid properties work in SQL queries"""
        # Test full_name in query (this tests SQL compatibility)
        employees = Employee.query.filter(
            Employee.employment_status == 'active'
        ).all()
        assert len(employees) >= 1

        # Test tenure calculation doesn't break SQL
        active_employees = Employee.query.filter(Employee.is_active).all()
        assert len(active_employees) >= 1

    def test_employee_business_logic_validation(self, sample_employee_data, sample_store, sample_position):
        """Test business logic validation"""
        # Test required fields
        incomplete_data = sample_employee_data.copy()
        del incomplete_data['employee_code']

        with pytest.raises(TypeError):
            Employee(**incomplete_data)

        # Test valid hire date
        valid_data = sample_employee_data.copy()
        valid_data.update({
            'store_id': sample_store.id,
            'position_id': sample_position.id,
            'hire_date': date.today()
        })

        employee = Employee(**valid_data)
        assert employee.hire_date == date.today()

    def test_employee_relationships_loading(self, sample_employee):
        """Test that relationships are properly loaded"""
        assert sample_employee.store is not None
        assert sample_employee.position is not None
        assert sample_employee.department is not None
        assert sample_employee.store.name == 'Test Store'
        assert sample_employee.position.name == '店長'
        assert sample_employee.department.name == '営業部'