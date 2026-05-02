# Feature Tracker

This document tracks the implemented features and their corresponding functions/endpoints.

| Feature ID | Feature Name | Status | Functions / Endpoints | Walkthrough |
| --- | --- | --- | --- | --- |
| 01 | Platform & Multi-Masjid Architecture | Done | `register_masjid`, `get_masjid_profile`, `super_admin_analytics` | [Platform_&_Multi-Masjid_Architecture](docs/walkthrough/Feature_1_Platform_&_Multi-Masjid_Architecture_walkthrough.md)|
| 02 | Authentication & Authorization | Done | `login_access_token`, `refresh_token`, `add_user_to_masjid`, `RoleChecker` (context-aware) | [Authentication_&_Authorization_Feature](docs/walkthrough/feature_2_Authentication_&_Authorization_Feature.md) |
| 03 | Masjid Profile & Customization | Done | `update_masjid_profile`, `get_masjid_profile`, `register_masjid`, `friday_jumuah_time`, `workspace_settings` | [Masjid_Profile_&_Customization_](docs/walkthrough/feature_3_Masjid_Profile_&_Customization__walkthrough.md)|
| 04 | Income Management | Done | `create_income`, `read_incomes`, `get_weekly_summary`, `read_income`, `update_income`, `delete_income` | [Income_Management](docs/walkthrough/Feature_4_Income_Management_walkthrough.md)|
| 05 | Expense Management | Done | `create_expense`, `read_expenses`, `get_monthly_summary`, `read_expense`, `update_expense`, `delete_expense` | [Expense_Management](docs/walkthrough/feature_5_Expense_Management_walkthrough.md) |
| 06 | Account & Balance Management | Done | `create_account`, `read_accounts`, `get_account_balance`, `create_transfer` | [Account_&_Balance_Management](docs/walkthrough/feature_6_Account_&_Balance_Management_walkthrough.md)|
| 07 | Monthly Donation & Donor Management | Done | `create_donor`, `read_donors`, `generate_monthly_donations`, `verify_donation_payment`| [Monthly_Donation_&_Donor_Management](docs/walkthrough/Feature_7_Monthly_Donation_&_Donor_Management_walkthrough.md) |
| 08 | Reporting & Analytics | Done | `get_summary_stats`, `get_weekly_report`, `get_monthly_report`, `get_yearly_report`, `get_donor_report` | [Reporting_&_Analytics](docs/walkthrough/Feature_8_Reporting_&_Analytics_walkthrough.md) |
| 09 | Notifications & Alerts | Done | `NotificationService.create_notification`, `notify_masjid_admins`, `notify_income_recorded`, `notify_expense_recorded`, `notify_donation_verified`, `send_email` | [Notifications_&_Alerts](docs/walkthrough/feature_9_walkthrough.md) |
| 10 | Audit & Activity Log | Done | `AuditLogService.log_action`, `/audit-logs` | [_Audit_&_Activity_Log](docs/walkthrough/feature_10_walkthrough.md) |



