from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import os
from app.services.rekog import rekognition_service, DetectionResult
from app.services.normalize import food_normalizer, NormalizedItem

logger = logging.getLogger(__name__)

router = APIRouter()

class VisionDetectRequest(BaseModel):
    keys: List[str] = Field(..., description="List of S3 object keys to analyze")
    bucket: str = Field(default="smart-fridge-images", description="S3 bucket name")

class VisionDetectResponse(BaseModel):
    items: List[Dict[str, Any]] = Field(..., description="Normalized food items with counts and confidence")
    raw_detections: Optional[List[Dict[str, Any]]] = Field(None, description="Raw Rekognition results for debugging")
    processing_stats: Dict[str, Any] = Field(..., description="Processing statistics")

@router.post("/vision/detect", response_model=VisionDetectResponse)
async def detect_food_items(request: VisionDetectRequest):
    """
    Detect food items from multiple images using AWS Rekognition
    
    This endpoint:
    1. Calls AWS Rekognition on each image
    2. Normalizes raw labels to canonical food names
    3. Merges duplicate items and aggregates counts
    4. Returns structured results for downstream processing
    """
    try:
        logger.info(f"Processing {len(request.keys)} images from bucket {request.bucket}")
        
        logger.info("Using AWS Rekognition service")
        # Step 1: Get raw detections from AWS Rekognition
        raw_results = await rekognition_service.detect_food_items(
            s3_keys=request.keys,
            bucket=request.bucket
        )
        
        logger.info(f"Rekognition returned {len(raw_results)} raw detections")
        
        # Step 2: Normalize raw results
        raw_items = [
            {
                'name': result.name,
                'confidence': result.confidence,
                'count': result.count
            }
            for result in raw_results
        ]
        
        normalized_items = food_normalizer.normalize_items(raw_items)
        
        logger.info(f"Normalization produced {len(normalized_items)} canonical items")
        
        # Step 3: Format response
        formatted_items = []
        for item in normalized_items:
            formatted_items.append({
                "name": item.canonical_name,
                "count": item.count,
                "confidence": round(item.confidence, 3),
                "raw_name": item.raw_name
            })
        
        # Calculate processing stats
        total_raw = len(raw_results)
        total_normalized = len(normalized_items)
        normalization_rate = (total_normalized / total_raw * 100) if total_raw > 0 else 0
        
        processing_stats = {
            "images_processed": len(request.keys),
            "raw_detections": total_raw,
            "normalized_items": total_normalized,
            "normalization_rate": round(normalization_rate, 1),
            "avg_confidence": round(
                sum(item.confidence for item in normalized_items) / len(normalized_items), 3
            ) if normalized_items else 0
        }
        
        # Prepare raw detections for debugging (optional)
        raw_detections = [
            {
                "name": result.name,
                "confidence": round(result.confidence, 3),
                "count": result.count
            }
            for result in raw_results
        ]
        
        response = VisionDetectResponse(
            items=formatted_items,
            raw_detections=raw_detections,
            processing_stats=processing_stats
        )
        
        logger.info(f"Successfully processed vision detection: {processing_stats}")
        return response
        
    except Exception as e:
        logger.error(f"Error in vision detection: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Vision detection failed: {str(e)}"
        )

# Simple analyze endpoint for frontend compatibility
class AnalyzeRequest(BaseModel):
    imageKeys: List[str]
    peopleCount: int
    inventory: Optional[List[Dict[str, Any]]] = None

class AnalyzeResponse(BaseModel):
    inventory: List[Dict[str, Any]]
    recipes: List[Dict[str, Any]]
    swapTips: List[Dict[str, Any]]
    totalCarbonImpact: float
    analysisTime: float

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_images(request: AnalyzeRequest):
    """Simple analyze endpoint for frontend compatibility"""
    try:
        # For now, return mock data since we don't have full AWS integration
        mock_inventory = [
            {
                "id": "1",
                "name": "Organic Tomatoes",
                "category": "Vegetables",
                "quantity": "6 pieces",
                "carbonImpact": "low",
                "confidence": 0.92
            },
            {
                "id": "2",
                "name": "Ground Beef",
                "category": "Meat",
                "quantity": "1 lb",
                "carbonImpact": "high",
                "confidence": 0.88
            },
            {
                "id": "3",
                "name": "Milk",
                "category": "Dairy",
                "quantity": "1 gallon",
                "carbonImpact": "medium",
                "confidence": 0.95
            }
        ]
        
        mock_recipes = [
            {
                "id": "1",
                "title": "Beef Bolognese",
                "description": "Classic Italian pasta with ground beef and tomatoes",
                "ingredients": ["Ground beef", "Tomatoes", "Onion", "Garlic", "Pasta"],
                "instructions": [
                    "Brown the ground beef in a large pan",
                    "Add diced onions and garlic",
                    "Add tomatoes and simmer for 20 minutes",
                    "Serve over cooked pasta"
                ],
                "carbonImpact": "high",
                "prepTime": 30,
                "servings": request.peopleCount,
                "imageUrl": "/api/placeholder/400/300"
            },
            {
                "id": "2",
                "title": "Tomato Basil Salad",
                "description": "Fresh and light salad with tomatoes and basil",
                "ingredients": ["Tomatoes", "Fresh basil", "Olive oil", "Salt", "Pepper"],
                "instructions": [
                    "Slice tomatoes",
                    "Chop fresh basil",
                    "Drizzle with olive oil",
                    "Season with salt and pepper"
                ],
                "carbonImpact": "low",
                "prepTime": 10,
                "servings": request.peopleCount,
                "imageUrl": "/api/placeholder/400/300"
            }
        ]
        
        mock_swap_tips = [
            {
                "id": "1",
                "original": "Ground Beef",
                "suggestion": "Lentils",
                "reason": "Plant-based protein with 90% less carbon footprint",
                "carbonSavings": 85
            }
        ]
        
        return AnalyzeResponse(
            inventory=mock_inventory,
            recipes=mock_recipes,
            swapTips=mock_swap_tips,
            totalCarbonImpact=2.3,
            analysisTime=8.5
        )
        
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Health check for vision service
@router.get("/vision/health")
async def vision_health():
    """Health check for vision detection service"""
    try:
        return {
            "status": "healthy",
            "service": "vision_detection",
            "rekognition_mode": "aws",
            "normalizer_loaded": len(food_normalizer.canonical_items) > 0,
            "canonical_items_count": len(food_normalizer.canonical_items),
            "aws_configured": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
