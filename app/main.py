from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
    title="Multi-tenant Org Service",
    description="Backend service with dynamic MongoDB collections and JWT Auth.",
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

from app.api.v1.org import router as org_router
from app.api.v1.auth import router as auth_router

app.include_router(org_router, prefix="/api/v1/org", tags=["Organization"])
app.include_router(auth_router, prefix="/api/v1/admin", tags=["Authentication"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Multi-tenant Organization Management Service"}