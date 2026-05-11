
---

## 12. Viva Questions and Answers

### File: `docs/viva_questions.md`

### Database Concepts

**Q1: What is the difference between a Primary Key and a Foreign Key?**

A **Primary Key** uniquely identifies each record in a table. It cannot be NULL and must be unique. Example: `customer_id` in the customers table.

A **Foreign Key** is a field that references the primary key of another table, establishing a relationship between tables. Example: `customer_id` in the accounts table references `customer_id` in the customers table.

---

**Q2: Explain the normalization forms used in this database.**

The database follows **Third Normal Form (3NF)**:

- **1NF**: All columns contain atomic values (no arrays or lists)
- **2NF**: No partial dependencies (all non-key attributes depend on the entire primary key)
- **3NF**: No transitive dependencies (non-key attributes don't depend on other non-key attributes)

Example: Customer address details (city, state, pincode) are stored in the customers table, not in a separate table, as they fully depend on customer_id.

---

**Q3: What are stored procedures and why are they used?**

Stored procedures are precompiled SQL code stored in the database. Benefits:

- **Performance**: Compiled once, executed many times
- **Security**: Users can execute without direct table access
- **Maintainability**: Business logic centralized in database
- **Atomic Operations**: Multiple statements in a single transaction

Example: `sp_transfer` procedure handles the complete fund transfer logic atomically.

---

**Q4: Explain ACID properties with examples from this system.**

- **Atomicity**: A fund transfer either completes fully (debit + credit) or not at all
- **Consistency**: Balance cannot go below minimum_balance constraint
- **Isolation**: Concurrent transactions don't interfere (using `FOR UPDATE` locks)
- **Durability**: Once committed, transactions survive system crashes

---

**Q5: What are triggers? Give an example.**

Triggers are automatic actions executed when specified events occur.

Example: `before_account_insert` trigger automatically generates a unique account number before inserting a new account:

```sql
CREATE TRIGGER before_account_insert
BEFORE INSERT ON accounts
FOR EACH ROW
BEGIN
    SET NEW.account_number = CONCAT('ACC', LPAD(FLOOR(RAND() * 10000000000), 10, '0'));
END

Q6: What is a View? How is it different from a Table?

A View is a virtual table based on a SELECT query. It doesn't store data physically.

Differences:

Tables store actual data; views store queries
Views always show current data from underlying tables
Views can simplify complex joins
Views can provide row-level security
Example: vw_customer_account_summary combines customer and account data.

Q7: Explain the indexing strategy in this database.

Indexes improve query performance. We've indexed:

Primary Keys: Automatically indexed (customer_id, account_id, etc.)
Foreign Keys: For faster joins (customer_id in accounts)
Frequently Searched Columns: email, phone, account_number
Date Columns: created_at for date-range queries
Trade-off: Indexes speed up reads but slow down writes.

Application Architecture
Q8: What is the Flask Blueprint pattern?

Blueprints organize Flask applications into modular components:

python


auth_bp = Blueprint('auth', __name__)
customer_bp = Blueprint('customer', __name__, url_prefix='/customer')
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
Benefits:

Code organization by feature
Reusable components
Separate URL prefixes
Independent testing
Q9: How is password security implemented?

We use Werkzeug's generate_password_hash and check_password_hash:

PBKDF2-SHA256 algorithm
Automatic salting (random salt per password)
600,000 iterations (computationally expensive)
Passwords are never stored in plain text.

Q10: Explain CSRF protection in this application.

Cross-Site Request Forgery protection ensures requests originate from our forms:

Flask-WTF generates unique tokens
Tokens embedded in forms: <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
Server validates token on POST requests
Invalid/missing tokens are rejected
Q11: How does Flask-Login manage user sessions?

Flask-Login provides:

@login_required decorator for protected routes
current_user proxy for accessing logged-in user
Session management with secure cookies
"Remember me" functionality
Custom get_id() returns 'customer_1' or 'admin_1' format to distinguish user types.

Q12: What is the MVC pattern? How does this project implement it?

Model-View-Controller separates concerns:

Model: models.py - Database interactions
View: Templates (templates/) - HTML presentation
Controller: Routes (routes/) - Business logic
This separation makes code maintainable and testable.

Security Questions
Q13: How do you prevent SQL Injection?

Using parameterized queries:

python


# WRONG (vulnerable):
query = f"SELECT * FROM users WHERE email = '{email}'"
# CORRECT (safe):
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
The database driver escapes special characters automatically.

Q14: What validations are performed before a withdrawal?

Account exists and belongs to the customer
Account status is 'active'
Amount is positive
Sufficient balance (balance - amount >= minimum_balance)
Amount within transaction limits
All validations occur in the stored procedure for atomicity.

Q15: How do you handle concurrent transactions?

Using database locks:

sql


SELECT balance FROM accounts WHERE account_id = %s FOR UPDATE;
FOR UPDATE locks the row until the transaction completes, preventing race conditions in simultaneous transfers.

Future Enhancements
Q16: What improvements would you suggest?

Two-Factor Authentication: SMS/Email OTP for sensitive operations
Email Notifications: Transaction alerts, loan status updates
Mobile App: React Native or Flutter frontend
Interest Calculation Jobs: Scheduled tasks for interest credit
Audit Dashboard: Visual analytics for admin
PDF Statements: Downloadable account statements
Multi-Currency Support: International transactions
API Rate Limiting: Prevent abuse
Redis Caching: Faster dashboard loading
Docker Deployment: Containerized production setup