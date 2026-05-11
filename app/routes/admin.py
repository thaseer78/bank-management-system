"""
Bank Management System - Admin Routes
Handles administrative functionality
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Customer, Account, Transaction, Loan, Admin
from app import mysql
from werkzeug.security import generate_password_hash
from functools import wraps
from app.models import *

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator to ensure user is an admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_type != 'admin':
            flash('Access denied. Admin login required.', 'error')
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with system overview"""
    cur = mysql.connection.cursor()
    
    # Get statistics
    cur.execute("SELECT COUNT(*) as count FROM customers WHERE is_active = TRUE")
    total_customers = cur.fetchone()['count']
    
    cur.execute("SELECT COUNT(*) as count FROM accounts WHERE status = 'active'")
    total_accounts = cur.fetchone()['count']
    
    cur.execute("SELECT COALESCE(SUM(balance), 0) as total FROM accounts WHERE status = 'active'")
    total_balance = cur.fetchone()['total']
    
    cur.execute("SELECT COUNT(*) as count FROM loans WHERE status = 'pending'")
    pending_loans = cur.fetchone()['count']
    
    cur.execute("SELECT COUNT(*) as count FROM transactions WHERE DATE(created_at) = CURDATE()")
    today_transactions = cur.fetchone()['count']
    
    cur.execute("""
        SELECT COALESCE(SUM(amount), 0) as total 
        FROM transactions 
        WHERE DATE(created_at) = CURDATE() AND transaction_type = 'deposit'
    """)
    today_deposits = cur.fetchone()['total']
    
    # Recent transactions
    cur.execute("""
        SELECT t.*, a.account_number, c.first_name, c.last_name
        FROM transactions t
        JOIN accounts a ON t.account_id = a.account_id
        JOIN customers c ON a.customer_id = c.customer_id
        ORDER BY t.created_at DESC
        LIMIT 10
    """)
    recent_transactions = cur.fetchall()
    
    # Pending loan applications
    cur.execute("""
        SELECT l.*, c.first_name, c.last_name, c.email
        FROM loans l
        JOIN customers c ON l.customer_id = c.customer_id
        WHERE l.status = 'pending'
        ORDER BY l.created_at DESC
        LIMIT 5
    """)
    loan_applications = cur.fetchall()
    
    cur.close()
    
    return render_template('admin/dashboard.html',
                         total_customers=total_customers,
                         total_accounts=total_accounts,
                         total_balance=total_balance,
                         pending_loans=pending_loans,
                         today_transactions=today_transactions,
                         today_deposits=today_deposits,
                         recent_transactions=recent_transactions,
                         loan_applications=loan_applications)


