"""
Bank Management System - Configuration
Contains all application settings
"""

import os
from datetime import timedelta


class Config:
    """Application configuration class"""
    
    # Secret key for session management and CSRF protection
    # In production, use a secure random key stored in environment variable
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-super-secret-key-change-in-production'
    
    # MySQL Database Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'root'  # Your MySQL password
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'bank_management_system'
    MYSQL_CURSORCLASS = 'DictCursor'  # Return results as dictionaries
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_COOKIE_SECURE = False  # Set True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    
    # Application settings
    ITEMS_PER_PAGE = 10
    MAX_TRANSFER_AMOUNT = 1000000  # Maximum single transfer amount
    MIN_ACCOUNT_BALANCE = 1000  # Minimum balance for savings account
