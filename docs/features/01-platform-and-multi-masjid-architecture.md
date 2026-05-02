# 1. Platform & Multi-Masjid Architecture

## Summary
The system operates as a multi-tenant SaaS platform where multiple masjids can be registered as isolated tenants. Each masjid has its own workspace and data isolation.

## Workflow Description
1. User requests to register a new masjid.
2. System creates a unique `masjid_id` and isolated tenant workspace.
3. Registering user becomes the Masjid Admin.
4. Email verification is performed to activate the masjid workspace.
5. Super Admin can view, deactivate, or delete active masjids.

## Functions Input/Output
- **Register Masjid**
  - **Input:** Masjid Name, Address, City, Country, Contact Email, Logo (Optional).
  - **Output:** Created Masjid Tenant Profile, Verification Email Sent status.
- **Get Masjid Profile**
  - **Input:** `masjid_id`
  - **Output:** Masjid Profile Data (name, slug, logo URL, etc.)
- **Super Admin Analytics**
  - **Input:** None
  - **Output:** Total Masjids, Total Transactions, Active Users.

## Operation Workflow
- **Tenant Isolation:** Enforced via `masjid_id` in JWT and all database queries (Row-Level Security / App-level filtering).
- **Workspace Access:** Accessible via subdomain or unique URL slug.

## Other Things
- Core multi-tenancy logic must be established early as it affects all subsequent features.
- Needs Super Admin impersonation capability for helpdesk support.
