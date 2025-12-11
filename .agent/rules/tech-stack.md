---
trigger: always_on
---

# Tech Stack Constraints (Always On)

1. **Framework:** Use FastAPI with `uvicorn`.
2. **Database:** - Use `motor` (AsyncIOMotorClient) for MongoDB.
   - NEVER use synchronous `pymongo` for DB calls.
   - All DB operations must use `await`.
3. **Validation:** - Use Pydantic v2 (`BaseModel`, `Field`, `ConfigDict`).
   - Use `pydantic-settings` for environment variables.