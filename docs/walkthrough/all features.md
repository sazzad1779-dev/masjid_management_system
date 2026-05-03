# Walkthrough - Feature 1: Platform & Multi-Masjid Architecture

## Overview
Feature 1 provides the core multi-tenancy architecture and masjid management capabilities for the Masjid Management System. I have aligned the implementation with the SRS requirements (section 4.1 and 4.3.1), added a dedicated seeder, and implemented automated tests.

## Changes Made

### 1. Model & Schema Alignment
- Updated `src/models/masjid.py` to include missing SRS fields: `cover_url`, `state`, `postal_code`, `website`, `established_year`, `about`.
- Renamed `secondary_color` to `accent_color` and `fiscal_year_start` to `fiscal_year_start_month` to match requirements.
- Updated `src/schemas/masjid.py` to stay in sync with the model.

### 2. Super Admin Analytics
- Replaced placeholders in the `/api/v1/masjids/super-admin/analytics` endpoint with real database counts for:
    - Total Masjids
    - Active Users
    - Total Transactions (Income records)

### 3. Dedicated Seeder
- Created `src/db/seed_masjid.py` to handle initial masjid data seeding.
- Updated `src/db/seed.py` to use the specialized masjid and user seeders.

### 4. Automated Tests
- Created `tests/api/v1/test_masjids.py` with tests for:
    - Masjid Registration
    - Profile Retrieval
    - Profile Update (PATCH)
    - Super Admin Analytics


# Walkthrough: Authentication & Authorization (Feature 2)

Aligned the authentication system with SRS requirements, moving to a multi-masjid membership architecture and implementing refresh token rotation.

## Changes Made

