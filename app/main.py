from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.mongodb import db
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db.connect()
    yield
    # Shutdown
    await db.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

from app.api.v1.org import router as org_router
from app.api.v1.auth import router as auth_router

app.include_router(org_router, prefix="/api/v1/org", tags=["Organization"])
app.include_router(auth_router, prefix="/api/v1/admin", tags=["Authentication"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Multi-tenant Organization Management Service"}