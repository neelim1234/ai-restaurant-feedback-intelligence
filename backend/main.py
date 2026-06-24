"""
main.py - FastAPI application factory.

Phase 1: Minimal setup. Routers are registered in later phases.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers.analytics import router as analytics_router
from routers.lookup import router as lookup_router
from routers.ai import router as ai_router

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "B2B SaaS analytics platform for multi-branch restaurant businesses. "
        "Converts raw customer feedback into actionable business intelligence "
        "using SQL analytics and AI-generated insights."
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS — allow all origins during development; restrict in production
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API Routers
app.include_router(analytics_router)
app.include_router(lookup_router)
app.include_router(ai_router)



# ---------------------------------------------------------------------------
# Health check — always present, useful for deployment
# ---------------------------------------------------------------------------
@app.get("/health", tags=["System"])
def health_check():
    """Returns service liveness status."""
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }

