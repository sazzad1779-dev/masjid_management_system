# Frontend Pages Analysis: Masjid Management System

Based on the existing backend implementation, here is a comprehensive list of pages required for the frontend, categorized by module.

## 1. Authentication & Onboarding
| Page Name | Details & Components | Key API Endpoints |
| --- | --- | --- |
| **Login** | Email/Password form, "Keep me logged in" option | `/auth/login/access-token` |
| **Signup** | Basic registration for new users | `/auth/signup` |
| **Register Masjid** | Form for Super Admins to onboard new Masjids | `/masjids/` |
| **Forgot Password** | Email entry to receive reset link | `/auth/forgot-password` |
| **Reset Password** | New password entry with token verification | `/auth/reset-password` |

## 2. Dashboard & Analytics
| Page Name | Details & Components | Key API Endpoints |
| --- | --- | --- |
| **Main Dashboard** | Overview cards (Balance, Income, Expense), Recent Activity, Notifications bell | `/reports/summary` |
| **Super Admin Stats** | Multi-masjid metrics (Total Masjids, Total Users, Platform-wide usage) | `/masjids/super-admin/analytics` |

## 3. Financial Management
| Page Name | Details & Components | Key API Endpoints |
| --- | --- | --- |
| **Income List** | Searchable table of incomes, Filters (Date, Category), Export options | `/income/` |
| **Expense List** | Searchable table of expenses, Filters (Date, Account) | `/expense/` |
| **Account Management** | Cards for each Account (Cash, Bank), Current balances, Transaction history | `/accounts/` |
| **Fund Transfer** | Modal/Page to transfer funds between internal accounts | `/accounts/transfer` |

## 4. Donor & Subscription Management
| Page Name | Details & Components | Key API Endpoints |
| --- | --- | --- |
| **Donor Directory** | List of regular donors, Search by name/phone, Pledge status | `/donors/` |
| **Donation Tracking** | Monthly collection grid, Status indicators (Paid, Pending, Overdue) | `/donations/` |
| **Payment Verification** | Interface to verify received donor payments and record details | `/donations/{id}/verify` |
| **Generate Monthly Bills** | Trigger for batch-generating donation records for a new month | `/donations/generate` |

## 5. Reports
| Page Name | Details & Components | Key API Endpoints |
| --- | --- | --- |
| **Weekly Report** | 7-day breakdown of cash flow | `/reports/weekly` |
| **Monthly Report** | Calendar-based category analysis | `/reports/monthly` |
| **Yearly Report** | Annual financial performance | `/reports/yearly` |
| **Donor Collection** | Performance report of monthly donor collections | `/reports/donors` |

## 6. Settings & Administration
| Page Name | Details & Components | Key API Endpoints |
| --- | --- | --- |
| **Masjid Profile** | Edit Masjid name, Address, Prayer/Jumuah times, and Logo | `/masjids/{id}` |
| **Team Management** | Invite staff/committee, Assign roles (Admin, Cashier, Viewer) | `/auth/me` (to check roles) |
| **Audit Logs** | Security trail of all system changes (IP, User, Action, Timestamp) | `/audit-logs/` |
| **Notification Center** | Inbox for system alerts and financial notifications | `/notifications/` |

---
**Total Estimated Pages:** ~18-20 unique views (including modals/sub-pages).
