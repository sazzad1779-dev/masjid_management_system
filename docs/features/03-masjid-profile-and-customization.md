# 3. Masjid Profile & Customization

## Summary
This feature allows customization of a masjid's organizational identity on the platform, including settings like logos, contact details, UI themes, and workspace preferences.

## Workflow Description
1. Masjid Admin navigates to settings page.
2. Modifies text fields (name, address, contacts) or uploads a new logo/banner.
3. Updates workspace preferences like primary color or fiscal year start.
4. UI instantly updates to reflect new branding across the workspace.

## Functions Input/Output
- **Update Masjid Profile**
  - **Input:** Profile Data Object (Name, Address, Email, Phone, Currency, Fiscal Year, Colors, etc.)
  - **Output:** Updated Masjid Profile Object
- **Upload Logo/Banner**
  - **Input:** Image File (Max 2MB, PNG/JPG)
  - **Output:** S3/Object Storage URL
- **Update Preferences**
  - **Input:** Toggle Public Summary, Categories configuration
  - **Output:** Success confirmation

## Operation Workflow
- Config options saved into the `masjids` table or a separate settings JSON structure.
- Default Categories pre-populated and can be overridden by admins.
- Public toggle exposes a specific public-facing frontend component.

## Other Things
- Social media links integration.
- Custom subdomain settings potentially planned for next phases.
