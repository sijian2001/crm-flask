"""
Position model module

This module contains the Position model for managing employee positions
and organizational hierarchy.
"""
from datetime import datetime
from sqlalchemy import func

from models import db


class Position(db.Model):
    """
    Position model for managing employee positions

    Attributes:
        id: Primary key
        name: Position name (店長, 副店長, スタッフ, etc.)
        level: Hierarchical level (1=highest, higher numbers=lower)
        description: Position description
        is_management: Whether this position is management level
        salary_min: Minimum salary for this position
        salary_max: Maximum salary for this position
        is_active: Whether this position is currently active
        created_at: Record creation timestamp
        updated_at: Record update timestamp
    """
    __tablename__ = 'positions'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Basic information
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    level = db.Column(db.Integer, nullable=False, default=999)  # 1=highest level
    description = db.Column(db.Text, nullable=True)

    # Management and privileges
    is_management = db.Column(db.Boolean, default=False, nullable=False)

    # Salary range
    salary_min = db.Column(db.Integer, nullable=True)  # Minimum salary in thousands
    salary_max = db.Column(db.Integer, nullable=True)  # Maximum salary in thousands

    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    employees = db.relationship('Employee', back_populates='position', lazy='dynamic')

    def __init__(self, name, level=999, description=None, is_management=False,
                 salary_min=None, salary_max=None, is_active=True):
        """
        Initialize Position instance

        Args:
            name: Position name
            level: Hierarchical level
            description: Position description
            is_management: Management position flag
            salary_min: Minimum salary
            salary_max: Maximum salary
            is_active: Active status
        """
        self.name = name
        self.level = level
        self.description = description
        self.is_management = is_management
        self.salary_min = salary_min
        self.salary_max = salary_max
        self.is_active = is_active
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    @property
    def employee_count(self):
        """
        Get number of employees in this position

        Returns:
            Number of active employees in this position
        """
        return self.employees.filter_by(employment_status='active').count()

    @property
    def salary_range_display(self):
        """
        Get formatted salary range string

        Returns:
            Formatted salary range or 'Not specified'
        """
        if self.salary_min and self.salary_max:
            return f"{self.salary_min}万円 - {self.salary_max}万円"
        elif self.salary_min:
            return f"{self.salary_min}万円以上"
        elif self.salary_max:
            return f"{self.salary_max}万円以下"
        else:
            return "未設定"

    def is_higher_than(self, other_position):
        """
        Check if this position is hierarchically higher than another

        Args:
            other_position: Position to compare with

        Returns:
            True if this position is higher (lower level number)
        """
        if not other_position:
            return True
        return self.level < other_position.level

    def to_dict(self):
        """
        Convert position to dictionary

        Returns:
            Dictionary representation of position
        """
        return {
            'id': self.id,
            'name': self.name,
            'level': self.level,
            'description': self.description,
            'is_management': self.is_management,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'salary_range_display': self.salary_range_display,
            'is_active': self.is_active,
            'employee_count': self.employee_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        """String representation of Position"""
        return f'<Position {self.id}: {self.name} (Level {self.level})>'

    def __str__(self):
        """Human-readable string representation"""
        mgmt_status = "管理職" if self.is_management else "一般職"
        return f'{self.name} - Level {self.level} ({mgmt_status})'

    @classmethod
    def get_active_positions(cls):
        """
        Get all active positions ordered by level

        Returns:
            Query object for active positions
        """
        return cls.query.filter(cls.is_active == True).order_by(cls.level, cls.name)

    @classmethod
    def get_management_positions(cls):
        """
        Get all management positions

        Returns:
            Query object for management positions
        """
        return cls.query.filter(cls.is_management == True, cls.is_active == True).order_by(cls.level)

    @classmethod
    def get_by_level_range(cls, min_level=None, max_level=None):
        """
        Get positions within level range

        Args:
            min_level: Minimum level (inclusive)
            max_level: Maximum level (inclusive)

        Returns:
            Query object for positions in level range
        """
        query = cls.query.filter(cls.is_active == True)

        if min_level is not None:
            query = query.filter(cls.level >= min_level)
        if max_level is not None:
            query = query.filter(cls.level <= max_level)

        return query.order_by(cls.level, cls.name)