"""
Bank Management System - Authentication Routes
Handles login, registration, and logout for customers and admins
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models import *
from app import mysql

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    """Home page - redirect based on login status"""
    if current_user.is_authenticated:
        if current_user.user_type == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('customer.dashboard'))
    return render_template('auth/login.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Customer login page"""
    if current_user.is_authenticated:
        return redirect(url_for('customer.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('auth/login.html')
        
        customer = Customer.verify_password(email, password)
        
        if customer:
            if not customer.is_active:
                flash('Your account has been deactivated. Please contact support.', 'error')
                return render_template('auth/login.html')
            
            login_user(customer, remember=remember)
            
            # Log the login
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO audit_log (user_type, user_id, action, ip_address, user_agent)
                VALUES ('customer', %s, 'LOGIN', %s, %s)
            """, (customer.customer_id, request.remote_addr, request.user_agent.string[:255]))
            mysql.connection.commit()
            cur.close()
            
            flash(f'Welcome back, {customer.first_name}!', 'success')
            
            # Redirect to requested page or dashboard
            next_page = request.args.get('next')
            return redirect(next_page or url_for('customer.dashboard'))
        
        flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Customer registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('customer.dashboard'))
    
    if request.method == 'POST':
        # Get form data
        data = {
            'first_name': request.form.get('first_name', '').strip(),
            'last_name': request.form.get('last_name', '').strip(),
            'email': request.form.get('email', '').strip().lower(),
            'phone': request.form.get('phone', '').strip(),
            'password': request.form.get('password', ''),
            'confirm_password': request.form.get('confirm_password', ''),
            'address': request.form.get('address', '').strip(),
            'city': request.form.get('city', '').strip(),
            'state': request.form.get('state', '').strip(),
            'pincode': request.form.get('pincode', '').strip(),
            'date_of_birth': request.form.get('date_of_birth', ''),
            'gender': request.form.get('gender', ''),
            'id_proof_type': request.form.get('id_proof_type', ''),
            'id_proof_number': request.form.get('id_proof_number', '').strip()
        }
        
        # Validation
        errors = []
        
        if not all([data['first_name'], data['last_name'], data['email'],
                   data['phone'], data['password']]):
            errors.append('Please fill in all required fields.')
        
        if len(data['password']) < 8:
            errors.append('Password must be at least 8 characters long.')
        
        if data['password'] != data['confirm_password']:
            errors.append('Passwords do not match.')
        
        if len(data['phone']) < 10:
            errors.append('Please enter a valid phone number.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html', data=data)
        
        # Create customer
        customer_id, message = Customer.create(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data['phone'],
            password=data['password'],
            address=data['address'],
            city=data['city'],
            state=data['state'],
            pincode=data['pincode'],
            date_of_birth=data['date_of_birth'] or None,
            gender=data['gender'] or None,
            id_proof_type=data['id_proof_type'] or None,
            id_proof_number=data['id_proof_number'] or None
        )
        
        if customer_id:
            flash('Registration successful! Please login to continue.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'error')
    
    return render_template('auth/register.html', data={})


@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if current_user.is_authenticated and current_user.user_type == 'admin':
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('auth/admin_login.html')
        
        admin = Admin.verify_password(username, password)
        
        if admin:
            if not admin.is_active:
                flash('Your account has been deactivated.', 'error')
                return render_template('auth/admin_login.html')
            
            login_user(admin)
            
            # Log the login
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO audit_log (user_type, user_id, action, ip_address, user_agent)
                VALUES ('admin', %s, 'LOGIN', %s, %s)
            """, (admin.admin_id, request.remote_addr, request.user_agent.string[:255]))
            mysql.connection.commit()
            cur.close()
            
            flash(f'Welcome, {admin.full_name}!', 'success')
            return redirect(url_for('admin.dashboard'))
        
        flash('Invalid username or password.', 'error')
    
    return render_template('auth/admin_login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
