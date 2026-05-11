"""
Bank Management System - Customer Routes
Handles all customer-facing functionality
"""

from app.models import *
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Account, Transaction, Loan
from app import mysql
from functools import wraps

customer_bp = Blueprint('customer', __name__)


def customer_required(f):
    """Decorator to ensure user is a customer"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_type != 'customer':
            flash('Please login as a customer to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@customer_bp.route('/dashboard')
@login_required
@customer_required
def dashboard():
    """Customer dashboard - overview of accounts and recent activity"""
    accounts = Account.get_by_customer(current_user.customer_id)
    
    # Calculate totals
    total_balance = sum(acc['balance'] for acc in accounts)
    
    # Get recent transactions (last 5)
    recent_transactions = []
    if accounts:
        cur = mysql.connection.cursor()
        account_ids = [acc['account_id'] for acc in accounts]
        placeholders = ','.join(['%s'] * len(account_ids))
        cur.execute(f"""
            SELECT t.*, a.account_number
            FROM transactions t
            JOIN accounts a ON t.account_id = a.account_id
            WHERE t.account_id IN ({placeholders})
            ORDER BY t.created_at DESC
            LIMIT 5
        """, account_ids)
        recent_transactions = cur.fetchall()
        cur.close()
    
    # Get pending loans
    loans = Loan.get_by_customer(current_user.customer_id)
    pending_loans = [l for l in loans if l['status'] in ('pending', 'approved')]
    
    return render_template('customer/dashboard.html',
                         accounts=accounts,
                         total_balance=total_balance,
                         recent_transactions=recent_transactions,
                         pending_loans=pending_loans)


@customer_bp.route('/deposit', methods=['GET', 'POST'])
@login_required
@customer_required
def deposit():
    """Deposit money into account"""
    accounts = Account.get_by_customer(current_user.customer_id)
    accounts = [a for a in accounts if a['status'] == 'active']
    
    if request.method == 'POST':
        account_id = request.form.get('account_id', type=int)
        amount = request.form.get('amount', type=float)
        description = request.form.get('description', 'Cash deposit').strip()
        
        # Validation
        if not account_id or not amount:
            flash('Please select an account and enter an amount.', 'error')
            return render_template('customer/deposit.html', accounts=accounts)
        
        if amount <= 0:
            flash('Amount must be greater than zero.', 'error')
            return render_template('customer/deposit.html', accounts=accounts)
        
        if amount > 1000000:
            flash('Maximum deposit amount is ₹10,00,000 per transaction.', 'error')
            return render_template('customer/deposit.html', accounts=accounts)
        
        # Verify account belongs to customer
        valid_account = any(a['account_id'] == account_id for a in accounts)
        if not valid_account:
            flash('Invalid account selected.', 'error')
            return render_template('customer/deposit.html', accounts=accounts)
        
        # Process deposit
        status, message = Transaction.deposit(account_id, amount, description)
        
        if status == 'success':
            flash(message, 'success')
            return redirect(url_for('customer.dashboard'))
        else:
            flash(message, 'error')
    
    return render_template('customer/deposit.html', accounts=accounts)


@customer_bp.route('/withdraw', methods=['GET', 'POST'])
@login_required
@customer_required
def withdraw():
    """Withdraw money from account"""
    accounts = Account.get_by_customer(current_user.customer_id)
    accounts = [a for a in accounts if a['status'] == 'active' and a['account_type'] != 'fixed_deposit']
    
    if request.method == 'POST':
        account_id = request.form.get('account_id', type=int)
        amount = request.form.get('amount', type=float)
        description = request.form.get('description', 'Cash withdrawal').strip()
        
        if not account_id or not amount:
            flash('Please select an account and enter an amount.', 'error')
            return render_template('customer/withdraw.html', accounts=accounts)
        
        if amount <= 0:
            flash('Amount must be greater than zero.', 'error')
            return render_template('customer/withdraw.html', accounts=accounts)
        
        valid_account = any(a['account_id'] == account_id for a in accounts)
        if not valid_account:
            flash('Invalid account selected.', 'error')
            return render_template('customer/withdraw.html', accounts=accounts)
        
        status, message = Transaction.withdraw(account_id, amount, description)
        
        if status == 'success':
            flash(message, 'success')
            return redirect(url_for('customer.dashboard'))
        else:
            flash(message, 'error')
    
    return render_template('customer/withdraw.html', accounts=accounts)


@customer_bp.route('/transfer', methods=['GET', 'POST'])
@login_required
@customer_required
def transfer():
    """Transfer money between accounts"""
    accounts = Account.get_by_customer(current_user.customer_id)
    accounts = [a for a in accounts if a['status'] == 'active' and a['account_type'] != 'fixed_deposit']
    
    if request.method == 'POST':
        from_account_id = request.form.get('from_account_id', type=int)
        to_account_number = request.form.get('to_account_number', '').strip()
        amount = request.form.get('amount', type=float)
        description = request.form.get('description', 'Fund transfer').strip()
        
        if not all([from_account_id, to_account_number, amount]):
            flash('Please fill in all required fields.', 'error')
            return render_template('customer/transfer.html', accounts=accounts)
        
        if amount <= 0:
            flash('Amount must be greater than zero.', 'error')
            return render_template('customer/transfer.html', accounts=accounts)
        
        if amount > 1000000:
            flash('Maximum transfer amount is ₹10,00,000 per transaction.', 'error')
            return render_template('customer/transfer.html', accounts=accounts)
        
        valid_account = any(a['account_id'] == from_account_id for a in accounts)
        if not valid_account:
            flash('Invalid source account selected.', 'error')
            return render_template('customer/transfer.html', accounts=accounts)
        
        status, message = Transaction.transfer(from_account_id, to_account_number, amount, description)
        
        if status == 'success':
            flash(message, 'success')
            return redirect(url_for('customer.dashboard'))
        else:
            flash(message, 'error')
    
    return render_template('customer/transfer.html', accounts=accounts)


@customer_bp.route('/transactions')
@login_required
@customer_required
def transactions():
    """View transaction history"""
    accounts = Account.get_by_customer(current_user.customer_id)
    
    selected_account = request.args.get('account_id', type=int)
    
    all_transactions = []
    for account in accounts:
        if selected_account and account['account_id'] != selected_account:
            continue
        
        txns = Transaction.get_by_account(account['account_id'])
        for txn in txns:
            txn['account_number'] = account['account_number']
        all_transactions.extend(txns)
    
    # Sort by date descending
    all_transactions.sort(key=lambda x: x['created_at'], reverse=True)
    
    return render_template('customer/transactions.html',
                         accounts=accounts,
                         transactions=all_transactions,
                         selected_account=selected_account)


@customer_bp.route('/loans')
@login_required
@customer_required
def loans():
    """View loans and apply for new loan"""
    customer_loans = Loan.get_by_customer(current_user.customer_id)
    accounts = Account.get_by_customer(current_user.customer_id)
    accounts = [a for a in accounts if a['status'] == 'active']
    
    return render_template('customer/loans.html',
                         loans=customer_loans,
                         accounts=accounts)


@customer_bp.route('/loans/apply', methods=['POST'])
@login_required
@customer_required
def apply_loan():
    """Apply for a new loan"""
    account_id = request.form.get('account_id', type=int)
    loan_type = request.form.get('loan_type')
    amount = request.form.get('amount', type=float)
    tenure = request.form.get('tenure', type=int)
    purpose = request.form.get('purpose', '').strip()
    
    if not all([account_id, loan_type, amount, tenure]):
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('customer.loans'))
    
    # Validate loan type
    valid_types = ['personal', 'home', 'car', 'education', 'business']
    if loan_type not in valid_types:
        flash('Invalid loan type.', 'error')
        return redirect(url_for('customer.loans'))
    
    # Validate amount
    if amount < 10000 or amount > 10000000:
        flash('Loan amount must be between ₹10,000 and ₹1,00,00,000.', 'error')
        return redirect(url_for('customer.loans'))
    
    # Validate tenure
    if tenure < 6 or tenure > 360:
        flash('Tenure must be between 6 and 360 months.', 'error')
        return redirect(url_for('customer.loans'))
    
    # Verify account belongs to customer
    accounts = Account.get_by_customer(current_user.customer_id)
    valid_account = any(a['account_id'] == account_id for a in accounts)
    if not valid_account:
        flash('Invalid account selected.', 'error')
        return redirect(url_for('customer.loans'))
    
    loan_id = Loan.apply(current_user.customer_id, account_id, loan_type, amount, tenure, purpose)
    
    if loan_id:
        flash('Loan application submitted successfully! We will review your application.', 'success')
    else:
        flash('Failed to submit loan application. Please try again.', 'error')
    
    return redirect(url_for('customer.loans'))


@customer_bp.route('/profile')
@login_required
@customer_required
def profile():
    """View and edit customer profile"""
    return render_template('customer/profile.html')


@customer_bp.route('/deposit', methods=['GET','POST'])
@login_required
@customer_required
def update_profile():
    """Update customer profile"""
    address = request.form.get('address', '').strip()
    city = request.form.get('city', '').strip()
    state = request.form.get('state', '').strip()
    pincode = request.form.get('pincode', '').strip()
    phone = request.form.get('phone', '').strip()
    
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE customers
        SET address = %s, city = %s, state = %s, pincode = %s, phone = %s
        WHERE customer_id = %s
    """, (address, city, state, pincode, phone, current_user.customer_id))
    mysql.connection.commit()
    cur.close()
    
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('customer.profile'))
