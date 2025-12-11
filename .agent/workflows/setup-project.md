---
description: Scaffolds the FastAPI project with Clean Architecture.
---

# Project Setup Workflow

## Step 2: Config & DB
1. Create `requirements.txt` containing:
   - fastapi, uvicorn[standard]
   - motor, pydantic-settings
   - python-jose[cryptography], passlib[bcrypt]  <-- Ye line zaroori hai
   - email-validator
2. Create `app/core/config.py`... (baki same rahega)