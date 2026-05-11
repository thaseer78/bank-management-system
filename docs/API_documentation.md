# Bank Management System - API Documentation

## Base URL
`[localhost](http://localhost:5000/api)`

## Authentication
All API endpoints require authentication via session cookie. Login through the web interface first.

---

## Endpoints

### 1. Get Account Balance

**Endpoint:** `GET /api/balance/<account_id>`

**Response:**
```json
{
    "account_number": "ACC1000000001",
    "account_type": "savings",
    "balance": 50000.00,
    "status": "active"
}
2. Validate Account
Endpoint: GET /api/validate-account/<account_number>

Response (Success):

json


{
    "valid": true,
    "account_holder": "Rahul S.",
    "account_type": "savings"
}
Response (Failure):

json


{
    "valid": false,
    "message": "Account not found"
}
3. Get Transactions
Endpoint: GET /api/transactions/<account_id>

Response:

json


{
    "transactions": [
        {
            "ref": "TXN20240101000001",
            "type": "deposit",
            "amount": 10000.00,
            "balance_after": 50000.00,
            "description": "Cash deposit",
            "date": "2024-01-15T10:30:00"
        }
    ]
}
4. Calculate Loan EMI
Endpoint: POST /api/loan-emi

Request Body:

json


{
    "principal": 100000,
    "rate": 12,
    "tenure": 24
}
Response:

json


{
    "emi": 4707.35,
    "total_payable": 112976.40,
    "total_interest": 12976.40
}
5. Dashboard Statistics (Admin Only)
Endpoint: GET /api/dashboard-stats

Response:

json


{
    "customers": 150,
    "accounts": 245,
    "total_balance": 25000000.00,
    "pending_loans": 12
}
