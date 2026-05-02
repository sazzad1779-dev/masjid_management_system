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

### Seeder (`src/db/seeders/feature_9_seeder.py`)

Seeds 6 notification types: `masjid_invitation`, `income_recorded`, `expense_recorded`, `low_balance`, `role_updated`, and `donation_verified`.

## Test Results

**File:** `tests/api/v1/test_feature_9.py` — **6/6 passed** ✅

| Test | Validates |
|---|---|
| `test_income_creates_notification` | Income POST triggers `income_recorded` notification |
| `test_expense_creates_notification` | Expense POST triggers `expense_recorded` notification |
| `test_list_notifications` | GET `/notifications/` returns user's notifications |
| `test_mark_notification_read` | PUT `/{id}/read` sets `is_read=True` |
| `test_mark_all_notifications_read` | PUT `/read-all` marks all as read |
| `test_filter_unread_notifications` | GET with `?is_read=false` filter works |

## SRS Alignment

| SRS Requirement | Status |
|---|---|
| Internal notification system for financial events | ✅ |
| Notification for income recorded | ✅ |
| Notification for expense recorded | ✅ |
| Notification for donation verified (admin + donor) | ✅ |
| Notification for user invitation | ✅ |
| Notification for role changes | ✅ |
| Email notification placeholder | ✅ |
| Mark as read / mark all as read | ✅ |
| Filter by read/unread status | ✅ |
