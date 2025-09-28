from fastapi import APIRouter
<<<<<<< HEAD
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "smart-fridge-api"
=======

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
>>>>>>> 85cfca634be5e8ef45cb4dc555da76c75924dfa3
    }
