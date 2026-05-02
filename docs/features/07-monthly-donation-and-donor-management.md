# 7. Monthly Donation & Donor Management

## Summary
Enables tracking of recurring donors who commit to a fixed sum over periods. Admin can monitor active pledges, track completion, and provide secure access for donors to view their historical contributions.

## Workflow Description
1. Admin creates a Donor profile, entering their contact information and monthly pledge amount.
2. Committeeman invites the Donor to a self-service portal.
3. Monthly, the system registers expected donations.
4. Upon receiving funds, the committee marks the expected donation record as "Paid".
5. Donor receives confirmation and a receipt accessible on their portal.

## Functions Input/Output
- **Manage Donors**
  - **Input:** Donor Data (Name, Phone, Pledge Amount, Method, etc.)
  - **Output:** Updated / Created Donor.
- **Generate Monthly Donation Obligations**
  - **Input:** Month Identifer (e.g., YYYY-MM)
  - **Output:** List of pending donation entities per active donor.
- **Verify Payment**
  - **Input:** Record ID, Payment Data (Paid amount, Note).
  - **Output:** Updated Monthly Record (Status -> Paid/Partial).

## Operation Workflow
- Automatically flags unfulfilled pledges as 'Missed' following end-of-month threshold.
- Sends regular automated reminder nudging late donors.

## Other Things
- Needs specific isolated views for Donors logged into the application.
- Donors should be able to download distinct PDF verified receipts natively.
