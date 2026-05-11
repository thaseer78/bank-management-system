from app import mysql
import MySQLdb.cursors
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string
from flask_login import UserMixin
import uuid


# =========================================
# CUSTOMER MODEL
# =========================================
# =========================================
# CUSTOMER MODEL
# =========================================
class Customer(UserMixin):

    def __init__(self, data):
        self.customer_id = data['customer_id']
        self.email = data['email']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.password_hash = data['password_hash']
        self.user_type = 'customer'
        self.is_active = True

    def get_id(self):
        return f"customer_{self.customer_id}"

    @staticmethod
    def get_by_id(customer_id):

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cur.execute("""
            SELECT * FROM customers
            WHERE customer_id = %s
        """, (customer_id,))

        customer = cur.fetchone()

        cur.close()

        return Customer(customer) if customer else None

    @staticmethod
    def get_by_email(email):

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cur.execute("""
            SELECT * FROM customers
            WHERE email = %s
        """, (email,))

        customer = cur.fetchone()

        cur.close()

        return Customer(customer) if customer else None

    @staticmethod
    def verify_password(email, password):

        customer = Customer.get_by_email(email)

        if customer and check_password_hash(customer.password_hash, password):
            return customer

        return None

# =========================================
# ADMIN MODEL
# =========================================
class Admin(UserMixin):

    def __init__(self, data):
        self.admin_id = data['admin_id']
        self.username = data['username']
        self.password_hash = data['password_hash']
        self.full_name = data.get('full_name', '')
        self.user_type = 'admin'
        self.is_active = True

    def get_id(self):
        return f"admin_{self.admin_id}"

    @staticmethod
    def get_by_id(admin_id):

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cur.execute("""
            SELECT * FROM admins
            WHERE admin_id = %s
        """, (admin_id,))

        admin = cur.fetchone()

        cur.close()

        return Admin(admin) if admin else None

    @staticmethod
    def get_by_username(username):

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cur.execute("""
            SELECT * FROM admins
            WHERE username = %s
        """, (username,))

        admin = cur.fetchone()

        cur.close()

        return Admin(admin) if admin else None

    @staticmethod
    def verify_password(username, password):

        admin = Admin.get_by_username(username)

        if admin and check_password_hash(admin.password_hash, password):
            return admin

        return None
    

