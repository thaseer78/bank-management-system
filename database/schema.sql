-- Bank Management System Database Schema
-- Created for College DBMS Project

-- Create database
CREATE DATABASE IF NOT EXISTS bank_management_system;
USE bank_management_system;

-- =====================================================
-- TABLE: admins
-- Stores administrator information for system management
-- =====================================================
CREATE TABLE admins (
    admin_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role ENUM('super_admin', 'manager', 'clerk') DEFAULT 'clerk',
    is_active BOOLEAN DEFAULT TRUE,
    last_login DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =====================================================
-- TABLE: customers
-- Stores customer personal and authentication information
-- =====================================================
CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    address TEXT,
    city VARCHAR(50),
    state VARCHAR(50),
    pincode VARCHAR(10),
    date_of_birth DATE,
    gender ENUM('male', 'female', 'other'),
    id_proof_type ENUM('aadhar', 'pan', 'passport', 'driving_license'),
    id_proof_number VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_email (email),
    INDEX idx_phone (phone)
);

-- =====================================================
-- TABLE: accounts
-- Stores bank account information
-- =====================================================
CREATE TABLE accounts (
    account_id INT PRIMARY KEY AUTO_INCREMENT,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    customer_id INT NOT NULL,
    account_type ENUM('savings', 'checking', 'fixed_deposit') NOT NULL,
    balance DECIMAL(15, 2) DEFAULT 0.00,
    minimum_balance DECIMAL(15, 2) DEFAULT 1000.00,
    interest_rate DECIMAL(5, 2) DEFAULT 4.00,
    status ENUM('active', 'inactive', 'frozen', 'closed') DEFAULT 'active',
    opened_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (opened_by) REFERENCES admins(admin_id) ON DELETE SET NULL,
    INDEX idx_account_number (account_number),
    INDEX idx_customer (customer_id)
);

-- =====================================================
-- TABLE: transactions
-- Stores all transaction records
-- =====================================================
CREATE TABLE transactions (
    transaction_id INT PRIMARY KEY AUTO_INCREMENT,
    transaction_ref VARCHAR(30) UNIQUE NOT NULL,
    account_id INT NOT NULL,
    transaction_type ENUM('deposit', 'withdrawal', 'transfer_in', 'transfer_out', 'interest', 'fee', 'loan_disbursement', 'loan_payment') NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    balance_before DECIMAL(15, 2) NOT NULL,
    balance_after DECIMAL(15, 2) NOT NULL,
    description TEXT,
    status ENUM('pending', 'completed', 'failed', 'reversed') DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE,
    INDEX idx_account (account_id),
    INDEX idx_transaction_ref (transaction_ref),
    INDEX idx_created_at (created_at)
);

-- =====================================================
-- TABLE: transfers
-- Stores money transfer records between accounts
-- =====================================================
CREATE TABLE transfers (
    transfer_id INT PRIMARY KEY AUTO_INCREMENT,
    transfer_ref VARCHAR(30) UNIQUE NOT NULL,
    from_account_id INT NOT NULL,
    to_account_id INT NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    description VARCHAR(255),
    status ENUM('pending', 'completed', 'failed', 'reversed') DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (from_account_id) REFERENCES accounts(account_id) ON DELETE CASCADE,
    FOREIGN KEY (to_account_id) REFERENCES accounts(account_id) ON DELETE CASCADE,
    INDEX idx_from_account (from_account_id),
    INDEX idx_to_account (to_account_id)
);

-- =====================================================
-- TABLE: loans
-- Stores loan applications and details
-- =====================================================
CREATE TABLE loans (
    loan_id INT PRIMARY KEY AUTO_INCREMENT,
    loan_ref VARCHAR(30) UNIQUE NOT NULL,
    customer_id INT NOT NULL,
    account_id INT NOT NULL,
    loan_type ENUM('personal', 'home', 'car', 'education', 'business') NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    interest_rate DECIMAL(5, 2) NOT NULL,
    tenure_months INT NOT NULL,
    emi_amount DECIMAL(15, 2),
    total_payable DECIMAL(15, 2),
    amount_paid DECIMAL(15, 2) DEFAULT 0.00,
    status ENUM('pending', 'approved', 'rejected', 'disbursed', 'closed') DEFAULT 'pending',
    purpose TEXT,
    approved_by INT,
    approved_at DATETIME,
    disbursed_at DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES admins(admin_id) ON DELETE SET NULL,
    INDEX idx_customer (customer_id),
    INDEX idx_status (status)
);

