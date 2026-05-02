# 5. Expense Management

## Summary
Comprehensive tools for recording, categorized tracking, and managing all regular and irregular outflows from the masjid funds.

## Workflow Description
1. Committee member expends money on an item (e.g., utility bill).
2. Initiates the "Add Expense Record".
3. Provides amount, category (utility), date, and vendor details.
4. If this is a regular bill, it can be marked as `is_recurring`.
5. Upon saving, it directly reduces the balance of the chosen financial account.

## Functions Input/Output
- **Create Expense Record**
  - **Input:** Title, Amount (Decimal), Date, Category, Vendor, Payment Method, Note, File Attachment, Recurring Flag.
  - **Output:** Created Expense Record details.
- **Create Recurring Template**
  - **Input:** Vendor, Category, Estimated Amount, Frequency (Monthly, etc.)
  - **Output:** Template created and scheduled reminder info.
- **Filter Expenditures**
  - **Input:** Date range, Vendor, Category, Payment Method.
  - **Output:** List of expense records.

## Operation Workflow
- Incorporates recurring expense logic, generating system notifications / reminders before amounts are due.
- Admins can manage these templates to pause/resume recurring billing contexts.
- Soft-deletes strictly applied for audit capabilities.

## Other Things
- Needs clear linkage when an actual expense record resolves an impending recurring template obligation.
