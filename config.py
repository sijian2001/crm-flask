import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///crm.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)

    # Session configuration
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'

    # Customer management configuration
    CUSTOMER_ITEMS_PER_PAGE = int(os.environ.get('CUSTOMER_ITEMS_PER_PAGE') or 10)
    CUSTOMER_MAX_ITEMS_PER_PAGE = int(os.environ.get('CUSTOMER_MAX_ITEMS_PER_PAGE') or 100)
    CUSTOMER_SEARCH_FIELDS = ['first_name', 'last_name', 'email', 'company']
    CUSTOMER_ENABLE_AUDIT_LOG = os.environ.get('CUSTOMER_ENABLE_AUDIT_LOG', 'True').lower() == 'true'

    # Customer field limits (must match database constraints)
    CUSTOMER_FIELD_LIMITS = {
        'first_name': 50,
        'last_name': 50,
        'email': 120,
        'phone': 20,
        'company': 100,
        'notes': 1000
    }