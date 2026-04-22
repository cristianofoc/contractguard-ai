"""
/health endpoint — used by load balancers and CI health checks.
"""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Return a simple OK status to confirm the service is running."""
    return {"status": "ok"}
