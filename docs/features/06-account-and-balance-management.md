# 6. Account & Balance Management

## Summary
Maintains distinct financial accounts (e.g., Cash Box, Bank, Mobile Bank) and provides a highly-accurate real-time balance derived from opening balances and transactional history.

## Workflow Description
1. Admin sets up initial accounts (Cash Account, Bank Account) with opening balances and dates.
2. When creating an income or expense, the user attributes it to a specific account.
3. System aggregates the operations: (Opening Balance + Total Income) - Total Expenses.
4. User initiates account transfers to move funds.
5. System records transfer reducing one account balance and increasing another.

## Functions Input/Output
- **Create Account**
  - **Input:** Account Name, Type (Cash/Bank), Initial Balance, Date, Notes.
  - **Output:** Account Entity.
- **Get Balance**
  - **Input:** Account ID, (Optional Date Threshold for historical balance)
  - **Output:** Exact Decimal Balance.
- **Transfer Funds**
  - **Input:** From Account ID, To Account ID, Amount, Date.
  - **Output:** Created Transfer Record details.

## Operation Workflow
- **Reconciliation:** Concept of defining confirmed balances against dates, which administrators can refer to for audits.
- Dashboard will aggregate Total Current Balance from all active sub-accounts.

## Other Things
- Ensures all records hold strict financial boundaries and math is performed as `DECIMAL(15,2)` locally.