@admin_bp.route('/customers')
@login_required
@admin_required
def customers():
    """View and manage customers"""
    search = request.args.get('search', '').strip()
    
    cur = mysql.connection.cursor()
    
    if search:
        cur.execute("""
            SELECT c.*, 
                   (SELECT COUNT(*) FROM accounts a WHERE a.customer_id = c.customer_id) as account_count,
                   (SELECT COALESCE(SUM(balance), 0) FROM accounts a WHERE a.customer_id = c.customer_id) as total_balance
            FROM customers c
            WHERE c.first_name LIKE %s OR c.last_name LIKE %s 
                  OR c.email LIKE %s OR c.phone LIKE %s
            ORDER BY c.created_at DESC
        """, (f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%'))
    else:
        cur.execute("""
            SELECT c.*, 
                   (SELECT COUNT(*) FROM accounts a WHERE a.customer_id = c.customer_id) as account_count,
                   (SELECT COALESCE(SUM(balance), 0) FROM accounts a WHERE a.customer_id = c.customer_id) as total_balance
            FROM customers c
            ORDER BY c.created_at DESC
        """)
    
    customers_list = cur.fetchall()
    cur.close()
    
    return render_template('admin/customers.html', customers=customers_list, search=search)


@admin_bp.route('/customers/<int:customer_id>')
@login_required
@admin_required
def customer_detail(customer_id):
    """View customer details"""
    customer = Customer.get_by_id(customer_id)
    if not customer:
        flash('Customer not found.', 'error')
        return redirect(url_for('admin.customers'))
    
    accounts = Account.get_by_customer(customer_id)
    loans = Loan.get_by_customer(customer_id)
    
    return render_template('admin/customer_detail.html',
                         customer=customer,
                         accounts=accounts,
                         loans=loans)


@admin_bp.route('/accounts')
@login_required
@admin_required
def accounts():
    """View all accounts"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT a.*, c.first_name, c.last_name, c.email, c.phone
        FROM accounts a
        JOIN customers c ON a.customer_id = c.customer_id
        ORDER BY a.created_at DESC
    """)
    accounts_list = cur.fetchall()
    cur.close()
    
    return render_template('admin/accounts.html', accounts=accounts_list)


@admin_bp.route('/accounts/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_account():
    """Create new bank account for customer"""
    if request.method == 'POST':
        customer_id = request.form.get('customer_id', type=int)
        account_type = request.form.get('account_type')
        initial_deposit = request.form.get('initial_deposit', type=float, default=0)
        
        if not customer_id or not account_type:
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('admin.create_account'))
        
        # Verify customer exists
        customer = Customer.get_by_id(customer_id)
        if not customer:
            flash('Customer not found.', 'error')
            return redirect(url_for('admin.create_account'))
        
        account_id, account_number = Account.create(
            customer_id=customer_id,
            account_type=account_type,
            initial_deposit=initial_deposit,
            opened_by=current_user.admin_id
        )
        
        flash(f'Account created successfully! Account Number: {account_number}', 'success')
        return redirect(url_for('admin.accounts'))
    
    # Get customers for dropdown
    cur = mysql.connection.cursor()
    cur.execute("SELECT customer_id, first_name, last_name, email FROM customers WHERE is_active = TRUE ORDER BY first_name")
    customers_list = cur.fetchall()
    cur.close()
    
    return render_template('admin/create_account.html', customers=customers_list)


@admin_bp.route('/loans')
@login_required
@admin_required
def loans():
    """View and manage loans"""
    status_filter = request.args.get('status', '')
    loans_list = Loan.get_all(status_filter if status_filter else None)
    
    return render_template('admin/loans.html', loans=loans_list, status_filter=status_filter)


@admin_bp.route('/loans/<int:loan_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_loan(loan_id):
    """Approve a loan application"""
    Loan.update_status(loan_id, 'approved', current_user.admin_id)
    flash('Loan approved successfully!', 'success')
    return redirect(url_for('admin.loans'))


@admin_bp.route('/loans/<int:loan_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_loan(loan_id):
    """Reject a loan application"""
    Loan.update_status(loan_id, 'rejected')
    flash('Loan rejected.', 'info')
    return redirect(url_for('admin.loans'))


@admin_bp.route('/loans/<int:loan_id>/disburse', methods=['POST'])
@login_required
@admin_required
def disburse_loan(loan_id):
    """Disburse an approved loan"""
    Loan.update_status(loan_id, 'disbursed')
    flash('Loan disbursed successfully!', 'success')
    return redirect(url_for('admin.loans'))


@admin_bp.route('/transactions')
@login_required
@admin_required
def transactions():
    """View all transactions"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT t.*, a.account_number, c.first_name, c.last_name
        FROM transactions t
        JOIN accounts a ON t.account_id = a.account_id
        JOIN customers c ON a.customer_id = c.customer_id
        ORDER BY t.created_at DESC
        LIMIT 100
    """)
    transactions_list = cur.fetchall()
    cur.close()
    
    return render_template('admin/transactions.html', transactions=transactions_list)


@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    """Generate reports"""
    cur = mysql.connection.cursor()
    
    # Daily transaction summary
    cur.execute("""
        SELECT DATE(created_at) as date,
               transaction_type,
               COUNT(*) as count,
               SUM(amount) as total
        FROM transactions
        WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        GROUP BY DATE(created_at), transaction_type
        ORDER BY date DESC, transaction_type
    """)
    daily_summary = cur.fetchall()
    
    # Monthly summary
    cur.execute("SELECT * FROM vw_monthly_report LIMIT 12")
    monthly_summary = cur.fetchall()
    
    # Account type distribution
    cur.execute("""
        SELECT account_type, COUNT(*) as count, SUM(balance) as total_balance
        FROM accounts WHERE status = 'active'
        GROUP BY account_type
    """)
    account_distribution = cur.fetchall()
    
    # Loan summary
    cur.execute("""
        SELECT loan_type, status, COUNT(*) as count, SUM(amount) as total_amount
        FROM loans
        GROUP BY loan_type, status
        ORDER BY loan_type, status
    """)
    loan_summary = cur.fetchall()
    
    cur.close()
    
    return render_template('admin/reports.html',
                         daily_summary=daily_summary,
                         monthly_summary=monthly_summary,
                         account_distribution=account_distribution,
                         loan_summary=loan_summary)
