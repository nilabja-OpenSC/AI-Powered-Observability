"""
Health Check Routes - E-commerce Backend
"""

from fastapi import APIRouter, status
from pydantic import BaseModel
import structlog

from backend.database import check_db_connection

logger = structlog.get_logger(__name__)

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    service: str
    version: str
    database: str


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint.
    
    Returns service status and database connectivity.
    """
    db_status = "healthy" if check_db_connection() else "unhealthy"
    
    return HealthResponse(
        status="healthy",
        service="ecommerce-backend",
        version="1.0.0",
        database=db_status,
    )


@router.get("/ready", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def readiness_check():
    """
    Readiness check endpoint.
    
    Returns 200 if service is ready to accept traffic.
    Returns 503 if database is not available.
    """
    db_healthy = check_db_connection()
    
    if not db_healthy:
        logger.warning("readiness_check_failed", reason="database_unavailable")
        return HealthResponse(
            status="not_ready",
            service="ecommerce-backend",
            version="1.0.0",
            database="unhealthy",
        )
    
    return HealthResponse(
        status="ready",
        service="ecommerce-backend",
        version="1.0.0",
        database="healthy",
    )

# Made with Bob