# =========================================
# ACCOUNT MODEL
# =========================================
class Account:

    @staticmethod
    def get_by_customer(customer_id):

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cur.execute("""
            SELECT * FROM accounts
            WHERE customer_id = %s
        """, (customer_id,))

        accounts = cur.fetchall()

        cur.close()

        return accounts

    @staticmethod
    def create(customer_id,
               account_type,
               initial_deposit=0,
               opened_by=None):

        cur = mysql.connection.cursor()

        account_number = 'ACC' + ''.join(
            random.choices(string.digits, k=6)
        )

        cur.execute("""
            INSERT INTO accounts
            (
                customer_id,
                account_number,
                account_type,
                balance,
                minimum_balance,
                interest_rate,
                status
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            customer_id,
            account_number,
            account_type,
            initial_deposit,
            1000,
            4.0,
            'active'
        ))

        mysql.connection.commit()

        account_id = cur.lastrowid

        cur.close()

        return account_id, account_number


# =========================================
# TRANSACTION MODEL
# =========================================
class Transaction:

    @staticmethod
    def deposit(account_id, amount, description):

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cur.execute("""
            SELECT * FROM accounts
            WHERE account_id = %s
        """, (account_id,))

        account = cur.fetchone()

        if not account:
            cur.close()
            return 'error', 'Account not found'

        new_balance = float(account['balance']) + float(amount)

        cur.execute("""
            UPDATE accounts
            SET balance = %s
            WHERE account_id = %s
        """, (new_balance, account_id))

        transaction_ref = str(uuid.uuid1())

        cur.execute("""
            INSERT INTO transactions
            (
                transaction_ref,
                account_id,
                transaction_type,
                amount,
                balance_before,
                balance_after,
                description,
                status
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            transaction_ref,
            account_id,
            'deposit',
            amount,
            account['balance'],
            new_balance,
            description,
            'completed'
        ))

        mysql.connection.commit()

        cur.close()

        return 'success', 'Deposit successful'

    @staticmethod
    def withdraw(account_id, amount, description):

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cur.execute("""
            SELECT * FROM accounts
            WHERE account_id = %s
        """, (account_id,))

        account = cur.fetchone()

        if not account:
            cur.close()
            return 'error', 'Account not found'

        if float(account['balance']) < float(amount):
            cur.close()
            return 'error', 'Insufficient balance'

        new_balance = float(account['balance']) - float(amount)

        cur.execute("""
            UPDATE accounts
            SET balance = %s
            WHERE account_id = %s
        """, (new_balance, account_id))

        transaction_ref = str(uuid.uuid1())

        cur.execute("""
            INSERT INTO transactions
            (
                transaction_ref,
                account_id,
                transaction_type,
                amount,
                balance_before,
                balance_after,
                description,
                status
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            transaction_ref,
            account_id,
            'withdrawal',
            amount,
            account['balance'],
            new_balance,
            description,
            'completed'
        ))

        mysql.connection.commit()

        cur.close()

        return 'success', 'Withdrawal successful'

    @staticmethod
    def transfer(from_account_id,
                 to_account_number,
                 amount,
                 description):

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cur.execute("""
            SELECT * FROM accounts
            WHERE account_id = %s
        """, (from_account_id,))

        sender = cur.fetchone()

        cur.execute("""
            SELECT * FROM accounts
            WHERE account_number = %s
        """, (to_account_number,))

        receiver = cur.fetchone()

        if not sender or not receiver:
            cur.close()
            return 'error', 'Invalid accounts'

        if float(sender['balance']) < float(amount):
            cur.close()
            return 'error', 'Insufficient balance'

        sender_new = float(sender['balance']) - float(amount)

        receiver_new = float(receiver['balance']) + float(amount)

        cur.execute("""
            UPDATE accounts
            SET balance = %s
            WHERE account_id = %s
        """, (sender_new, sender['account_id']))

        cur.execute("""
            UPDATE accounts
            SET balance = %s
            WHERE account_id = %s
        """, (receiver_new, receiver['account_id']))

        mysql.connection.commit()

        cur.close()

        return 'success', 'Transfer successful'

    @staticmethod
    def get_by_account(account_id):

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cur.execute("""
            SELECT * FROM transactions
            WHERE account_id = %s
            ORDER BY created_at DESC
        """, (account_id,))

        transactions = cur.fetchall()

        cur.close()

        return transactions


# =========================================
# LOAN MODEL
# =========================================
class Loan:

    @staticmethod
    def get_by_customer(customer_id):

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cur.execute("""
            SELECT * FROM loans
            WHERE customer_id = %s
        """, (customer_id,))

        loans = cur.fetchall()

        cur.close()

        return loans

    @staticmethod
    def apply(customer_id,
              account_id,
              loan_type,
              amount,
              tenure,
              purpose):

        cur = mysql.connection.cursor()

        cur.execute("""
            INSERT INTO loans
            (
                customer_id,
                account_id,
                loan_type,
                amount,
                tenure_months,
                purpose,
                status
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            customer_id,
            account_id,
            loan_type,
            amount,
            tenure,
            purpose,
            'pending'
        ))

        mysql.connection.commit()

        loan_id = cur.lastrowid

        cur.close()

        return loan_id

    @staticmethod
    def get_all(status=None):

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if status:

            cur.execute("""
                SELECT * FROM loans
                WHERE status = %s
            """, (status,))

        else:

            cur.execute("""
                SELECT * FROM loans
            """)

        loans = cur.fetchall()

        cur.close()

        return loans

    @staticmethod
    def update_status(loan_id,
                      status,
                      approved_by=None):

        cur = mysql.connection.cursor()

        cur.execute("""
            UPDATE loans
            SET status = %s
            WHERE loan_id = %s
        """, (status, loan_id))

        mysql.connection.commit()

        cur.close()