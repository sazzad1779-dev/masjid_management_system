# Feature Tracker

This document tracks the implemented features and their corresponding functions/endpoints.

| Feature ID | Feature Name | Status | Functions / Endpoints |
| --- | --- | --- | --- |
| 01 | Platform & Multi-Masjid Architecture | Done | `register_masjid`, `get_masjid_profile`, `super_admin_analytics` |
| 02 | Authentication & Authorization | Done | `login_access_token`, `refresh_token`, `add_user_to_masjid`, `RoleChecker` (context-aware) |
| 03 | Masjid Profile & Customization | Done | `update_masjid_profile`, `get_masjid_profile`, `register_masjid`, `friday_jumuah_time`, `workspace_settings` |
| 04 | Income Management | Done | `create_income`, `read_incomes`, `get_weekly_summary`, `read_income`, `update_income`, `delete_income` |
| 05 | Expense Management | Done | `create_expense`, `read_expenses`, `get_monthly_summary`, `read_expense`, `update_expense`, `delete_expense` |
| 06 | Account & Balance Management | Done | `create_account`, `read_accounts`, `get_account_balance`, `create_transfer` |
| 07 | Monthly Donation & Donor Management | Done | `create_donor`, `read_donors`, `generate_monthly_donations`, `verify_donation_payment` |
| 08 | Reporting & Analytics | Done | `get_summary_stats`, `get_weekly_report`, `get_monthly_report`, `get_yearly_report`, `get_donor_report` |
| 09 | Notifications & Alerts | Done | `NotificationService.create_notification`, `notify_masjid_admins`, `notify_income_recorded`, `notify_expense_recorded`, `notify_donation_verified`, `send_email` (placeholder), [Walkthrough](docs/walkthrough/feature_9_walkthrough.md) |
| 10 | Audit & Activity Log | Done | `AuditLogService.log_action`, `/audit-logs`, [Walkthrough](docs/walkthrough/feature_10_walkthrough.md) |
