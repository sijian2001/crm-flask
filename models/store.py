"""
Store model module

This module contains the Store model for managing store information,
business status, and operational details.
"""
from datetime import datetime, date
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property

from models import db


class Store(db.Model):
    """
    Store model for managing store information

    Attributes:
        id: Primary key
        name: Store name
        address: Full address
        phone: Contact phone number
        email: Contact email address
        business_hours: Operating hours (JSON format)
        closed_days: Closed days of week
        status: Current business status
        location_prefecture: Prefecture/state
        location_city: City
        establishment_date: Date when store was established
        created_at: Record creation timestamp
        updated_at: Record update timestamp
    """
    __tablename__ = 'stores'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Basic information
    name = db.Column(db.String(200), nullable=False, index=True)
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)

    # Business information
    business_hours = db.Column(db.JSON, nullable=True)  # {'mon': '9:00-18:00', 'tue': '9:00-18:00', ...}
    closed_days = db.Column(db.String(50), nullable=True, default='')  # 'sat,sun' or individual days
    status = db.Column(db.String(20), nullable=False, default='active')  # active, inactive, temporarily_closed

    # Location information
    location_prefecture = db.Column(db.String(50), nullable=True, index=True)
    location_city = db.Column(db.String(100), nullable=True, index=True)

    # Date information
    establishment_date = db.Column(db.Date, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __init__(self, name, address, phone=None, email=None, business_hours=None,
                 closed_days='', status='active', location_prefecture=None,
                 location_city=None, establishment_date=None):
        """
        Initialize Store instance

        Args:
            name: Store name
            address: Store address
            phone: Contact phone number
            email: Contact email address
            business_hours: Operating hours dictionary
            closed_days: Closed days string
            status: Business status
            location_prefecture: Prefecture/state
            location_city: City
            establishment_date: Establishment date
        """
        self.name = name
        self.address = address
        self.phone = phone
        self.email = email
        self.business_hours = business_hours or self._default_business_hours()
        self.closed_days = closed_days or ''
        self.status = status
        self.location_prefecture = location_prefecture
        self.location_city = location_city
        self.establishment_date = establishment_date or date.today()
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def _default_business_hours(self):
        """Get default business hours"""
        return {
            'mon': '09:00-18:00',
            'tue': '09:00-18:00',
            'wed': '09:00-18:00',
            'thu': '09:00-18:00',
            'fri': '09:00-18:00',
            'sat': '10:00-17:00',
            'sun': 'closed'
        }

    @hybrid_property
    def business_years(self):
        """
        Calculate business years since establishment

        Returns:
            Number of years in business (float)
        """
        if not self.establishment_date:
            return 0.0

        today = date.today()
        delta = today - self.establishment_date
        return round(delta.days / 365.25, 1)

    @hybrid_property
    def is_active(self):
        """
        Check if store is currently active

        Returns:
            True if store is active
        """
        return self.status == 'active'

    @hybrid_property
    def is_temporarily_closed(self):
        """
        Check if store is temporarily closed

        Returns:
            True if store is temporarily closed
        """
        return self.status == 'temporarily_closed'

    @hybrid_property
    def location_full(self):
        """
        Get full location string

        Returns:
            Combined prefecture and city
        """
        parts = []
        if self.location_prefecture:
            parts.append(self.location_prefecture)
        if self.location_city:
            parts.append(self.location_city)
        return ', '.join(parts) if parts else ''

    @hybrid_property
    def closed_days_list(self):
        """
        Get list of closed days

        Returns:
            List of closed day abbreviations
        """
        if not self.closed_days:
            return []
        return [day.strip() for day in self.closed_days.split(',') if day.strip()]

    def is_open_on_day(self, day_abbr):
        """
        Check if store is open on specific day

        Args:
            day_abbr: Day abbreviation (mon, tue, wed, thu, fri, sat, sun)

        Returns:
            True if store is open on that day
        """
        if not self.business_hours:
            return False

        day_hours = self.business_hours.get(day_abbr.lower())
        return day_hours and day_hours.lower() != 'closed'

    def get_hours_for_day(self, day_abbr):
        """
        Get operating hours for specific day

        Args:
            day_abbr: Day abbreviation

        Returns:
            Hours string or 'Closed'
        """
        if not self.business_hours:
            return 'Closed'

        day_hours = self.business_hours.get(day_abbr.lower(), 'Closed')
        return day_hours if day_hours.lower() != 'closed' else 'Closed'

    def update_status(self, new_status):
        """
        Update store status

        Args:
            new_status: New status value
        """
        valid_statuses = ['active', 'inactive', 'temporarily_closed']
        if new_status in valid_statuses:
            self.status = new_status
            self.updated_at = datetime.utcnow()

    def update_business_hours(self, new_hours):
        """
        Update business hours

        Args:
            new_hours: Dictionary of new business hours
        """
        if isinstance(new_hours, dict):
            self.business_hours = new_hours
            self.updated_at = datetime.utcnow()

    def to_dict(self):
        """
        Convert store to dictionary

        Returns:
            Dictionary representation of store
        """
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'business_hours': self.business_hours,
            'closed_days': self.closed_days,
            'status': self.status,
            'location_prefecture': self.location_prefecture,
            'location_city': self.location_city,
            'establishment_date': self.establishment_date.isoformat() if self.establishment_date else None,
            'business_years': self.business_years,
            'is_active': self.is_active,
            'location_full': self.location_full,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        """String representation of Store"""
        return f'<Store {self.id}: {self.name} ({self.status})>'

    def __str__(self):
        """Human-readable string representation"""
        return f'{self.name} - {self.location_full or "No location"} ({self.status})'

    @classmethod
    def get_by_status(cls, status):
        """
        Get stores by status

        Args:
            status: Store status to filter by

        Returns:
            Query object for stores with specified status
        """
        return cls.query.filter(cls.status == status)

    @classmethod
    def get_active_stores(cls):
        """
        Get all active stores

        Returns:
            Query object for active stores
        """
        return cls.get_by_status('active')

    @classmethod
    def get_by_location(cls, prefecture=None, city=None):
        """
        Get stores by location

        Args:
            prefecture: Prefecture to filter by
            city: City to filter by

        Returns:
            Query object for stores in specified location
        """
        query = cls.query

        if prefecture:
            query = query.filter(cls.location_prefecture == prefecture)
        if city:
            query = query.filter(cls.location_city == city)

        return query

    @classmethod
    def search(cls, search_term):
        """
        Search stores by name or address

        Args:
            search_term: Term to search for

        Returns:
            Query object for matching stores
        """
        if not search_term:
            return cls.query

        search_pattern = f'%{search_term}%'
        return cls.query.filter(
            db.or_(
                cls.name.ilike(search_pattern),
                cls.address.ilike(search_pattern),
                cls.location_prefecture.ilike(search_pattern),
                cls.location_city.ilike(search_pattern)
            )
        )