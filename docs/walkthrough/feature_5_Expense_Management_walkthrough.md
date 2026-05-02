# Feature Walkthrough: Expense Management (Feature 5)

This document provides a walkthrough of the Expense Management feature implemented in the Masjid Management System.

## Overview

The Expense Management feature allows masjid committee members to record, track, and manage all financial outflows. It supports categorizing expenses, soft deletion for audit purposes, and monthly summary reporting.

## Key Components

### 1. Data Models
- **Expense**: Stores individual expense records including title, amount, date, category, and payment method.
- **RecurringExpenseTemplate**: Allows defining templates for frequent costs (e.g., utility bills).

### 2. API Endpoints
All endpoints are prefix with `/api/v1/expense/`.

| Method | Endpoint | Description | Role Required |
|--------|----------|-------------|---------------|
| POST | `/` | Create a new expense | admin, committee, cashier |
| GET | `/` | List expenses (with filters) | any member |
| GET | `/summary` | Get monthly total summary | any member |
| GET | `/{id}` | Get details of a specific expense | any member |
| PATCH | `/{id}` | Update an expense record | admin, committee, cashier |
| DELETE | `/{id}` | Soft-delete an expense record | admin, super_admin |

### 3. Implementation Details
- **Soft Delete**: Records are never fully removed; they are flagged as `is_deleted` and kept for audit purposes.
- **RBAC**: Strictly enforced using `RoleChecker` and token context.
- **Row-Level Security**: Users can only access data belonging to their masjid (enforced via token `masjid_id`).

## Verification Results

### Automated Tests
Successfully ran 7 API tests covering creation, listing, summary, updates, deletion, and RBAC permissions.
```bash
uv run pytest tests/api/test_expense.py
```
**Results**: `7 passed`.

### Data Seeding
A dedicated seeder is available to populate initial data:
```bash
PYTHONPATH=. uv run python src/db/seed_feature_5.py
```

## Alignment with SRS
- [x] All expense record fields implemented as required (Table 4.5.1).
- [x] Default categories support.
- [x] Create, Read, Update, Delete (Soft) operations.
- [x] Monthly summary reporting (Table 4.8.1).
- [x] Recurring expense template model implemented.
- [x] DB isolation for multi-tenancy.
