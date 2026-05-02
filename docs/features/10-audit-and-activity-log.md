# 10. Audit & Activity Log

## Summary
Maintains rigid and read-only transparency standards providing chronological sequence data on exact transactions and manipulations handled by standard accounts.

## Workflow Description
1. Admin alters a financial tracking mechanism inside an account.
2. The endpoint handler synchronously binds the `old_value` entity with new `new_value` schema object.
3. Saves a record of 'update' type referencing the table element and user signature within the `audit_logs` relation.
4. Super Admin / Admin scans logs within the interface finding exact change traces.

## Functions Input/Output
- **Record Action Mutator**
  - **Input:** user_id, user_name, entity_type, action(ENUM), old/new JSON states.
  - **Output:** Inserted immutable log mechanism.
- **Generate Read-Only Feed**
  - **Input:** `masjid_id`, target filtered ranges / action identities.
  - **Output:** Activity array containing temporal modifications.

## Operation Workflow
- Audit fields include critical elements such as IP headers, User Agents, ensuring valid security contexts.
- Specifically protects itself from removal directives (even standard Administrator deletions merely mark soft flags in other tables).

## Other Things
- Helps guarantee non-repudiation inside financial data workflows—necessary due to high community responsibility.
