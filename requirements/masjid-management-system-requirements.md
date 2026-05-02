# Masjid Management System (MMS)
### Software Requirements Specification (SRS)
**Version:** 1.0.0  
**Date:** May 2026  
**Status:** Draft — Ready for Development

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Overview](#2-system-overview)
3. [Stakeholders & User Roles](#3-stakeholders--user-roles)
4. [Functional Requirements](#4-functional-requirements)
   - 4.1 [Platform & Multi-Masjid Architecture](#41-platform--multi-masjid-architecture)
   - 4.2 [Authentication & Authorization](#42-authentication--authorization)
   - 4.3 [Masjid Profile & Customization](#43-masjid-profile--customization)
   - 4.4 [Income Management](#44-income-management)
   - 4.5 [Expense Management](#45-expense-management)
   - 4.6 [Account & Balance Management](#46-account--balance-management)
   - 4.7 [Monthly Donation & Donor Management](#47-monthly-donation--donor-management)
   - 4.8 [Reporting & Analytics](#48-reporting--analytics)
   - 4.9 [Notifications & Alerts](#49-notifications--alerts)
   - 4.10 [Audit & Activity Log](#410-audit--activity-log)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [System Architecture](#6-system-architecture)
7. [Database Schema Design](#7-database-schema-design)
8. [API Design Overview](#8-api-design-overview)
9. [UI/UX Requirements](#9-uiux-requirements)
10. [Security Requirements](#10-security-requirements)
11. [Technology Stack Recommendation](#11-technology-stack-recommendation)
12. [Development Phases & Task Breakdown](#12-development-phases--task-breakdown)
13. [Acceptance Criteria](#13-acceptance-criteria)
14. [Glossary](#14-glossary)

---

## 1. Executive Summary

The **Masjid Management System (MMS)** is a multi-tenant, web-based platform designed to help masjid (mosque) committees digitally manage their financial operations. Each masjid operates as an independent tenant with its own branded interface, user accounts, and financial data.

The platform covers:
- Income and expense tracking
- Account balance management
- Monthly recurring donor management with payment verification
- Weekly and monthly cost summaries
- Role-based access for committee members
- Reports and dashboards for transparency

The system is designed so that **any masjid committee** can self-register, configure their masjid profile, and immediately begin managing their finances — without needing technical expertise.

---

## 2. System Overview

### 2.1 Problem Statement

Most masjids today manage their finances through paper registers, spreadsheets, or general-purpose tools that are not built for Islamic community financial workflows. This leads to:
- Lack of transparency for donors
- No easy way to verify monthly donations
- Difficulty generating periodic reports for the committee
- No centralized oversight across multiple masjids in an organization

### 2.2 Solution

A SaaS-style multi-tenant platform where:
- Each masjid gets its own isolated workspace (subdomain or tenant ID)
- Committee admins manage finances and member access
- Monthly donors can log in to verify their donation history
- Financial summaries are generated automatically (weekly, monthly, yearly)

### 2.3 Scope

**In Scope:**
- Multi-masjid multi-tenant platform
- Financial management (income, expense, accounts)
- Monthly donor tracking and verification
- Role-based access control
- Custom branding per masjid
- Reporting and dashboards
- Notification system (email/SMS)
- Audit trail

**Out of Scope (v1.0):**
- Online payment gateway integration (can be added in v2)
- Mobile native app (PWA is sufficient for v1)
- Payroll or HR management
- Inventory management

---

## 3. Stakeholders & User Roles

### 3.1 Roles

| Role | Description | Scope |
|------|-------------|-------|
| **Super Admin** | Platform owner (MMS platform team) | All masjids |
| **Masjid Admin** | Committee member who registered the masjid | Single masjid |
| **Committee Member** | Staff with limited access assigned by Admin | Single masjid |
| **Cashier / Accountant** | Can record income/expense but cannot manage users | Single masjid |
| **Monthly Donor** | Registered donor who can view their own donation records | Single masjid |
| **Public Viewer** | Anonymous viewer of public financial summary (if enabled) | Single masjid |

### 3.2 Role Permission Matrix

| Feature | Super Admin | Masjid Admin | Committee Member | Cashier | Monthly Donor |
|---------|:-----------:|:------------:|:----------------:|:-------:|:-------------:|
| Register masjid | ✅ | ✅ | ❌ | ❌ | ❌ |
| Manage masjid settings | ✅ | ✅ | ❌ | ❌ | ❌ |
| Add/remove committee members | ✅ | ✅ | ❌ | ❌ | ❌ |
| Add/edit income records | ✅ | ✅ | ✅ | ✅ | ❌ |
| Add/edit expense records | ✅ | ✅ | ✅ | ✅ | ❌ |
| Delete financial records | ✅ | ✅ | ❌ | ❌ | ❌ |
| Manage donors | ✅ | ✅ | ✅ | ❌ | ❌ |
| View own donation history | ✅ | ✅ | ✅ | ✅ | ✅ |
| Verify donations | ✅ | ✅ | ✅ | ❌ | ❌ |
| View reports | ✅ | ✅ | ✅ | ✅ | ❌ |
| View all masjids | ✅ | ❌ | ❌ | ❌ | ❌ |
| Platform settings | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## 4. Functional Requirements

---

### 4.1 Platform & Multi-Masjid Architecture

#### 4.1.1 Multi-Tenancy
- The system MUST support multiple masjids as isolated tenants.
- Each masjid's data MUST be fully isolated from other masjids.
- Tenant isolation MUST be enforced at the database query level (row-level security or schema-per-tenant).
- Each masjid MUST be identified by a unique `masjid_id` and optionally a unique slug (e.g., `mms.app/masjid/al-noor`).

#### 4.1.2 Masjid Registration
- Any user can register a new masjid on the platform.
- Upon registration, the registering user automatically becomes the **Masjid Admin**.
- Registration requires: Masjid name, address, city, country, contact email, and optionally a logo.
- After registration, a unique masjid workspace is created.
- Email verification MUST be required before the masjid workspace becomes active.

#### 4.1.3 Super Admin Panel
- Super Admin can view a list of all registered masjids with their status (active/inactive/suspended).
- Super Admin can deactivate or delete a masjid tenant.
- Super Admin can view platform-level analytics (total masjids, total transactions, active users).
- Super Admin can impersonate a masjid admin for support purposes (with audit log entry).

---

### 4.2 Authentication & Authorization

#### 4.2.1 Authentication
- Email + password-based authentication.
- Support for password reset via email OTP.
- Optional: Google OAuth login.
- JWT-based session tokens with configurable expiry (default 7 days).
- Refresh token rotation for session security.
- A user can be a member of multiple masjids with different roles in each.

#### 4.2.2 Authorization
- Role-Based Access Control (RBAC) enforced on every API endpoint.
- Frontend routes MUST be protected and redirect unauthorized users.
- All permission checks MUST be done server-side; frontend guards are supplementary only.

#### 4.2.3 Donor Account Access
- Monthly donors are invited via email by the Masjid Admin.
- Donors receive an invitation link to set up their password.
- Donor accounts are scoped to the specific masjid that invited them.
- Donors can only view their own donation records — not the general financials.

---

### 4.3 Masjid Profile & Customization

#### 4.3.1 Masjid Profile Fields
- Masjid name (required)
- Logo / profile image (upload, max 2MB, PNG/JPG)
- Cover photo / banner image
- Address (street, city, state, country, postal code)
- Contact phone number
- Contact email
- Website URL (optional)
- Established year (optional)
- About / description (rich text, optional)
- Primary currency (e.g., BDT, USD, GBP) — used across all financial records
- Financial year start month (default: January)
- Friday Jumu'ah time (display only)
- Social media links (optional)

#### 4.3.2 Custom Branding
- Each masjid MUST have a customizable primary color and accent color for their workspace UI.
- The masjid logo MUST appear in the navigation/header of the masjid's workspace.
- Masjid name MUST appear as the page/tab title within the workspace.
- Optional: custom subdomain support (e.g., `alnoor.mms.app`) — Phase 2.

#### 4.3.3 Workspace Settings
- Toggle public financial summary page (on/off).
- Set fiscal/financial year start.
- Configure notification preferences (email, SMS).
- Set default expense and income categories.

---

### 4.4 Income Management

#### 4.4.1 Income Record Fields
Every income record MUST capture:

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `title` | String | Yes | Short description (e.g., "Friday Collection") |
| `amount` | Decimal | Yes | Must be > 0 |
| `currency` | String | Yes | Auto-filled from masjid settings |
| `income_date` | Date | Yes | Date the income was received |
| `category` | Enum/String | Yes | See categories below |
| `source` | String | No | Who/where it came from |
| `payment_method` | Enum | Yes | Cash, Bank Transfer, Mobile Banking, Cheque, Other |
| `reference_number` | String | No | Bank ref, transaction ID, etc. |
| `notes` | Text | No | Additional context |
| `receipt_attachment` | File | No | PDF/image of receipt, max 5MB |
| `recorded_by` | FK User | Auto | The user who created the record |
| `created_at` | Timestamp | Auto | |
| `updated_at` | Timestamp | Auto | |

#### 4.4.2 Income Categories (Default, Editable)
- Friday Jumu'ah Collection
- Daily Prayer Collection
- Eid Collection (Eid ul-Fitr / Eid ul-Adha)
- Zakat
- Sadaqah / Voluntary Donation
- Monthly Donation (linked to donor records)
- Event / Program Income
- Rental Income
- Grant / Aid
- Other

#### 4.4.3 Income Operations
- **Create** income record (with optional file attachment).
- **Edit** income record (only Admin or the recorder within 24 hours; Admin anytime).
- **Delete** income record (Admin only, with reason required).
- **Search & Filter** by date range, category, payment method, amount range, source.
- **Sort** by date, amount, category.
- **Paginate** results (default 20 per page).
- **Export** filtered income records to CSV or PDF.
- **Bulk import** via CSV template (Admin only).

#### 4.4.4 Special Income — Weekly Collection Tracking
- The system MUST auto-aggregate and display total income per week.
- Weekly collection should be viewable in a dedicated weekly view by selecting the week.
- Jumu'ah collections should be automatically tagged to the corresponding Friday date.

---

### 4.5 Expense Management

#### 4.5.1 Expense Record Fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `title` | String | Yes | Short description |
| `amount` | Decimal | Yes | Must be > 0 |
| `currency` | String | Yes | Auto-filled from masjid settings |
| `expense_date` | Date | Yes | |
| `category` | Enum/String | Yes | See categories below |
| `vendor` | String | No | Who was paid |
| `payment_method` | Enum | Yes | Cash, Bank Transfer, Mobile Banking, Cheque, Other |
| `reference_number` | String | No | |
| `is_recurring` | Boolean | No | Flags if this is a fixed monthly cost |
| `recurring_frequency` | Enum | Conditional | Monthly, Weekly, Yearly |
| `notes` | Text | No | |
| `receipt_attachment` | File | No | Max 5MB |
| `approved_by` | FK User | No | Optional approval workflow |
| `recorded_by` | FK User | Auto | |
| `created_at` | Timestamp | Auto | |

#### 4.5.2 Expense Categories (Default, Editable)
- Utility Bills (Electricity, Gas, Water)
- Internet / Phone
- Imam / Staff Salary
- Cleaning & Maintenance
- Building Repair
- Education / Madrasa
- Event / Program Cost
- Stationary & Office
- Security
- Food & Hospitality
- Zakat Distribution
- Charity / Aid Given
- Loan Repayment
- Other

#### 4.5.3 Expense Operations
- **Create**, **Edit**, **Delete** (same rules as income).
- **Recurring expense** — mark an expense as recurring; system auto-reminds to record it each period.
- **Search & Filter** by date range, category, vendor, payment method, amount range, is_recurring.
- **Export** to CSV or PDF.
- **Monthly cost summary** — auto-aggregate all expenses for a calendar month.
- **Weekly cost summary** — auto-aggregate all expenses for a selected week.

#### 4.5.4 Recurring Expense Templates
- Admin can define a recurring expense template (e.g., monthly electricity bill ~5,000 BDT).
- Each period, the system creates a reminder notification.
- When the admin records the actual payment, it links back to the template.
- Templates can be paused or deleted.

---

### 4.6 Account & Balance Management

#### 4.6.1 Account Concept
- A masjid can have one or more **financial accounts** (e.g., Cash Box, Bank Account, Mobile Banking).
- Each income/expense record is associated with an account.
- Each account maintains a real-time running balance.

#### 4.6.2 Account Fields

| Field | Type | Required |
|-------|------|----------|
| `account_name` | String | Yes |
| `account_type` | Enum | Yes | Cash, Bank, Mobile Banking, Other |
| `bank_name` | String | Conditional | Required if type = Bank |
| `account_number` | String | Conditional | Required if type = Bank |
| `opening_balance` | Decimal | Yes | Starting balance when account was created |
| `opening_date` | Date | Yes | |
| `is_active` | Boolean | Auto | |
| `notes` | Text | No | |

#### 4.6.3 Balance Operations
- **Current Balance** = Opening Balance + Total Income − Total Expenses (for that account).
- **Balance as of any date** — query balance at any historical point in time.
- **Total Balance** = sum of all active account balances.
- **Transfer between accounts** — record a transfer (reduces one account, increases another, net zero effect on total).
- **Account reconciliation** — admin can mark a reconciliation date with a confirmed balance.

#### 4.6.4 Dashboard Balance Summary
- Total current balance (all accounts combined).
- Per-account balance breakdown.
- Monthly net (income − expenses).
- Year-to-date net.
- Quick stats: This week's income, this week's expenses, this month's income, this month's expenses.

---

### 4.7 Monthly Donation & Donor Management

#### 4.7.1 Donor Profile

| Field | Type | Required |
|-------|------|----------|
| `full_name` | String | Yes |
| `phone` | String | Yes |
| `email` | String | No | Used for account invitation |
| `address` | String | No | |
| `monthly_pledge_amount` | Decimal | Yes | Committed monthly donation |
| `pledge_currency` | String | Yes | |
| `pledge_start_date` | Date | Yes | |
| `pledge_end_date` | Date | No | |
| `payment_method` | Enum | Yes | How they usually pay |
| `notes` | String | No | |
| `has_account` | Boolean | Auto | True if invited and registered |
| `is_active` | Boolean | Yes | |

#### 4.7.2 Donation Records (Monthly)
Each month, a donation record is expected per active donor.

| Field | Type | Required |
|-------|------|----------|
| `donor_id` | FK | Yes |
| `month` | String (YYYY-MM) | Yes |
| `pledged_amount` | Decimal | Auto | Copied from donor profile |
| `paid_amount` | Decimal | No | Actual amount received |
| `payment_date` | Date | No | When payment was received |
| `payment_method` | Enum | No | |
| `reference_number` | String | No | |
| `status` | Enum | Auto | Pending, Paid, Partial, Missed |
| `verified_by` | FK User | No | Committee member who verified |
| `verification_note` | Text | No | |
| `receipt_attachment` | File | No | |

#### 4.7.3 Donation Tracking Operations
- Admin can **generate donation records** for all active donors for any given month (bulk create with status = Pending).
- Admin or committee member can **mark a donation as Paid** and enter the actual amount received.
- If paid amount < pledged amount, status = **Partial**.
- If end of month and no payment, status auto-updates to **Missed**.
- **Donor dashboard** (donor login): Donor can see their own monthly donation history, status, and confirmation receipts.
- **Donation verification** — committee member records payment proof; donor can see the verified status in their portal.
- Admin can **send payment reminders** to donors via email/SMS (manual trigger).
- **Donor list view** — shows all donors, their pledge, current month status, total donated YTD.
- **Export donor report** to CSV/PDF.

#### 4.7.4 Donor Account (Self-Service Portal)
- Donors with email on record can be invited to create a login.
- Donor portal shows:
  - Their name and pledge info.
  - A table of all months since joining: month, pledged amount, paid amount, status, payment date.
  - Any committee notes/verification.
  - A printable/downloadable receipt for any verified month.

---

### 4.8 Reporting & Analytics

#### 4.8.1 Standard Reports

| Report | Description |
|--------|-------------|
| **Daily Summary** | Total income and expenses for a selected day |
| **Weekly Summary** | Income, expenses, net balance for a selected week |
| **Monthly Summary** | Full breakdown by category for a selected month |
| **Yearly Summary** | Month-by-month income vs expense comparison for a year |
| **Income by Category** | Pie/bar chart and table of income grouped by category for a period |
| **Expense by Category** | Pie/bar chart and table of expenses grouped by category for a period |
| **Account Statement** | Full transaction history for a specific account, any date range |
| **Donor Report** | All donors, their pledges, paid amounts, missed months for a period |
| **Monthly Donation Collection** | For a selected month: all donors and their payment status |
| **Recurring Expense Report** | All recurring expenses and whether they were recorded each period |

#### 4.8.2 Dashboard Widgets
- **Balance Card** — total balance across all accounts.
- **This Month Income** vs **This Month Expenses** (progress bars or cards).
- **Monthly Comparison Chart** — last 6 months income vs expenses (bar chart).
- **Recent Transactions** — last 10 income/expense entries.
- **Pending Donations** — count of donors with pending payment this month.
- **Upcoming Recurring Expenses** — next 30 days.
- **Category Breakdown** — current month expenses by category (donut chart).

#### 4.8.3 Export & Print
- All reports MUST be exportable as **PDF** and **CSV**.
- PDF exports MUST include the masjid name, logo, date range, and generation date in the header.
- Reports MUST be printable from the browser (print-friendly CSS).

---

### 4.9 Notifications & Alerts

#### 4.9.1 In-App Notifications
- New income/expense recorded (for admin/committee).
- Donation payment received and verified.
- Donor's payment is overdue (after 5th of the month).
- Recurring expense reminder (3 days before due).
- Low balance alert (admin configures threshold).
- New committee member added.

#### 4.9.2 Email Notifications
- Welcome email on masjid registration.
- Donor invitation email (with signup link).
- Monthly donation reminder email to donors (configurable: sent on 1st of each month).
- Payment confirmation/receipt email to donor after verification.
- Password reset email.
- Weekly financial summary email to admin (optional, toggleable).
- Monthly financial summary email to admin (optional, toggleable).

#### 4.9.3 SMS Notifications (Optional, Phase 2)
- Donor payment reminder SMS.
- Donation received confirmation SMS.
- Low balance alert SMS to admin.

---

### 4.10 Audit & Activity Log

- Every create, update, and delete action on financial records MUST be logged.
- Every login and logout MUST be logged with IP and user agent.
- Every role change (user added/removed/role updated) MUST be logged.
- Audit log entries MUST include: `user_id`, `user_name`, `action`, `entity_type`, `entity_id`, `old_value` (JSON), `new_value` (JSON), `timestamp`, `ip_address`.
- Admin can view the audit log filtered by user, date range, action type, entity type.
- Audit logs are **read-only** — they cannot be deleted or modified by anyone.
- Super Admin can view audit logs across all masjids.

---

## 5. Non-Functional Requirements

### 5.1 Performance
- Dashboard and list pages MUST load within **2 seconds** on a standard broadband connection.
- Report generation for up to 12 months of data MUST complete within **5 seconds**.
- The system MUST support at least **500 concurrent masjid workspaces** in v1.
- Database queries for financial summaries MUST use indexed fields and aggregation queries — not application-level loops.

### 5.2 Scalability
- The architecture MUST be horizontally scalable (stateless API servers behind a load balancer).
- Database MUST support read replicas for reporting queries.
- File attachments MUST be stored in cloud object storage (S3 or equivalent), not on the server filesystem.

### 5.3 Availability
- Target uptime: **99.5%** (allows ~44 hours downtime/year).
- Scheduled maintenance MUST be announced 24 hours in advance via in-app banner.

### 5.4 Data Integrity
- All monetary amounts MUST be stored as `DECIMAL(15, 2)` — never as floating point.
- Currency MUST be stored with every financial record — do not rely on masjid-level currency alone.
- All financial records MUST be soft-deleted (flagged as deleted, not removed from the database).
- Deleted records MUST still appear in audit logs and must not affect historical balance calculations.

### 5.5 Accessibility
- The UI MUST meet **WCAG 2.1 Level AA** accessibility standards.
- The system MUST support **RTL (Right-to-Left)** layout for Arabic, Urdu, and other RTL languages (Phase 2).
- The system MUST be fully usable on mobile browsers (responsive design, not just desktop).

### 5.6 Localization
- All user-facing currency amounts MUST be formatted according to the masjid's configured locale.
- Date formats MUST be configurable (DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD).
- The system MUST support multiple languages in Phase 2 (Bengali, Arabic, Urdu, English at minimum).

### 5.7 Backup & Recovery
- Database backups MUST run daily with 30-day retention.
- Point-in-time recovery MUST be available for the last 7 days.
- File attachments in object storage MUST have versioning enabled.

---

## 6. System Architecture

### 6.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                        │
│  Web Browser (React PWA) — responsive, mobile-first    │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTPS
┌───────────────────────▼─────────────────────────────────┐
│                   API GATEWAY / REVERSE PROXY           │
│              (Nginx / Caddy — handles SSL, routing)     │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│                  BACKEND API LAYER                      │
│          REST API (Node.js / Express or Fastify)        │
│      JWT Auth Middleware — RBAC Middleware              │
│      Masjid Tenant Context Middleware                   │
└──────────┬─────────────────────────────┬────────────────┘
           │                             │
┌──────────▼──────────┐       ┌──────────▼──────────────┐
│   PRIMARY DATABASE  │       │    BACKGROUND JOBS       │
│  PostgreSQL (RDS)   │       │  (Bull Queue / Redis)    │
│  Row-Level Security │       │  Email, SMS, Reports     │
└─────────────────────┘       └──────────────────────────┘
           │
┌──────────▼──────────┐       ┌─────────────────────────┐
│   OBJECT STORAGE    │       │   EMAIL SERVICE          │
│  AWS S3 / Cloudflare│       │   (SendGrid / Resend)    │
│  R2 (file uploads)  │       └─────────────────────────┘
└─────────────────────┘
```

### 6.2 Multi-Tenancy Strategy
- **Approach:** Single database with `masjid_id` column on every tenant-scoped table (shared schema, row-level isolation).
- Every API route that accesses tenant data MUST extract `masjid_id` from the authenticated user's JWT and apply it as a mandatory filter.
- A middleware layer MUST inject `masjid_id` into every database query context automatically.
- This approach is chosen for simplicity in v1; schema-per-tenant can be migrated to in v2 if needed.

### 6.3 File Storage Strategy
- Uploaded files (receipts, logos) are stored in **cloud object storage**.
- Files are organized by: `/{masjid_id}/{entity_type}/{year}/{month}/{uuid}.{ext}`
- Signed URLs (time-limited, e.g., 1 hour) are generated per-request — files are never publicly accessible by default.
- File size limits: Images (2MB), Documents/Receipts (5MB).

---

## 7. Database Schema Design

### 7.1 Core Tables

#### `platforms` (Super Admin config)
```
id, name, settings_json, created_at
```

#### `masjids`
```
id (UUID), name, slug (unique), logo_url, cover_url,
address, city, state, country, postal_code,
phone, email, website, established_year, about,
currency, fiscal_year_start_month,
primary_color, accent_color,
is_public_summary_enabled, is_active, is_verified,
created_at, updated_at
```

#### `users`
```
id (UUID), full_name, email (unique), password_hash,
is_email_verified, last_login_at, is_active,
created_at, updated_at
```

#### `masjid_members` (join table — user belongs to masjid with a role)
```
id, masjid_id (FK), user_id (FK), role (ENUM: super_admin|admin|committee|cashier|donor),
invited_by (FK user), joined_at, is_active,
UNIQUE(masjid_id, user_id)
```

#### `accounts` (financial accounts per masjid)
```
id (UUID), masjid_id (FK), account_name, account_type (ENUM),
bank_name, account_number, opening_balance, opening_date,
is_active, notes, created_by (FK), created_at, updated_at
```

#### `income_records`
```
id (UUID), masjid_id (FK), account_id (FK),
title, amount (DECIMAL 15,2), currency,
income_date, category, source,
payment_method (ENUM), reference_number,
notes, receipt_url,
donor_id (FK, nullable — links to monthly donation),
recorded_by (FK), is_deleted, deleted_at, deleted_by,
created_at, updated_at
```

#### `expense_records`
```
id (UUID), masjid_id (FK), account_id (FK),
title, amount (DECIMAL 15,2), currency,
expense_date, category, vendor,
payment_method (ENUM), reference_number,
is_recurring, recurring_template_id (FK nullable),
notes, receipt_url, approved_by (FK),
recorded_by (FK), is_deleted, deleted_at, deleted_by,
created_at, updated_at
```

#### `recurring_expense_templates`
```
id (UUID), masjid_id (FK), title, estimated_amount,
category, vendor, payment_method,
frequency (ENUM: monthly|weekly|yearly),
due_day_of_month, is_active,
notes, created_by (FK), created_at, updated_at
```

#### `account_transfers`
```
id (UUID), masjid_id (FK),
from_account_id (FK), to_account_id (FK),
amount (DECIMAL 15,2), currency,
transfer_date, notes, recorded_by (FK), created_at
```

#### `donors`
```
id (UUID), masjid_id (FK), user_id (FK nullable),
full_name, phone, email,
address, monthly_pledge_amount, pledge_currency,
pledge_start_date, pledge_end_date,
payment_method, notes, is_active,
created_by (FK), created_at, updated_at
```

#### `donation_records`
```
id (UUID), masjid_id (FK), donor_id (FK),
month (CHAR 7 — 'YYYY-MM'),
pledged_amount, paid_amount, payment_date,
payment_method, reference_number,
status (ENUM: pending|paid|partial|missed),
verified_by (FK nullable), verification_note,
receipt_url, income_record_id (FK nullable — links to income),
created_at, updated_at
```

#### `notifications`
```
id (UUID), masjid_id (FK), user_id (FK),
type, title, body, is_read,
related_entity_type, related_entity_id,
created_at
```

#### `audit_logs`
```
id (UUID), masjid_id (FK nullable),
user_id (FK), user_name, action (ENUM: create|update|delete|login|logout|invite|...),
entity_type, entity_id,
old_value (JSONB), new_value (JSONB),
ip_address, user_agent, created_at
```

### 7.2 Key Indexes
- `income_records`: `(masjid_id, income_date)`, `(masjid_id, category)`, `(masjid_id, account_id)`
- `expense_records`: `(masjid_id, expense_date)`, `(masjid_id, category)`, `(masjid_id, is_recurring)`
- `donation_records`: `(masjid_id, month)`, `(donor_id, month)`, `(masjid_id, status)`
- `audit_logs`: `(masjid_id, created_at)`, `(user_id, created_at)`

---

## 8. API Design Overview

### 8.1 Base URL Structure
```
https://api.mms.app/v1/
```

### 8.2 Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login, returns JWT |
| POST | `/auth/logout` | Invalidate token |
| POST | `/auth/refresh` | Refresh JWT |
| POST | `/auth/forgot-password` | Send reset OTP |
| POST | `/auth/reset-password` | Reset with OTP |
| POST | `/auth/verify-email` | Verify email |

### 8.3 Masjid Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/masjids` | Register new masjid |
| GET | `/masjids/:id` | Get masjid profile |
| PUT | `/masjids/:id` | Update masjid profile |
| GET | `/masjids/:id/members` | List members |
| POST | `/masjids/:id/members/invite` | Invite member |
| PUT | `/masjids/:id/members/:userId/role` | Update role |
| DELETE | `/masjids/:id/members/:userId` | Remove member |

### 8.4 Financial Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/masjids/:id/accounts` | List accounts |
| POST | `/masjids/:id/accounts` | Create account |
| GET | `/masjids/:id/accounts/:accountId/balance` | Get balance |
| POST | `/masjids/:id/accounts/transfer` | Transfer between accounts |
| GET | `/masjids/:id/income` | List income (filterable) |
| POST | `/masjids/:id/income` | Create income record |
| PUT | `/masjids/:id/income/:recordId` | Update income record |
| DELETE | `/masjids/:id/income/:recordId` | Soft delete record |
| GET | `/masjids/:id/expenses` | List expenses (filterable) |
| POST | `/masjids/:id/expenses` | Create expense record |
| PUT | `/masjids/:id/expenses/:recordId` | Update expense record |
| DELETE | `/masjids/:id/expenses/:recordId` | Soft delete record |
| GET | `/masjids/:id/recurring-templates` | List recurring templates |
| POST | `/masjids/:id/recurring-templates` | Create template |

### 8.5 Donor Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/masjids/:id/donors` | List donors |
| POST | `/masjids/:id/donors` | Add donor |
| PUT | `/masjids/:id/donors/:donorId` | Update donor |
| DELETE | `/masjids/:id/donors/:donorId` | Deactivate donor |
| POST | `/masjids/:id/donors/:donorId/invite` | Invite donor to portal |
| GET | `/masjids/:id/donations` | List donation records |
| POST | `/masjids/:id/donations/generate` | Generate monthly records |
| PUT | `/masjids/:id/donations/:recordId` | Record/verify payment |
| GET | `/masjids/:id/donations/my` | Donor's own records (donor role) |

### 8.6 Report Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/masjids/:id/reports/summary` | Dashboard summary stats |
| GET | `/masjids/:id/reports/weekly` | Weekly income/expense |
| GET | `/masjids/:id/reports/monthly` | Monthly full breakdown |
| GET | `/masjids/:id/reports/yearly` | Yearly month-by-month |
| GET | `/masjids/:id/reports/donors` | Donor collection report |
| GET | `/masjids/:id/reports/export` | Export report (CSV/PDF) |
| GET | `/masjids/:id/audit-logs` | Audit log (admin only) |

### 8.7 API Conventions
- All responses use consistent envelope: `{ success, data, message, pagination? }`
- Errors use: `{ success: false, error: { code, message, details? } }`
- All list endpoints support: `page`, `limit`, `sort_by`, `sort_order`, `search` query params
- Date filters use: `date_from` and `date_to` in `YYYY-MM-DD` format
- File uploads use `multipart/form-data`

---

## 9. UI/UX Requirements

### 9.1 General UX Principles
- The UI MUST be **mobile-first** and fully responsive.
- The UI MUST be clean, simple, and accessible to non-technical committee members.
- All destructive actions (delete, remove) MUST require a confirmation dialog.
- All forms MUST show inline validation errors before submission.
- All data-changing operations MUST show a loading state and a success/error feedback (toast notification).
- Empty states MUST have a helpful message and a call-to-action (e.g., "No income recorded yet. Add your first income record.").

### 9.2 Page/Screen Inventory

#### Public Pages (No login required)
- Landing / Homepage (platform marketing)
- Masjid Registration Page
- Login Page
- Forgot Password Page
- Public Financial Summary Page (per masjid, if enabled)

#### Authenticated — Common
- Dashboard (Home)
- Notification Center
- Profile & Account Settings
- Change Password

#### Authenticated — Admin / Committee
- Masjid Profile Settings
- Member Management
- Account (Financial Accounts) List & Detail
- Income List, Create, Edit, View
- Expense List, Create, Edit, View
- Recurring Expense Templates
- Donor List, Create, Edit, Detail
- Donation Records (monthly view — grid of donors × months)
- Reports & Analytics
- Audit Log

#### Authenticated — Donor Portal
- My Donation History (table view)
- My Profile
- Download/Print Receipt (per month)

#### Super Admin
- All Masjids List
- Masjid Detail (view any masjid)
- Platform Analytics
- User Search

### 9.3 Key UI Components
- **Financial Summary Cards** — large, scannable cards showing key balance and period stats.
- **Donation Grid** — a matrix of donors (rows) × months (columns) showing payment status with color coding (green = paid, yellow = partial, red = missed, grey = pending).
- **Transaction Table** — sortable, filterable, paginated table for income/expense records.
- **Chart Components** — bar chart for monthly comparison, donut chart for category breakdown, line chart for balance over time.
- **Date Range Picker** — pre-set options (This Week, This Month, Last Month, This Year, Custom).
- **Receipt Upload** — drag-and-drop with preview.
- **Inline Balance Indicator** — always-visible current balance in the sidebar/header.

---

## 10. Security Requirements

- All HTTP traffic MUST be served over **HTTPS**. HTTP MUST redirect to HTTPS.
- Passwords MUST be hashed with **bcrypt** (minimum cost factor 12) or **argon2**.
- JWT secrets MUST be at least 256-bit random values stored in environment variables (never in code).
- API endpoints MUST enforce **rate limiting**: 100 requests/minute per IP for auth endpoints; 1000 requests/minute for general API.
- File uploads MUST be virus-scanned before storage (ClamAV or equivalent).
- Uploaded file types MUST be validated by MIME type (not just extension): only PDF, JPG, PNG allowed.
- All database queries MUST use parameterized queries / ORM — no raw string concatenation.
- Sensitive fields (bank account numbers) MUST be encrypted at rest using AES-256.
- The application MUST implement standard security headers: `HSTS`, `X-Frame-Options`, `Content-Security-Policy`, `X-Content-Type-Options`.
- Admin actions (delete, role changes) MUST require password confirmation or 2FA (Phase 2).
- CORS MUST be configured to allow only known frontend origins.
- Financial records MUST be **immutable via soft delete only** — hard delete is not allowed.

---

## 11. Technology Stack Recommendation

### 11.1 Recommended Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Frontend** | React + TypeScript + Vite | Component ecosystem, type safety, fast build |
| **UI Library** | Tailwind CSS + shadcn/ui | Rapid, consistent, accessible UI |
| **Charts** | Recharts or Chart.js | Lightweight, React-friendly |
| **State Management** | TanStack Query (React Query) | Server state, caching, pagination built-in |
| **Forms** | React Hook Form + Zod | Validation, performance |
| **Backend** | Node.js + Express or Fastify | JavaScript full-stack, large ecosystem |
| **ORM** | Prisma | Type-safe, migration support, PostgreSQL |
| **Database** | PostgreSQL | ACID compliance, JSONB, row-level security |
| **Cache / Queue** | Redis + Bull | Background jobs, rate limiting, session store |
| **File Storage** | AWS S3 or Cloudflare R2 | Scalable object storage |
| **Email** | Resend or SendGrid | Transactional email |
| **Authentication** | Custom JWT + bcrypt | Full control, no vendor lock-in |
| **Hosting (API)** | Railway / Render / AWS ECS | Managed, scalable |
| **Hosting (DB)** | Supabase / AWS RDS | Managed PostgreSQL |
| **Hosting (Frontend)** | Vercel / Netlify / Cloudflare Pages | CDN, zero config |
| **PDF Generation** | Puppeteer or pdfmake | Report export |
| **CSV Export** | json2csv / papaparse | Simple, lightweight |

### 11.2 Alternative Stack (if PHP/Laravel preferred)

| Layer | Technology |
|-------|-----------|
| **Backend** | Laravel (PHP 8.2+) |
| **ORM** | Eloquent |
| **Queue** | Laravel Horizon + Redis |
| **Frontend** | Inertia.js + React or Livewire |

---

## 12. Development Phases & Task Breakdown

### Phase 1 — Foundation (Weeks 1–4)

#### Sprint 1 (Week 1–2): Project Setup & Auth
- [ ] Initialize monorepo (frontend + backend)
- [ ] Set up PostgreSQL database and Prisma schema
- [ ] Implement user registration and email verification
- [ ] Implement login / logout / JWT / refresh token
- [ ] Implement password reset via email OTP
- [ ] Build masjid registration flow (creates masjid + sets user as admin)
- [ ] Build basic masjid middleware (tenant context injection)
- [ ] Build role-based authorization middleware
- [ ] Set up Redis for rate limiting and session blacklist
- [ ] Set up file upload to S3/R2 with signed URL retrieval
- [ ] Set up SendGrid/Resend for transactional email

#### Sprint 2 (Week 3–4): Core UI Shell
- [ ] Design system setup (Tailwind config, color tokens, typography)
- [ ] Build main layout: sidebar navigation, header, notification bell
- [ ] Build login, register, forgot password pages
- [ ] Build masjid registration wizard (multi-step)
- [ ] Build masjid settings page (profile, branding, currency)
- [ ] Build member management page (invite, role change, remove)
- [ ] Build user profile and change password pages
- [ ] Build empty dashboard page structure

---

### Phase 2 — Financial Core (Weeks 5–9)

#### Sprint 3 (Week 5–6): Accounts & Income
- [ ] Build financial accounts CRUD (API + UI)
- [ ] Build real-time balance calculation logic
- [ ] Build income record CRUD (API + UI)
  - [ ] Form with all fields, file upload, validation
  - [ ] Income list with filter, search, sort, pagination
  - [ ] Inline edit and delete with confirmation
- [ ] Build weekly income aggregation API
- [ ] Build CSV export for income

#### Sprint 4 (Week 7–8): Expenses & Recurring
- [ ] Build expense record CRUD (API + UI)
  - [ ] Form with all fields, recurring flag, file upload
  - [ ] Expense list with filter, search, sort, pagination
- [ ] Build recurring expense template CRUD (API + UI)
- [ ] Build background job for recurring expense reminders
- [ ] Build account transfer feature (API + UI)
- [ ] Build weekly/monthly expense aggregation API
- [ ] Build CSV export for expenses

#### Sprint 5 (Week 9): Dashboard & Balance
- [ ] Build dashboard API (summary stats endpoint)
- [ ] Build dashboard UI with all cards and charts
  - [ ] Balance cards
  - [ ] Monthly comparison bar chart
  - [ ] Category breakdown donut chart
  - [ ] Recent transactions list
  - [ ] Upcoming recurring expenses widget
- [ ] Build account balance history chart
- [ ] Build "balance as of date" query

---

### Phase 3 — Donors & Reporting (Weeks 10–13)

#### Sprint 6 (Week 10–11): Donor Management
- [ ] Build donor profile CRUD (API + UI)
- [ ] Build monthly donation record generation (bulk create)
- [ ] Build donation recording and verification workflow (API + UI)
- [ ] Build donation grid view (donors × months matrix UI)
- [ ] Build donor invitation email flow
- [ ] Build donor portal login and dashboard
  - [ ] My donation history table
  - [ ] Printable receipt per month
- [ ] Build manual payment reminder trigger (email)
- [ ] Build donor report export (CSV/PDF)

#### Sprint 7 (Week 12–13): Reports & Audit
- [ ] Build all standard report APIs (weekly, monthly, yearly, category)
- [ ] Build reports page UI with date range picker and chart views
- [ ] Build PDF report export (with masjid logo + header)
- [ ] Build CSV report export
- [ ] Build print-friendly CSS for reports
- [ ] Build audit log API (with filters)
- [ ] Build audit log UI for admin
- [ ] Build notification system (in-app) — API + UI
- [ ] Build email notification triggers for all defined events

---

### Phase 4 — Polish & Launch (Weeks 14–16)

#### Sprint 8 (Week 14–15): Super Admin & Security
- [ ] Build Super Admin panel (masjid list, platform stats)
- [ ] Build masjid activation/deactivation by Super Admin
- [ ] Security hardening: rate limiting, CORS, security headers
- [ ] File upload virus scanning integration
- [ ] Input sanitization audit across all API endpoints
- [ ] Encrypted storage for sensitive fields

#### Sprint 9 (Week 16): Testing & Deployment
- [ ] Unit tests for financial calculation logic
- [ ] Integration tests for critical API flows (auth, income, donors)
- [ ] End-to-end tests for key user journeys (masjid registration, donation tracking)
- [ ] Performance testing (load test dashboard and report endpoints)
- [ ] Set up CI/CD pipeline (GitHub Actions)
- [ ] Set up staging and production environments
- [ ] Set up database backup automation
- [ ] Set up monitoring and error tracking (Sentry)
- [ ] Set up uptime monitoring
- [ ] Production deployment and smoke testing

---

### Phase 5 — Future Enhancements (Post-Launch)

| Feature | Priority |
|---------|----------|
| SMS notifications (Twilio / local gateway) | High |
| Multi-language support (Bengali, Arabic, Urdu) | High |
| RTL layout support | High |
| Online donation payment gateway integration | Medium |
| Custom subdomain per masjid | Medium |
| Mobile native app (React Native) | Medium |
| Two-factor authentication (2FA) | Medium |
| Annual budget planning and tracking | Medium |
| Zakat calculation helper | Low |
| Inter-masjid network / organization grouping | Low |
| Asset/inventory management | Low |

---

## 13. Acceptance Criteria

### 13.1 Must-Have for v1.0 Launch
- [ ] A committee member can register a masjid and log in within 5 minutes.
- [ ] Admin can record income and expenses with receipt attachments.
- [ ] Dashboard correctly shows current balance, monthly income, and monthly expenses.
- [ ] Admin can add a monthly donor and mark their payment as verified.
- [ ] Donor can log in and see their donation history with verified status.
- [ ] Monthly and yearly financial reports can be exported as PDF and CSV.
- [ ] All financial data is isolated per masjid — no data leakage between tenants.
- [ ] Audit log records all create, update, delete operations on financial records.
- [ ] The system is usable on a mobile browser without horizontal scrolling.

### 13.2 Definition of Done (per feature)
- API endpoint implemented with authentication and authorization checks.
- Frontend page/component implemented with loading, error, and empty states.
- Form validation on both client and server side.
- Unit/integration test written.
- No critical accessibility violations (automated check with axe).
- Code reviewed and merged.

---

## 14. Glossary

| Term | Definition |
|------|------------|
| **Masjid** | A mosque; an Islamic place of worship |
| **MMS** | Masjid Management System — this platform |
| **Tenant** | A single masjid workspace on the platform |
| **Admin** | The primary committee member who manages the masjid workspace |
| **Donor** | A person who commits to a monthly donation (pledge) |
| **Pledge** | The committed monthly donation amount by a donor |
| **Donation Record** | The monthly record tracking whether a donor paid their pledge |
| **Account** | A financial account belonging to a masjid (e.g., cash box, bank account) |
| **Soft Delete** | Marking a record as deleted without physically removing it from the database |
| **Recurring Expense** | A regular expense that repeats on a defined schedule |
| **Fiscal Year** | The 12-month period used for annual financial reporting |
| **RBAC** | Role-Based Access Control — restricting system access based on user role |
| **JWT** | JSON Web Token — used for secure authentication sessions |
| **Multi-tenant** | A single platform serving multiple independent organizations (masjids) |
| **Row-Level Security** | Database-level enforcement that users can only access their own tenant's rows |

---

*Document prepared for software development use. This SRS is intended to be fed to an AI code generation tool or handed to a development team as the primary specification for building the Masjid Management System (MMS).*

*Last updated: May 2026*
