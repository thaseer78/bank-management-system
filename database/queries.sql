-- =====================================================
-- COMMON SQL QUERIES FOR BANK MANAGEMENT SYSTEM
-- =====================================================

-- 1. Get all customers with their total balance
SELECT 
    c.customer_id,
    CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
    c.email,
    COUNT(a.account_id) AS total_accounts,
    COALESCE(SUM(a.balance), 0) AS total_balance
FROM customers c
LEFT JOIN accounts a ON c.customer_id = a.customer_id
GROUP BY c.customer_id
ORDER BY total_balance DESC;

-- 2. Get transaction summary for a specific account
SELECT 
    transaction_type,
    COUNT(*) AS transaction_count,
    SUM(amount) AS total_amount,
    MIN(amount) AS min_amount,
    MAX(amount) AS max_amount,
    AVG(amount) AS avg_amount
FROM transactions
WHERE account_id = 1
GROUP BY transaction_type;

-- 3. Get daily transaction report
SELECT 
    DATE(created_at) AS transaction_date,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN transaction_type = 'deposit' THEN amount ELSE 0 END) AS total_deposits,
    SUM(CASE WHEN transaction_type = 'withdrawal' THEN amount ELSE 0 END) AS total_withdrawals
FROM transactions
WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY DATE(created_at)
ORDER BY transaction_date DESC;

-- 4. Get loan statistics by type
SELECT 
    loan_type,
    COUNT(*) AS total_applications,
    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) AS pending,
    SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) AS approved,
    SUM(CASE WHEN status = 'disbursed' THEN 1 ELSE 0 END) AS disbursed,
    SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) AS rejected,
    SUM(amount) AS total_amount_requested,
    AVG(interest_rate) AS avg_interest_rate
FROM loans
GROUP BY loan_type;

-- 5. Find inactive accounts (no transactions in 6 months)
SELECT 
    a.account_number,
    CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
    a.balance,
    MAX(t.created_at) AS last_transaction_date
FROM accounts a
JOIN customers c ON a.customer_id = c.customer_id
LEFT JOIN transactions t ON a.account_id = t.account_id
WHERE a.status = 'active'
GROUP BY a.account_id
HAVING last_transaction_date < DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
    OR last_transaction_date IS NULL;

-- 6. Top 10 customers by balance
SELECT 
    c.customer_id,
    CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
    c.email,
    SUM(a.balance) AS total_balance,
    COUNT(a.account_id) AS account_count
FROM customers c
JOIN accounts a ON c.customer_id = a.customer_id
WHERE a.status = 'active'
GROUP BY c.customer_id
ORDER BY total_balance DESC
LIMIT 10;

-- 7. Monthly transaction growth
SELECT 
    DATE_FORMAT(created_at, '%Y-%m') AS month,
    COUNT(*) AS transaction_count,
    SUM(amount) AS total_volume,
    COUNT(DISTINCT account_id) AS unique_accounts
FROM transactions
GROUP BY DATE_FORMAT(created_at, '%Y-%m')
ORDER BY month DESC;

-- 8. Accounts below minimum balance
SELECT 
    a.account_number,
    CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
    c.phone,
    a.balance,
    a.minimum_balance,
    (a.minimum_balance - a.balance) AS deficit
FROM accounts a
JOIN customers c ON a.customer_id = c.customer_id
WHERE a.balance < a.minimum_balance AND a.status = 'active';

-- 9. Transfer history between accounts
SELECT 
    t.transfer_ref,
    t.amount,
    fa.account_number AS from_account,
    CONCAT(fc.first_name, ' ', fc.last_name) AS from_customer,
    ta.account_number AS to_account,
    CONCAT(tc.first_name, ' ', tc.last_name) AS to_customer,
    t.description,
    t.created_at
FROM transfers t
JOIN accounts fa ON t.from_account_id = fa.account_id
JOIN customers fc ON fa.customer_id = fc.customer_id
JOIN accounts ta ON t.to_account_id = ta.account_id
JOIN customers tc ON ta.customer_id = tc.customer_id
ORDER BY t.created_at DESC
LIMIT 50;

-- 10. Loan EMI schedule (calculated)
SELECT 
    l.loan_ref,
    CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
    l.amount AS principal,
    l.interest_rate,
    l.tenure_months,
    l.emi_amount,
    l.total_payable,
    (l.total_payable - l.amount) AS total_interest,
    l.amount_paid,
    (l.total_payable - l.amount_paid) AS remaining_amount,
    CEIL((l.total_payable - l.amount_paid) / l.emi_amount) AS remaining_emis
FROM loans l
JOIN customers c ON l.customer_id = c.customer_id
WHERE l.status = 'disbursed';
