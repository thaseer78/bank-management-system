"""
Bank Management System - API Routes
RESTful API endpoints for external integration
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import Account, Transaction, Loan
from app import mysql

api_bp = Blueprint('api', __name__)


@api_bp.route('/balance/<int:account_id>')
@login_required
def get_balance(account_id):
    """Get account balance"""
    account = Account.get_by_id(account_id)
    
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    
    # Verify ownership for customers
    if current_user.user_type == 'customer':
        if account['customer_id'] != current_user.customer_id:
            return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'account_number': account['account_number'],
        'account_type': account['account_type'],
        'balance': float(account['balance']),
        'status': account['status']
    })


@api_bp.route('/validate-account/<account_number>')
@login_required
def validate_account(account_number):
    """Validate if account exists and get basic info"""
    account = Account.get_by_account_number(account_number)
    
    if not account:
        return jsonify({'valid': False, 'message': 'Account not found'})
    
    if account['status'] != 'active':
        return jsonify({'valid': False, 'message': 'Account is not active'})
    
    return jsonify({
        'valid': True,
        'account_holder': f"{account['first_name']} {account['last_name'][0]}.",
        'account_type': account['account_type']
    })


@api_bp.route('/transactions/<int:account_id>')
@login_required
def get_transactions(account_id):
    """Get transaction history"""
    # Verify ownership for customers
    if current_user.user_type == 'customer':
        account = Account.get_by_id(account_id)
        if not account or account['customer_id'] != current_user.customer_id:
            return jsonify({'error': 'Unauthorized'}), 403
    
    transactions = Transaction.get_by_account(account_id)
    
    return jsonify({
        'transactions': [{
            'ref': t['transaction_ref'],
            'type': t['transaction_type'],
            'amount': float(t['amount']),
            'balance_after': float(t['balance_after']),
            'description': t['description'],
            'date': t['created_at'].isoformat()
        } for t in transactions]
    })


@api_bp.route('/loan-emi', methods=['POST'])
@login_required
def calculate_emi():
    """Calculate loan EMI"""
    data = request.get_json()
    
    principal = data.get('principal', 0)
    rate = data.get('rate', 0)
    tenure = data.get('tenure', 0)
    
    if not all([principal, rate, tenure]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    emi, total = Loan.calculate_emi(principal, rate, tenure)
    
    return jsonify({
        'emi': emi,
        'total_payable': total,
        'total_interest': round(total - principal, 2)
    })


@api_bp.route('/dashboard-stats')
@login_required
def dashboard_stats():
    """Get dashboard statistics for admin"""
    if current_user.user_type != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    cur = mysql.connection.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM customers WHERE is_active = TRUE")
    customers = cur.fetchone()['count']
    
    cur.execute("SELECT COUNT(*) as count FROM accounts WHERE status = 'active'")
    accounts = cur.fetchone()['count']
    
    cur.execute("SELECT COALESCE(SUM(balance), 0) as total FROM accounts")
    total_balance = float(cur.fetchone()['total'])
    
    cur.execute("SELECT COUNT(*) as count FROM loans WHERE status = 'pending'")
    pending_loans = cur.fetchone()['count']
    
    cur.close()
    
    return jsonify({
        'customers': customers,
        'accounts': accounts,
        'total_balance': total_balance,
        'pending_loans': pending_loans
    })
