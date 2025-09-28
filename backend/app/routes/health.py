from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "smart-fridge-api",
        "version": "1.0.0"
    }

@router.get("/ready")
async def readiness_check():
    """Readiness check for load balancer"""
    return {
        "status": "ready",
        "service": "smart-fridge-backend"
    }
