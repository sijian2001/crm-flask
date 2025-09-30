"""
Views package for CRM application

This package contains all view controllers (Flask Blueprints) including auth, customer, product, store, and employee views.
"""
from .auth_views import auth
from .customer_views import customers
from .product_views import products
from .store_views import stores
from .employee_views import employees

__all__ = ['auth', 'customers', 'products', 'stores', 'employees']