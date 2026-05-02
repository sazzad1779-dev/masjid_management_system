# 4. Income Management

## Summary
Provides mechanisms to systematically track all financial income entering the masjid through various channels (daily/friday collections, zakat, sadaqah, etc.).

## Workflow Description
1. Cashier/Admin receives funds (e.g., Friday Jumu'ah Collection).
2. Navigates to Income page and initiates flow to "Add Income Record".
3. Fills in title, amount, category, date, and payment method.
4. Attaches a physical receipt scan if necessary.
5. Saves record. Record is tied to a specific account balance.

## Functions Input/Output
- **Create Income Record**
  - **Input:** Title, Amount (Decimal), Date, Category, Payment Method, Reference Number, Notes, Receipt Attachment File.
  - **Output:** Created Income Record details.
- **Search & Filter Income**
  - **Input:** Date range, Category, Payment Method, Amount Range.
  - **Output:** Paginated list of income records.
- **Export Income**
  - **Input:** Selected Filters, Format (CSV/PDF).
  - **Output:** File Download Stream.

## Operation Workflow
- **Validation:** Amount must be > 0. Validations on date format.
- Weekly collections auto-tracked and summarized by linking to a week identifier.
- Delete operations are soft deletes for integrity.

## Other Things
- Allows batch import through CSV files.
- Automatically calculates weekly Jumu'ah funds accurately mapped to Fridays.
