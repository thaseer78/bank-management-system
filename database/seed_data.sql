USE bank_management_system;

-- Insert Admin Users (Password: admin123 - hashed)
INSERT INTO admins (username, password_hash, full_name, email, role) VALUES
('superadmin', 'pbkdf2:sha256:600000$salt$hash', 'Super Administrator', 'superadmin@bank.com', 'super_admin'),
('manager1', 'pbkdf2:sha256:600000$salt$hash', 'John Manager', 'manager@bank.com', 'manager'),
('clerk1', 'pbkdf2:sha256:600000$salt$hash', 'Jane Clerk', 'clerk@bank.com', 'clerk');

-- Insert Sample Customers (Password: customer123 - will be hashed by application)
INSERT INTO customers (first_name, last_name, email, phone, password_hash, address, city, state, pincode, date_of_birth, gender, id_proof_type, id_proof_number, is_verified) VALUES
('Rahul', 'Sharma', 'rahul@email.com', '9876543210', 'pbkdf2:sha256:600000$salt$hash', '123 Main Street', 'Mumbai', 'Maharashtra', '400001', '1990-05-15', 'male', 'aadhar', '1234-5678-9012', TRUE),
('Priya', 'Patel', 'priya@email.com', '9876543211', 'pbkdf2:sha256:600000$salt$hash', '456 Park Avenue', 'Delhi', 'Delhi', '110001', '1992-08-22', 'female', 'pan', 'ABCDE1234F', TRUE),
('Amit', 'Kumar', 'amit@email.com', '9876543212', 'pbkdf2:sha256:600000$salt$hash', '789 Lake Road', 'Bangalore', 'Karnataka', '560001', '1988-12-10', 'male', 'passport', 'J1234567', TRUE),
('Sneha', 'Reddy', 'sneha@email.com', '9876543213', 'pbkdf2:sha256:600000$salt$hash', '321 Hill View', 'Hyderabad', 'Telangana', '500001', '1995-03-28', 'female', 'driving_license', 'KA01-1234567', TRUE),
('Vikram', 'Singh', 'vikram@email.com', '9876543214', 'pbkdf2:sha256:600000$salt$hash', '654 Garden Lane', 'Chennai', 'Tamil Nadu', '600001', '1991-07-05', 'male', 'aadhar', '9876-5432-1098', TRUE);

-- Insert Sample Accounts
INSERT INTO accounts (account_number, customer_id, account_type, balance, minimum_balance, interest_rate, status, opened_by) VALUES
('ACC1000000001', 1, 'savings', 50000.00, 1000.00, 4.00, 'active', 1),
('ACC1000000002', 1, 'checking', 25000.00, 500.00, 0.00, 'active', 1),
('ACC1000000003', 2, 'savings', 75000.00, 1000.00, 4.00, 'active', 1),
('ACC1000000004', 3, 'savings', 100000.00, 1000.00, 4.00, 'active', 2),
('ACC1000000005', 3, 'fixed_deposit', 200000.00, 0.00, 7.00, 'active', 2),
('ACC1000000006', 4, 'savings', 35000.00, 1000.00, 4.00, 'active', 2),
('ACC1000000007', 5, 'savings', 60000.00, 1000.00, 4.00, 'active', 3);

-- Insert Sample Transactions
INSERT INTO transactions (transaction_ref, account_id, transaction_type, amount, balance_before, balance_after, description, created_at) VALUES
('TXN20240101000001', 1, 'deposit', 10000.00, 40000.00, 50000.00, 'Cash deposit', '2024-01-15 10:30:00'),
('TXN20240101000002', 1, 'withdrawal', 5000.00, 50000.00, 45000.00, 'ATM withdrawal', '2024-01-20 14:15:00'),
('TXN20240101000003', 1, 'deposit', 5000.00, 45000.00, 50000.00, 'Online transfer received', '2024-01-25 09:45:00'),
('TXN20240101000004', 3, 'deposit', 25000.00, 50000.00, 75000.00, 'Salary credit', '2024-01-28 11:00:00'),
('TXN20240101000005', 4, 'deposit', 50000.00, 50000.00, 100000.00, 'Business income', '2024-02-01 16:30:00'),
('TXN20240101000006', 6, 'withdrawal', 10000.00, 45000.00, 35000.00, 'Rent payment', '2024-02-05 12:00:00'),
('TXN20240101000007', 7, 'deposit', 20000.00, 40000.00, 60000.00, 'Freelance payment', '2024-02-10 15:45:00');

-- Insert Sample Transfers
INSERT INTO transfers (transfer_ref, from_account_id, to_account_id, amount, description, created_at) VALUES
('TRF20240101000001', 1, 3, 5000.00, 'Payment for services', '2024-01-22 11:30:00'),
('TRF20240101000002', 4, 6, 10000.00, 'Gift', '2024-02-03 14:00:00'),
('TRF20240101000003', 3, 7, 7500.00, 'Loan repayment', '2024-02-08 09:15:00');

-- Insert Sample Loans
INSERT INTO loans (loan_ref, customer_id, account_id, loan_type, amount, interest_rate, tenure_months, emi_amount, total_payable, status, purpose, approved_by, approved_at) VALUES
('LN20240101000001', 1, 1, 'personal', 100000.00, 12.00, 24, 4707.35, 112976.40, 'disbursed', 'Home renovation', 1, '2024-01-10 10:00:00'),
('LN20240101000002', 3, 4, 'car', 500000.00, 9.50, 60, 10504.79, 630287.40, 'approved', 'New car purchase', 2, '2024-02-01 11:30:00'),
('LN20240101000003', 4, 6, 'education', 200000.00, 8.00, 48, 4889.37, 234689.76, 'pending', 'Higher education abroad', NULL, NULL);

-- Insert Audit Log entries
INSERT INTO audit_log (user_type, user_id, action, table_name, record_id, ip_address) VALUES
('admin', 1, 'LOGIN', NULL, NULL, '192.168.1.1'),
('customer', 1, 'LOGIN', NULL, NULL, '192.168.1.100'),
('admin', 1, 'CREATE_ACCOUNT', 'accounts', 1, '192.168.1.1'),
('customer', 1, 'DEPOSIT', 'transactions', 1, '192.168.1.100'),
('customer', 1, 'TRANSFER', 'transfers', 1, '192.168.1.100');
