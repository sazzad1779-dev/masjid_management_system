# 8. Reporting & Analytics

## Summary
Provides robust analysis metrics, visualizations, and static reports (printable/downloadable) encompassing all aggregated financial data tracked across defined timeframes.

## Workflow Description
1. User travels to Reports section.
2. Selects the desired temporal report type (Daily, Weekly, Monthly, Yearly).
3. The server runs heavy aggregation queries on requested categories/tags.
4. Generates both graphical visualization and tabular structural layouts.
5. User clicks "Export" to download a localized PDF variant with headers.

## Functions Input/Output
- **Generate Financial Breakdown Report**
  - **Input:** masjid_id, start_date, end_date (Report context filters)
  - **Output:** JSON containing { income: [], expenses: [], net_balance: X }
- **Dashboard Stats Synthesis**
  - **Input:** masjid_id
  - **Output:** Core high-level sums (Total Balance, Current Month Net).
- **Export to Document**
  - **Input:** Requested format (CSV, PDF), report dataset.
  - **Output:** File stream with proper headers containing Masjid identity.

## Operation Workflow
- Uses indexed Database SQL Group-Bys rather than standard server-side mapping mechanisms to support fast processing.
- Handles custom print schemas with CSS specifically formulated for PDF engine print capabilities.

## Other Things
- Time generation bounds must complete inside the < 5 seconds requirement constraint mentioned in the SRS.
