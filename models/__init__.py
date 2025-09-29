"""
Models package for CRM application

This package contains all data models including User, Customer, Product, Category, Store, and Employee management.
"""
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()

# Import all models to make them available
from .user import User
from .customer import Customer
from .product import Product
from .category import Category
from .store import Store
from .position import Position
from .department import Department
from .employee import Employee

__all__ = ['db', 'User', 'Customer', 'Product', 'Category', 'Store', 'Position', 'Department', 'Employee']