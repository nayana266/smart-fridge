from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "smart-fridge-backend",
        "version": "1.0.0"
    }

@router.get("/ready")
async def readiness_check():
    """Readiness check for load balancer"""
    return {
        "status": "ready",
        "service": "smart-fridge-backend"
    }
