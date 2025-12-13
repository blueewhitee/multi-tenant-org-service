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


tags_metadata = [
    {
        "name": "Organization",
        "description": "Operations to manage organizations (create, update, delete).",
    },
    {
        "name": "Authentication",
        "description": "Admin authentication and token management.",
    },
]

app = FastAPI(
    title="Multi-tenant Org Service",
    description="""
    Backend service for managing multi-tenant organizations.
    
    Key Features:
    * Dynamic Multi-tenancy: Dedicated MongoDB collection for each organization.
    * JWT Authentication: Secure admin access.
    * Async Performance: Built with FastAPI and Motor.
    * Rate Limiting: Protected endpoints using SlowAPI.
    * Class-Based Services: Clean architecture with service layer pattern.
    """,
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    openapi_tags=tags_metadata,
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,  # Hide Schemas at bottom
        "docExpansion": "none",          # Collapse all operations
        "syntaxHighlight.theme": "obsidian", # Dark theme for code
        "tryItOutEnabled": True,         # "Try it out" ready by default
        "displayRequestDuration": True,  # Show how long requests take
    }
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

limiter = Limiter(key_func=get_remote_address, headers_enabled=True)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

from app.api.v1.org import router as org_router
from app.api.v1.auth import router as auth_router

app.include_router(org_router, prefix="/api/v1/org", tags=["Organization"])
app.include_router(auth_router, prefix="/api/v1/admin", tags=["Authentication"])

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Welcome to the Multi-tenant Organization Management Service"}
