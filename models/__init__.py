"""
Models package for CRM application

This package contains all data models including User, Customer, Product, and Category.
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

__all__ = ['db', 'User', 'Customer', 'Product', 'Category', 'Store']