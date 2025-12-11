---
trigger: always_on
---

# Architecture Constraints (Always On)

1. **Class-Based Services:** [MANDATORY]
   - All business logic MUST reside in Service Classes (e.g., `OrganizationService`) inside `app/services/`.
   - API Routers (`app/api/`) should only handle request parsing and calling services.

2. **Multi-Tenancy Strategy:**
   - **Master DB:** Stores metadata (Org Name, Admin Creds) in `master_metadata`.
   - **Tenant Collections:** Each org gets a dedicated collection named `org_{sanitized_name}`.
   - **Update Logic:** If org name changes, migrate data to new collection dynamically.