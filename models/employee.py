"""
Employee model module

This module contains the Employee model for managing employee information,
organizational relationships, and employment details.
"""
from datetime import datetime, date
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property

from models import db


class Employee(db.Model):
    """
    Employee model for managing employee information

    Attributes:
        id: Primary key
        employee_code: Unique employee identifier
        first_name: Employee first name
        last_name: Employee last name
        email: Employee email address
        phone: Employee phone number
        hire_date: Date of hiring
        employment_status: Current employment status
        salary_level: Current salary level
        store_id: Associated store ID
        position_id: Position/role ID
        department_id: Department ID
        manager_id: Manager employee ID
        emergency_contact_name: Emergency contact name
        emergency_contact_phone: Emergency contact phone
        notes: Additional notes
        created_at: Record creation timestamp
        updated_at: Record update timestamp
    """
    __tablename__ = 'employees'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Basic identification
    employee_code = db.Column(db.String(20), nullable=False, unique=True, index=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

    # Contact information
    email = db.Column(db.String(120), nullable=True, unique=True, index=True)
    phone = db.Column(db.String(20), nullable=True)

    # Employment information
    hire_date = db.Column(db.Date, nullable=False, index=True)
    employment_status = db.Column(db.String(20), nullable=False, default='active', index=True)
    salary_level = db.Column(db.Integer, nullable=True)  # Salary level 1-10

    # Organization relationships
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False, index=True)
    position_id = db.Column(db.Integer, db.ForeignKey('positions.id'), nullable=False, index=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True, index=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True, index=True)

    # Emergency contact
    emergency_contact_name = db.Column(db.String(100), nullable=True)
    emergency_contact_phone = db.Column(db.String(20), nullable=True)

    # Additional information
    notes = db.Column(db.Text, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    store = db.relationship('Store', backref='employees')
    position = db.relationship('Position', back_populates='employees')
    department = db.relationship('Department', back_populates='employees', foreign_keys=[department_id])
    manager = db.relationship('Employee', remote_side=[id], backref='subordinates')

    def __init__(self, employee_code, first_name, last_name, email, hire_date,
                 store_id, position_id, department_id=None, manager_id=None,
                 phone=None, employment_status='active', salary_level=None,
                 emergency_contact_name=None, emergency_contact_phone=None, notes=None):
        """
        Initialize Employee instance

        Args:
            employee_code: Unique employee code
            first_name: Employee first name
            last_name: Employee last name
            email: Employee email
            hire_date: Date of hiring
            store_id: Store ID
            position_id: Position ID
            department_id: Department ID
            manager_id: Manager employee ID
            phone: Phone number
            employment_status: Employment status
            salary_level: Salary level
            emergency_contact_name: Emergency contact name
            emergency_contact_phone: Emergency contact phone
            notes: Additional notes
        """
        self.employee_code = employee_code
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.hire_date = hire_date if isinstance(hire_date, date) else datetime.strptime(hire_date, '%Y-%m-%d').date()
        self.employment_status = employment_status
        self.salary_level = salary_level
        self.store_id = store_id
        self.position_id = position_id
        self.department_id = department_id
        self.manager_id = manager_id
        self.emergency_contact_name = emergency_contact_name
        self.emergency_contact_phone = emergency_contact_phone
        self.notes = notes
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    @hybrid_property
    def full_name(self):
        """
        Get full name (last name + first name)

        Returns:
            Full name string
        """
        return f"{self.last_name} {self.first_name}"

    @hybrid_property
    def tenure_years(self):
        """
        Calculate tenure years since hire date

        Returns:
            Number of years employed (float)
        """
        if not self.hire_date:
            return 0.0

        today = date.today()
        delta = today - self.hire_date
        return round(delta.days / 365.25, 1)

    @hybrid_property
    def is_active(self):
        """
        Check if employee is currently active

        Returns:
            True if employee is active
        """
        return self.employment_status == 'active'

    @hybrid_property
    def is_manager(self):
        """
        Check if employee is a manager (has subordinates)

        Returns:
            True if employee has subordinates
        """
        return len(self.subordinates) > 0

    @hybrid_property
    def is_management_position(self):
        """
        Check if employee is in management position

        Returns:
            True if position is management level
        """
        return self.position and self.position.is_management

    @property
    def subordinate_count(self):
        """
        Get number of direct subordinates

        Returns:
            Number of active subordinates
        """
        return len([sub for sub in self.subordinates if sub.is_active])

    @property
    def salary_range(self):
        """
        Get salary range based on position and level

        Returns:
            Estimated salary range string
        """
        if not self.position:
            return "未設定"

        base_min = self.position.salary_min or 200
        base_max = self.position.salary_max or 800

        if self.salary_level:
            level_multiplier = 1 + (self.salary_level - 1) * 0.1
            actual_min = int(base_min * level_multiplier)
            actual_max = int(base_max * level_multiplier)
            return f"{actual_min}万円 - {actual_max}万円"

        return self.position.salary_range_display

    def get_all_subordinates(self):
        """
        Get all subordinates recursively

        Returns:
            List of all subordinate employees
        """
        all_subordinates = []
        for subordinate in self.subordinates:
            if subordinate.is_active:
                all_subordinates.append(subordinate)
                all_subordinates.extend(subordinate.get_all_subordinates())
        return all_subordinates

    def can_be_manager_of(self, employee):
        """
        Check if this employee can be manager of another employee

        Args:
            employee: Employee to check

        Returns:
            True if can be manager (no circular reference)
        """
        if employee.id == self.id:
            return False

        # Check if the employee is already a manager of this employee
        current = self
        while current.manager:
            if current.manager.id == employee.id:
                return False
            current = current.manager

        return True

    def update_status(self, new_status):
        """
        Update employment status

        Args:
            new_status: New employment status
        """
        valid_statuses = ['active', 'inactive', 'on_leave', 'terminated']
        if new_status in valid_statuses:
            self.employment_status = new_status
            self.updated_at = datetime.utcnow()

    def transfer_to_store(self, new_store_id, new_position_id=None, new_department_id=None, new_manager_id=None):
        """
        Transfer employee to different store/position

        Args:
            new_store_id: New store ID
            new_position_id: New position ID (optional)
            new_department_id: New department ID (optional)
            new_manager_id: New manager ID (optional)
        """
        self.store_id = new_store_id
        if new_position_id:
            self.position_id = new_position_id
        if new_department_id is not None:
            self.department_id = new_department_id
        if new_manager_id is not None:
            self.manager_id = new_manager_id
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        """
        Convert employee to dictionary

        Returns:
            Dictionary representation of employee
        """
        return {
            'id': self.id,
            'employee_code': self.employee_code,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'employment_status': self.employment_status,
            'salary_level': self.salary_level,
            'salary_range': self.salary_range,
            'store_id': self.store_id,
            'store_name': self.store.name if self.store else None,
            'position_id': self.position_id,
            'position_name': self.position.name if self.position else None,
            'department_id': self.department_id,
            'department_name': self.department.name if self.department else None,
            'manager_id': self.manager_id,
            'manager_name': self.manager.full_name if self.manager else None,
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_contact_phone': self.emergency_contact_phone,
            'notes': self.notes,
            'tenure_years': self.tenure_years,
            'is_active': self.is_active,
            'is_manager': self.is_manager,
            'is_management_position': self.is_management_position,
            'subordinate_count': self.subordinate_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        """String representation of Employee"""
        return f'<Employee {self.id}: {self.employee_code} - {self.full_name}>'

    def __str__(self):
        """Human-readable string representation"""
        return f'{self.full_name} ({self.employee_code}) - {self.position.name if self.position else "未設定"}'

    @classmethod
    def get_active_employees(cls):
        """
        Get all active employees

        Returns:
            Query object for active employees
        """
        return cls.query.filter(cls.employment_status == 'active')

    @classmethod
    def get_by_store(cls, store_id):
        """
        Get employees by store

        Args:
            store_id: Store ID to filter by

        Returns:
            Query object for employees in specified store
        """
        return cls.query.filter(cls.store_id == store_id)

    @classmethod
    def get_by_position(cls, position_id):
        """
        Get employees by position

        Args:
            position_id: Position ID to filter by

        Returns:
            Query object for employees in specified position
        """
        return cls.query.filter(cls.position_id == position_id)

    @classmethod
    def get_by_department(cls, department_id):
        """
        Get employees by department

        Args:
            department_id: Department ID to filter by

        Returns:
            Query object for employees in specified department
        """
        return cls.query.filter(cls.department_id == department_id)

    @classmethod
    def search(cls, search_term):
        """
        Search employees by name, code, or email

        Args:
            search_term: Term to search for

        Returns:
            Query object for matching employees
        """
        if not search_term:
            return cls.query

        search_pattern = f'%{search_term}%'
        return cls.query.filter(
            db.or_(
                cls.first_name.ilike(search_pattern),
                cls.last_name.ilike(search_pattern),
                cls.employee_code.ilike(search_pattern),
                cls.email.ilike(search_pattern)
            )
        )