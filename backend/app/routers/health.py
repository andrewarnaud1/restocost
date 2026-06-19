"""Health check endpoints."""

from fastapi import APIRouter, HTTPException, status

from app.db.database import check_db_connection

router = APIRouter(tags=["health"])


@router.get("/health", response_model=dict[str, str])
async def health_check() -> dict[str, str]:
    """Basic health check endpoint.

    Returns:
        Dict[str, str]: Status response with "ok" value.

    Example:
        ```bash
        curl http://localhost:8000/api/health
        # Returns: {"status": "ok"}
        ```
    """
    return {"status": "ok"}


@router.get("/health/db", response_model=dict[str, str])
async def health_check_db() -> dict[str, str]:
    """Database health check endpoint.

    Verifies that the application can connect to the PostgreSQL database.

    Returns:
        Dict[str, str]: Status response with "ok" value if database is reachable.

    Raises:
        HTTPException: 503 Service Unavailable if database is unreachable.

    Example:
        ```bash
        curl http://localhost:8000/api/health/db
        # Returns: {"status": "ok"} if database is healthy
        # Returns: 503 error if database is unreachable
        ```
    """
    is_healthy = await check_db_connection()

    if not is_healthy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed",
        )

    return {"status": "ok"}
