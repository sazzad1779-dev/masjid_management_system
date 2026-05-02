# 2. Authentication & Authorization

## Summary
The application supports standard email/password authentication along with Role-Based Access Control (RBAC) to ensure security and proper access isolation.

## Workflow Description
1. User logs in with email and password.
2. System generates and issues a JWT session token containing `user_id` and `masjid_id`.
3. User accesses protected route.
4. Server verifies token and checks if the user's role has permission for the action.

## Functions Input/Output
- **Login User**
  - **Input:** Email, Password
  - **Output:** JWT Token, Refresh Token, User Profile Data
- **Reset Password**
  - **Input:** Email / OTP, New Password
  - **Output:** Success/Failure Message
- **Check Permission**
  - **Input:** JWT Context, Required Action (e.g., Delete Income)
  - **Output:** Boolean (Authorized/Unauthorized)

## Operation Workflow
- **Authentication:** Sessions managed via JWT and rotation of Refresh Tokens.
- **Authorization:** Handled server-side with RBAC middleware on APIs.
- **Donor Access:** Monthly donors have scoped access just to view their own donation history.

## Other Things
- Consider adding Google OAuth in the future.
- Need strict frontend guards to redirect unauthorized attempts.
