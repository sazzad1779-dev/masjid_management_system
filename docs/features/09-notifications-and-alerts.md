# 9. Notifications & Alerts

## Summary
Internal system capability to construct alerting operations triggering email dispatches, interface banners, and notifications tied directly to event lifecycles.

## Workflow Description
1. Action occurs in the frontend (e.g., verifying a donor payment).
2. Backend hooks listen to this data mutation.
3. System logs a direct application notification bound to a target user.
4. (Optional) Involves background task queue injecting an external email via SMTP/SendGrid.

## Functions Input/Output
- **Log Activity Notification**
  - **Input:** Type, Title, Body, Targeted User ID, Reference Entity Info.
  - **Output:** Notification Entity properly queued.
- **Dispatch Email**
  - **Input:** Recipient Email, Context Variables (Masjid Data), Mail Template ID.
  - **Output:** Accepted Email Send Status.
- **Fetch Unread Notifications**
  - **Input:** User ID
  - **Output:** Sequence of new alert structures.

## Operation Workflow
- Employs a specific Bull/Redis style queue logic to prevent synchronous blocking on slow network-bound SMTP endpoints.
- SMS operations mapped out primarily for a Phase 2 rollout.

## Other Things
- Customizable system preferences handle filtering unneeded emails configured by user boundaries.