-- =====================================================
-- TABLE: loan_payments
-- Stores loan EMI payment records
-- =====================================================
CREATE TABLE loan_payments (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    loan_id INT NOT NULL,
    payment_ref VARCHAR(30) UNIQUE NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    principal_amount DECIMAL(15, 2) NOT NULL,
    interest_amount DECIMAL(15, 2) NOT NULL,
    payment_date DATE NOT NULL,
    status ENUM('pending', 'paid', 'overdue') DEFAULT 'pending',
    paid_at DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (loan_id) REFERENCES loans(loan_id) ON DELETE CASCADE,
    INDEX idx_loan (loan_id),
    INDEX idx_payment_date (payment_date)
);

-- =====================================================
-- TABLE: audit_log
-- Stores system audit trail for security
-- =====================================================
CREATE TABLE audit_log (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    user_type ENUM('admin', 'customer') NOT NULL,
    user_id INT NOT NULL,
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(50),
    record_id INT,
    old_values JSON,
    new_values JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_user (user_type, user_id),
    INDEX idx_action (action),
    INDEX idx_created_at (created_at)
);

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger to generate unique account number
DELIMITER //
CREATE TRIGGER before_account_insert
BEFORE INSERT ON accounts
FOR EACH ROW
BEGIN
    IF NEW.account_number IS NULL OR NEW.account_number = '' THEN
        SET NEW.account_number = CONCAT('ACC', LPAD(FLOOR(RAND() * 10000000000), 10, '0'));
    END IF;
END//
DELIMITER ;

-- Trigger to generate unique transaction reference
DELIMITER //
CREATE TRIGGER before_transaction_insert
BEFORE INSERT ON transactions
FOR EACH ROW
BEGIN
    IF NEW.transaction_ref IS NULL OR NEW.transaction_ref = '' THEN
        SET NEW.transaction_ref = CONCAT('TXN', DATE_FORMAT(NOW(), '%Y%m%d'), LPAD(FLOOR(RAND() * 1000000), 6, '0'));
    END IF;
END//
DELIMITER ;

-- Trigger to generate unique transfer reference
DELIMITER //
CREATE TRIGGER before_transfer_insert
BEFORE INSERT ON transfers
FOR EACH ROW
BEGIN
    IF NEW.transfer_ref IS NULL OR NEW.transfer_ref = '' THEN
        SET NEW.transfer_ref = CONCAT('TRF', DATE_FORMAT(NOW(), '%Y%m%d'), LPAD(FLOOR(RAND() * 1000000), 6, '0'));
    END IF;
END//
DELIMITER ;

-- Trigger to generate unique loan reference
DELIMITER //
CREATE TRIGGER before_loan_insert
BEFORE INSERT ON loans
FOR EACH ROW
BEGIN
    IF NEW.loan_ref IS NULL OR NEW.loan_ref = '' THEN
        SET NEW.loan_ref = CONCAT('LN', DATE_FORMAT(NOW(), '%Y%m%d'), LPAD(FLOOR(RAND() * 1000000), 6, '0'));
    END IF;
END//
DELIMITER ;

-- =====================================================
-- STORED PROCEDURES
-- =====================================================

