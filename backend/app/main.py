"""
FastAPI application entrypoint.

Registers all route groups, CORS middleware, and startup/shutdown events.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, contracts, health
from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered contract risk reviewer — upload a contract, get instant insights.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ── CORS ─────────────────────────────────────────────────────────────────────
# Allow the React dev server and production frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",
        "https://contractguard.ai",  # production (update as needed)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(contracts.router, prefix="/api/v1")


# ── Startup / shutdown events ─────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event() -> None:
    """Log startup confirmation. DB tables are managed by Alembic migrations."""
    print(f"🚀 {settings.APP_NAME} is running")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Graceful shutdown — close the connection pool."""
    from app.database import engine

    await engine.dispose()
    print("🛑 Database connection pool closed")
