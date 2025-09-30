"""
Department model module

This module contains the Department model for managing organizational
departments and hierarchical structure.
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property

from models import db


class Department(db.Model):
    """
    Department model for managing organizational departments

    Attributes:
        id: Primary key
        name: Department name
        parent_id: Parent department ID for hierarchical structure
        description: Department description
        head_employee_id: Department head employee ID
        is_active: Whether this department is currently active
        created_at: Record creation timestamp
        updated_at: Record update timestamp
    """
    __tablename__ = 'departments'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Basic information
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)

    # Hierarchical structure
    parent_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True, index=True)

    # Department management
    head_employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)

    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    parent = db.relationship('Department', remote_side=[id], backref='children')
    employees = db.relationship('Employee', back_populates='department', lazy='dynamic',
                              foreign_keys='Employee.department_id')
    head_employee = db.relationship('Employee', foreign_keys=[head_employee_id], post_update=True)

    def __init__(self, name, parent_id=None, description=None, head_employee_id=None, is_active=True):
        """
        Initialize Department instance

        Args:
            name: Department name
            parent_id: Parent department ID
            description: Department description
            head_employee_id: Department head employee ID
            is_active: Active status
        """
        self.name = name
        self.parent_id = parent_id
        self.description = description
        self.head_employee_id = head_employee_id
        self.is_active = is_active
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    @hybrid_property
    def full_name(self):
        """
        Get full department name with parent hierarchy

        Returns:
            Full hierarchical department name
        """
        if self.parent:
            return f"{self.parent.full_name} > {self.name}"
        return self.name

    @hybrid_property
    def level(self):
        """
        Get department level in hierarchy (0=root)

        Returns:
            Department level number
        """
        if not self.parent:
            return 0
        return self.parent.level + 1

    @property
    def employee_count(self):
        """
        Get number of employees in this department

        Returns:
            Number of active employees in this department
        """
        return self.employees.filter_by(employment_status='active').count()

    @property
    def total_employee_count(self):
        """
        Get total number of employees including subdepartments

        Returns:
            Total employee count in this department and all subdepartments
        """
        count = self.employee_count
        for child in self.children:
            count += child.total_employee_count
        return count

    @property
    def subdepartment_count(self):
        """
        Get number of active subdepartments

        Returns:
            Number of active child departments
        """
        return len([child for child in self.children if child.is_active])

    def get_all_children(self, include_inactive: bool = False) -> List['Department']:
        """
        Get all descendant departments recursively

        Args:
            include_inactive: Whether to include inactive departments

        Returns:
            List of all descendant departments
        """
        children = []
        for child in self.children:
            if include_inactive or child.is_active:
                children.append(child)
                children.extend(child.get_all_children(include_inactive))
        return children

    def get_root_department(self) -> 'Department':
        """
        Get the root department of this hierarchy

        Returns:
            Root department object
        """
        if not self.parent:
            return self
        return self.parent.get_root_department()

    def is_descendant_of(self, other_department: 'Department') -> bool:
        """
        Check if this department is a descendant of another

        Args:
            other_department: Department to check against

        Returns:
            True if this department is a descendant
        """
        if not self.parent:
            return False
        if self.parent.id == other_department.id:
            return True
        return self.parent.is_descendant_of(other_department)

    def can_be_moved_to(self, new_parent: Optional['Department']) -> bool:
        """
        Check if department can be moved to new parent without creating cycles

        Args:
            new_parent: Proposed new parent department

        Returns:
            True if move is valid
        """
        if not new_parent:
            return True
        if new_parent.id == self.id:
            return False
        return not new_parent.is_descendant_of(self)

    def to_dict(self, include_children=False):
        """
        Convert department to dictionary

        Args:
            include_children: Whether to include child departments

        Returns:
            Dictionary representation of department
        """
        result = {
            'id': self.id,
            'name': self.name,
            'full_name': self.full_name,
            'description': self.description,
            'parent_id': self.parent_id,
            'parent_name': self.parent.name if self.parent else None,
            'head_employee_id': self.head_employee_id,
            'head_employee_name': self.head_employee.full_name if self.head_employee else None,
            'level': self.level,
            'is_active': self.is_active,
            'employee_count': self.employee_count,
            'total_employee_count': self.total_employee_count,
            'subdepartment_count': self.subdepartment_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_children:
            result['children'] = [child.to_dict() for child in self.children if child.is_active]

        return result

    def __repr__(self):
        """String representation of Department"""
        return f'<Department {self.id}: {self.name}>'

    def __str__(self):
        """Human-readable string representation"""
        return self.full_name

    @classmethod
    def get_active_departments(cls):
        """
        Get all active departments ordered by name

        Returns:
            Query object for active departments
        """
        return cls.query.filter(cls.is_active == True).order_by(cls.name)

    @classmethod
    def get_root_departments(cls):
        """
        Get all root departments (no parent)

        Returns:
            Query object for root departments
        """
        return cls.query.filter(cls.parent_id.is_(None), cls.is_active == True).order_by(cls.name)

    @classmethod
    def get_by_level(cls, level):
        """
        Get departments at specific hierarchical level

        Args:
            level: Target level (0=root)

        Returns:
            List of departments at specified level
        """
        if level == 0:
            return cls.get_root_departments().all()

        departments = []
        for dept in cls.get_active_departments().all():
            if dept.level == level:
                departments.append(dept)
        return departments

    @classmethod
    def get_hierarchy_tree(cls):
        """
        Get complete department hierarchy as nested dict

        Returns:
            List of root departments with nested children
        """
        roots = cls.get_root_departments().all()
        return [dept.to_dict(include_children=True) for dept in roots]