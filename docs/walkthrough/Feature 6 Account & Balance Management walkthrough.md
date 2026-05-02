# Feature 6: Account & Balance Management Walkthrough

This feature enables masjids to manage multiple financial accounts (Cash, Bank, Mobile Banking) and track their balances in real-time. It also supports transferring funds between accounts.

## Key Changes

### 1. Database Models
- **Account**: Stores account details like name, type, bank info, and opening balance.
- **AccountTransfer**: Records movement of funds between two accounts.
- **Income/Expense Links**: Updated `Income` and `Expense` models to include an `account_id` foreign key.

### 2. API Endpoints
- `GET /api/v1/accounts/`: List all accounts for a masjid.
- `POST /api/v1/accounts/`: Create a new financial account.
- `GET /api/v1/accounts/{id}/balance`: Calculate the current balance of an account.
- `POST /api/v1/accounts/transfer`: Record a fund transfer between accounts.

### 3. Balance Calculation Logic
The balance is calculated dynamically:
`Current Balance = Opening Balance + Total Income - Total Expenses - Total Transfers Out + Total Transfers In`

---

## Verification Results

### Automated Tests
I have implemented comprehensive API tests in `tests/api/test_feature_6_accounts.py`.
The tests cover:
- Account creation and listing.
- Complex balance calculation involving income, expenses, and transfers.
- fund transfers between accounts.

**Test Execution Output:**
```
tests/api/test_feature_6_accounts.py ....                    [100%]
================== 4 passed, 10 warnings in 0.49s ==================
```

### Data Seeding
A dedicated seeder `src/db/seed_feature_6.py` has been created to populate the system with sample data.
**Seeder Output:**
```
Cash Balance: 1080.0 (Expected: 1000 + 500 - 20 - 400 = 1080)
Bank Balance: 5600.0 (Expected: 5000 + 200 + 400 = 5600)
```

---

## Alignment with Requirements
- ✅ **4.6.1 Account Concept**: Supported (Cash, Bank, Mobile Banking).
- ✅ **4.6.2 Account Fields**: All required fields implemented in `Account` model.
- ✅ **4.6.3 Balance Operations**: Implemented dynamic calculation and transfers.
- ✅ **Security**: RBAC enforced on all endpoints; masjid isolation maintained via `masjid_id`.