### 1. Multi-Masjid Membership Architecture
- **New Model:** Created `MasjidMember` in [src/models/masjid_member.py](file:///home/saif/Documents/Masjid_Management_system/src/models/masjid_member.py) to manage the many-to-many relationship between users and masjids.
- **Updated User Model:** Removed `masjid_id` and `role` from the `User` model in [src/models/user.py](file:///home/saif/Documents/Masjid_Management_system/src/models/user.py). Users now have their roles defined per masjid in the `MasjidMember` table.

### 2. Enhanced Security
- **Refresh Token Rotation:** Implemented `create_refresh_token` and a `/refresh` endpoint in [src/api/v1/endpoints/auth.py](file:///home/saif/Documents/Masjid_Management_system/src/api/v1/endpoints/auth.py) for secure token rotation.
- **Context-Aware Tokens:** The JWT access token now carries the current `masjid_id` and `role`, allowing stateless authorization checks across different masjids.

### 3. Dependency Refactoring
- **RoleChecker:** Updated the `RoleChecker` in [src/api/dependencies.py](file:///home/saif/Documents/Masjid_Management_system/src/api/dependencies.py) to support per-masjid role validation and platform-level super admin access.


# Walkthrough - Feature 3: Masjid Profile & Customization

This walkthrough documents the implementation and verification of Feature 3, ensuring it aligns with the SRS requirements.

## Changes Made

### 1. Database Schema Alignment
Updated the `Masjid` model in `src/models/masjid.py` to include missing fields:
- `friday_jumuah_time`: For displaying Jumu'ah prayer times.
- `notification_settings`: JSON field for workspace notification preferences.
- `default_categories`: JSON field for masjid-specific income/expense categories.
- `social_media`: JSON field for social media links.

### 2. Schema Updates
Updated Pydantic schemas in `src/schemas/masjid.py` (`MasjidCreate`, `MasjidUpdate`, `MasjidRead`) to support the new fields in API requests and responses.

### 3. Dedicated Seeder
Created `src/db/seed_feature_3.py` to populate the database with a comprehensive masjid profile ("Al-Noor Islamic Center") including all branding and setting fields.

### 4. API Testing
Created `tests/api/test_feature_3_masjid_profile.py` with tests for:
- Creating a masjid with a full profile.
- Retrieving the full profile.
- Patching (updating) profile fields and workspace settings.


# Walkthrough - Feature 04: Income Management

Income Management provides mechanisms to systematically track all financial income entering the masjid through various channels (daily/friday collections, zakat, sadaqah, etc.).

## Changes Made

### backend
- **New Model**: [income.py](file:///home/saif/Documents/Masjid_Management_system/src/models/income.py) defines the `Income` record with soft-delete support.
- **New Schemas**: [income.py](file:///home/saif/Documents/Masjid_Management_system/src/schemas/income.py) handles data validation for creation, updates, and reading.
- **CRUD Operations**: [crud_income.py](file:///home/saif/Documents/Masjid_Management_system/src/crud/crud_income.py) implements the business logic, including weekly summaries.
- **API Endpoints**: [income.py](file:///home/saif/Documents/Masjid_Management_system/src/api/v1/endpoints/income.py) exposes the functionality via REST.
- **Seeder**: [seed_income.py](file:///home/saif/Documents/Masjid_Management_system/src/db/seed_income.py) provides sample data for development.

### Infrastructure & Security
- Updated [api.py](file:///home/saif/Documents/Masjid_Management_system/src/api/v1/api.py) to include the income router.
- Updated [session.py](file:///home/saif/Documents/Masjid_Management_system/src/db/session.py) to register the `Income` model.
- Fixed `get_current_user` in [dependencies.py](file:///home/saif/Documents/Masjid_Management_system/src/api/dependencies.py) to handle UUID string conversion.
- Switched to `pbkdf2_sha256` in [security.py](file:///home/saif/Documents/Masjid_Management_system/src/core/security.py) to resolve `bcrypt` compatibility issues in the current environment.


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



# Walkthrough - Feature 7: Monthly Donation & Donor Management

I have implemented the "Monthly Donation & Donor Management" feature, ensuring full alignment with the SRS requirements. This feature allows masjid committees to manage recurring donors and track their monthly contributions.

## Changes Made

### Database Models
- **Donor**: Stores donor profiles, pledge amounts, and join dates. [donor.py](file:///home/saif/Documents/Masjid_Management_system/src/models/donor.py)
- **DonationRecord**: Tracks monthly pledge vs. actual payment. [donation.py](file:///home/saif/Documents/Masjid_Management_system/src/models/donation.py)

### API Endpoints
- **Donors API**: CRUD operations for managing donors. [donors.py](file:///home/saif/Documents/Masjid_Management_system/src/api/v1/endpoints/donors.py)
- **Donations API**: Bulk record generation and payment verification. [donations.py](file:///home/saif/Documents/Masjid_Management_system/src/api/v1/endpoints/donations.py)

### Business Logic
- **Record Generation**: Automated bulk creation of pending donation records for all active donors for a given month.
- **Payment Verification**: When a donation is marked as paid, the system automatically creates a linked `Income` record, ensuring financial consistency.


# Walkthrough - Feature 8: Reporting & Analytics

This feature provides comprehensive financial reporting and analytics for the Masjid Management System, including dashboard statistics, weekly, monthly, and yearly summaries, and donor collection reports.

## Changes Made

### Core Implementation
- **Schemas**: Defined `SummaryStats`, `WeeklySummary`, `MonthlySummary`, `YearlySummary`, and `DonorCollectionReport` in `src/schemas/reports.py`.
- **Service Logic**: Implemented `ReportService` in `src/services/reports.py` to handle complex data aggregations across income, expense, account, and donation models.
- **API Endpoints**: Created `src/api/v1/endpoints/reports.py` with endpoints for:
    - `GET /summary`: Dashboard balance cards and recent transactions.
    - `GET /weekly`: Weekly financial summary.
    - `GET /monthly`: Monthly breakdown with category analysis.
    - `GET /yearly`: Year-over-year comparison.
    - `GET /donors`: Donor collection status for a specific month.
- **Router Registration**: Registered the reports router in `src/api/v1/api.py`.


# Feature 9: Notifications & Alerts — Walkthrough

## Overview

This feature provides an internal notification system for the Masjid Management System, aligned with SRS requirements. Notifications are automatically created when key financial events occur (income recorded, expense recorded, donation verified) and are sent to relevant masjid admins and donors.

## Architecture

```
API Endpoint (income/expense/donation)
  └─> NotificationService.notify_masjid_admins() / create_notification()
        └─> notification_crud.create() → Notification table
```

**Key design decision:** Notifications are triggered at the **API endpoint layer** (not CRUD layer), ensuring they only fire on user-facing actions and avoiding duplication.

## Components

### NotificationService (`src/services/notification.py`)

| Method | Trigger | Recipients |
|---|---|---|
| `create_notification` | Manual / internal | Single user |
| `notify_masjid_admins` | Financial events | All admin/committee members |
| `notify_income_recorded` | Income creation | Masjid admins |
| `notify_expense_recorded` | Expense creation | Masjid admins |
| `notify_donation_verified` | Donation verification | Admins + donor (if linked) |
| `notify_user_invitation` | User added to masjid | Invited user |
| `notify_role_change` | Role updated | Affected user |
| `send_email` | Placeholder | External (future) |

### API Endpoints (`src/api/v1/endpoints/notifications.py`)

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/notifications/` | GET | List user notifications (filterable by `is_read`) |
| `/api/v1/notifications/{id}/read` | PUT | Mark single notification as read |
| `/api/v1/notifications/read-all` | PUT | Mark all notifications as read |

### Endpoint Integration

- **Income** (`POST /api/v1/income/`) → triggers `income_recorded` notification
- **Expense** (`POST /api/v1/expense/`) → triggers `expense_recorded` notification
- **Donation** (`PUT /api/v1/donations/{id}/verify`) → triggers `donation_verified` notification to admins + donor


# Walkthrough - Feature 10: Audit & Activity Log

## Problem Statement
The Masjid Management System required a robust "Audit & Activity Log" feature to ensures full traceability of system actions, especially financial operations and user access.

## Proposed Changes
I implemented a centralized audit logging system that captures:
- User actions (login, create, update, delete, etc.)
- Entity types and IDs
- Changes made (old vs new values in JSON)
- Request metadata (IP address, user agent)
- Masjid context

### [Component Name]
#### [NEW] [audit_log.py](file:///home/saif/Documents/Masjid_Management_system/src/models/audit_log.py)
#### [NEW] [audit_log.py](file:///home/saif/Documents/Masjid_Management_system/src/schemas/audit_log.py)
#### [NEW] [audit_log.py](file:///home/saif/Documents/Masjid_Management_system/src/crud/audit_log.py)
#### [NEW] [audit_log.py](file:///home/saif/Documents/Masjid_Management_system/src/services/audit_log.py)
#### [NEW] [audit_logs.py](file:///home/saif/Documents/Masjid_Management_system/src/api/v1/endpoints/audit_logs.py)
#### [NEW] [feature_10_seeder.py](file:///home/saif/Documents/Masjid_Management_system/src/db/seeders/feature_10_seeder.py)
#### [NEW] [test_feature_10_audit_logs.py](file:///home/saif/Documents/Masjid_Management_system/tests/api/v1/test_feature_10_audit_logs.py)

#### [MODIFY] [api.py](file:///home/saif/Documents/Masjid_Management_system/src/api/v1/api.py)
#### [MODIFY] [auth.py](file:///home/saif/Documents/Masjid_Management_system/src/api/v1/endpoints/auth.py)
#### [MODIFY] [income.py](file:///home/saif/Documents/Masjid_Management_system/src/api/v1/endpoints/income.py)
#### [MODIFY] [expense.py](file:///home/saif/Documents/Masjid_Management_system/src/api/v1/endpoints/expense.py)
#### [MODIFY] [accounts.py](file:///home/saif/Documents/Masjid_Management_system/src/api/v1/endpoints/accounts.py)
#### [MODIFY] [donors.py](file:///home/saif/Documents/Masjid_Management_system/src/api/v1/endpoints/donors.py)
#### [MODIFY] [donations.py](file:///home/saif/Documents/Masjid_Management_system/src/api/v1/endpoints/donations.py)