-- Procedure: Deposit Money
DELIMITER //
CREATE PROCEDURE sp_deposit(
    IN p_account_id INT,
    IN p_amount DECIMAL(15, 2),
    IN p_description VARCHAR(255),
    OUT p_status VARCHAR(50),
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE v_current_balance DECIMAL(15, 2);
    DECLARE v_new_balance DECIMAL(15, 2);
    DECLARE v_account_status VARCHAR(20);
    
    -- Start transaction
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_status = 'error';
        SET p_message = 'Transaction failed due to database error';
    END;
    
    START TRANSACTION;
    
    -- Check account exists and is active
    SELECT balance, status INTO v_current_balance, v_account_status
    FROM accounts WHERE account_id = p_account_id FOR UPDATE;
    
    IF v_account_status IS NULL THEN
        SET p_status = 'error';
        SET p_message = 'Account not found';
        ROLLBACK;
    ELSEIF v_account_status != 'active' THEN
        SET p_status = 'error';
        SET p_message = 'Account is not active';
        ROLLBACK;
    ELSEIF p_amount <= 0 THEN
        SET p_status = 'error';
        SET p_message = 'Amount must be greater than zero';
        ROLLBACK;
    ELSE
        SET v_new_balance = v_current_balance + p_amount;
        
        -- Update account balance
        UPDATE accounts SET balance = v_new_balance WHERE account_id = p_account_id;
        
        -- Insert transaction record
        INSERT INTO transactions (account_id, transaction_type, amount, balance_before, balance_after, description)
        VALUES (p_account_id, 'deposit', p_amount, v_current_balance, v_new_balance, p_description);
        
        COMMIT;
        SET p_status = 'success';
        SET p_message = CONCAT('Deposit successful. New balance: ', v_new_balance);
    END IF;
END//
DELIMITER ;

-- Procedure: Withdraw Money
DELIMITER //
CREATE PROCEDURE sp_withdraw(
    IN p_account_id INT,
    IN p_amount DECIMAL(15, 2),
    IN p_description VARCHAR(255),
    OUT p_status VARCHAR(50),
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE v_current_balance DECIMAL(15, 2);
    DECLARE v_min_balance DECIMAL(15, 2);
    DECLARE v_new_balance DECIMAL(15, 2);
    DECLARE v_account_status VARCHAR(20);
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_status = 'error';
        SET p_message = 'Transaction failed due to database error';
    END;
    
    START TRANSACTION;
    
    SELECT balance, minimum_balance, status INTO v_current_balance, v_min_balance, v_account_status
    FROM accounts WHERE account_id = p_account_id FOR UPDATE;
    
    IF v_account_status IS NULL THEN
        SET p_status = 'error';
        SET p_message = 'Account not found';
        ROLLBACK;
    ELSEIF v_account_status != 'active' THEN
        SET p_status = 'error';
        SET p_message = 'Account is not active';
        ROLLBACK;
    ELSEIF p_amount <= 0 THEN
        SET p_status = 'error';
        SET p_message = 'Amount must be greater than zero';
        ROLLBACK;
    ELSEIF (v_current_balance - p_amount) < v_min_balance THEN
        SET p_status = 'error';
        SET p_message = CONCAT('Insufficient balance. Minimum balance required: ', v_min_balance);
        ROLLBACK;
    ELSE
        SET v_new_balance = v_current_balance - p_amount;
        
        UPDATE accounts SET balance = v_new_balance WHERE account_id = p_account_id;
        
        INSERT INTO transactions (account_id, transaction_type, amount, balance_before, balance_after, description)
        VALUES (p_account_id, 'withdrawal', p_amount, v_current_balance, v_new_balance, p_description);
        
        COMMIT;
        SET p_status = 'success';
        SET p_message = CONCAT('Withdrawal successful. New balance: ', v_new_balance);
    END IF;
END//
DELIMITER ;

-- Procedure: Transfer Money
DELIMITER //
CREATE PROCEDURE sp_transfer(
    IN p_from_account_id INT,
    IN p_to_account_number VARCHAR(20),
    IN p_amount DECIMAL(15, 2),
    IN p_description VARCHAR(255),
    OUT p_status VARCHAR(50),
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE v_from_balance DECIMAL(15, 2);
    DECLARE v_from_min_balance DECIMAL(15, 2);
    DECLARE v_from_status VARCHAR(20);
    DECLARE v_to_account_id INT;
    DECLARE v_to_balance DECIMAL(15, 2);
    DECLARE v_to_status VARCHAR(20);
    DECLARE v_from_new_balance DECIMAL(15, 2);
    DECLARE v_to_new_balance DECIMAL(15, 2);
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_status = 'error';
        SET p_message = 'Transfer failed due to database error';
    END;
    
    START TRANSACTION;
    
    -- Get from account details
    SELECT balance, minimum_balance, status INTO v_from_balance, v_from_min_balance, v_from_status
    FROM accounts WHERE account_id = p_from_account_id FOR UPDATE;
    
    -- Get to account details
    SELECT account_id, balance, status INTO v_to_account_id, v_to_balance, v_to_status
    FROM accounts WHERE account_number = p_to_account_number FOR UPDATE;
    
    IF v_from_status IS NULL THEN
        SET p_status = 'error';
        SET p_message = 'Source account not found';
        ROLLBACK;
    ELSEIF v_to_account_id IS NULL THEN
        SET p_status = 'error';
        SET p_message = 'Destination account not found';
        ROLLBACK;
    ELSEIF p_from_account_id = v_to_account_id THEN
        SET p_status = 'error';
        SET p_message = 'Cannot transfer to same account';
        ROLLBACK;
    ELSEIF v_from_status != 'active' THEN
        SET p_status = 'error';
        SET p_message = 'Source account is not active';
        ROLLBACK;
    ELSEIF v_to_status != 'active' THEN
        SET p_status = 'error';
        SET p_message = 'Destination account is not active';
        ROLLBACK;
    ELSEIF p_amount <= 0 THEN
        SET p_status = 'error';
        SET p_message = 'Amount must be greater than zero';
        ROLLBACK;
    ELSEIF (v_from_balance - p_amount) < v_from_min_balance THEN
        SET p_status = 'error';
        SET p_message = CONCAT('Insufficient balance. Minimum balance required: ', v_from_min_balance);
        ROLLBACK;
    ELSE
        SET v_from_new_balance = v_from_balance - p_amount;
        SET v_to_new_balance = v_to_balance + p_amount;
        
        -- Update balances
        UPDATE accounts SET balance = v_from_new_balance WHERE account_id = p_from_account_id;
        UPDATE accounts SET balance = v_to_new_balance WHERE account_id = v_to_account_id;
        
        -- Insert transfer record
        INSERT INTO transfers (from_account_id, to_account_id, amount, description)
        VALUES (p_from_account_id, v_to_account_id, p_amount, p_description);
        
        -- Insert transaction records for both accounts
        INSERT INTO transactions (account_id, transaction_type, amount, balance_before, balance_after, description)
        VALUES (p_from_account_id, 'transfer_out', p_amount, v_from_balance, v_from_new_balance, CONCAT('Transfer to ', p_to_account_number, ': ', IFNULL(p_description, '')));
        
        INSERT INTO transactions (account_id, transaction_type, amount, balance_before, balance_after, description)
        VALUES (v_to_account_id, 'transfer_in', p_amount, v_to_balance, v_to_new_balance, CONCAT('Transfer from account: ', IFNULL(p_description, '')));
        
        COMMIT;
        SET p_status = 'success';
        SET p_message = CONCAT('Transfer successful. New balance: ', v_from_new_balance);
    END IF;
END//
DELIMITER ;

-- Procedure: Calculate Loan EMI
DELIMITER //
CREATE PROCEDURE sp_calculate_emi(
    IN p_principal DECIMAL(15, 2),
    IN p_rate DECIMAL(5, 2),
    IN p_tenure_months INT,
    OUT p_emi DECIMAL(15, 2),
    OUT p_total_payable DECIMAL(15, 2)
)
BEGIN
    DECLARE v_monthly_rate DECIMAL(10, 8);
    
    -- Convert annual rate to monthly
    SET v_monthly_rate = p_rate / 12 / 100;
    
    -- EMI Formula: P * r * (1+r)^n / ((1+r)^n - 1)
    IF v_monthly_rate > 0 THEN
        SET p_emi = p_principal * v_monthly_rate * POW(1 + v_monthly_rate, p_tenure_months) 
                    / (POW(1 + v_monthly_rate, p_tenure_months) - 1);
    ELSE
        SET p_emi = p_principal / p_tenure_months;
    END IF;
    
    SET p_emi = ROUND(p_emi, 2);
    SET p_total_payable = ROUND(p_emi * p_tenure_months, 2);
END//
DELIMITER ;

-- =====================================================
-- VIEWS
-- =====================================================

-- View: Customer Account Summary
CREATE VIEW vw_customer_account_summary AS
SELECT 
    c.customer_id,
    CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
    c.email,
    c.phone,
    a.account_id,
    a.account_number,
    a.account_type,
    a.balance,
    a.status AS account_status,
    (SELECT COUNT(*) FROM transactions t WHERE t.account_id = a.account_id) AS total_transactions,
    (SELECT COALESCE(SUM(amount), 0) FROM transactions t WHERE t.account_id = a.account_id AND t.transaction_type = 'deposit') AS total_deposits,
    (SELECT COALESCE(SUM(amount), 0) FROM transactions t WHERE t.account_id = a.account_id AND t.transaction_type = 'withdrawal') AS total_withdrawals
FROM customers c
JOIN accounts a ON c.customer_id = a.customer_id;

-- View: Loan Summary
CREATE VIEW vw_loan_summary AS
SELECT 
    l.loan_id,
    l.loan_ref,
    CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
    c.email,
    l.loan_type,
    l.amount AS loan_amount,
    l.interest_rate,
    l.tenure_months,
    l.emi_amount,
    l.total_payable,
    l.amount_paid,
    (l.total_payable - l.amount_paid) AS outstanding_amount,
    l.status,
    CONCAT(a.full_name) AS approved_by_name,
    l.created_at,
    l.approved_at
FROM loans l
JOIN customers c ON l.customer_id = c.customer_id
LEFT JOIN admins a ON l.approved_by = a.admin_id;

-- View: Daily Transaction Report
CREATE VIEW vw_daily_transactions AS
SELECT 
    DATE(created_at) AS transaction_date,
    transaction_type,
    COUNT(*) AS transaction_count,
    SUM(amount) AS total_amount,
    AVG(amount) AS average_amount
FROM transactions
GROUP BY DATE(created_at), transaction_type
ORDER BY transaction_date DESC, transaction_type;

-- View: Monthly Revenue Report
CREATE VIEW vw_monthly_report AS
SELECT 
    DATE_FORMAT(created_at, '%Y-%m') AS month,
    SUM(CASE WHEN transaction_type = 'deposit' THEN amount ELSE 0 END) AS total_deposits,
    SUM(CASE WHEN transaction_type = 'withdrawal' THEN amount ELSE 0 END) AS total_withdrawals,
    SUM(CASE WHEN transaction_type IN ('transfer_in', 'transfer_out') THEN amount ELSE 0 END) / 2 AS total_transfers,
    COUNT(DISTINCT account_id) AS active_accounts,
    COUNT(*) AS total_transactions
FROM transactions
GROUP BY DATE_FORMAT(created_at, '%Y-%m')
ORDER BY month DESC;
