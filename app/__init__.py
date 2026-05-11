"""
Bank Management System - Application Factory
This module initializes the Flask application and its extensions
"""

from flask import Flask
from flask_login import LoginManager
from flask_mysqldb import MySQL
from flask_wtf.csrf import CSRFProtect

# Initialize extensions (but don't configure them yet)
mysql = MySQL()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app():
    """
    Application Factory Pattern
    Creates and configures the Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('app.config.Config')
    
    # Initialize extensions with the app
    mysql.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Register blueprints (modular routes)
    from app.routes.auth import auth_bp
    from app.routes.customer import customer_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        """Load user from session data"""
        from app.models import Customer, Admin
        
        # User ID format: 'customer_1' or 'admin_1'
        if user_id.startswith('customer_'):
            return Customer.get_by_id(int(user_id.split('_')[1]))
        elif user_id.startswith('admin_'):
            return Admin.get_by_id(int(user_id.split('_')[1]))
        return None
    
    return app
