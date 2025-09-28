<<<<<<< HEAD
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Any
from app.services.rekog import analyze_images
from app.services.recipes_llm import generate_recipes
from app.services.carbon import calculate_carbon_impact
from app.services.normalize import normalize_ingredients
import time

router = APIRouter()

class AnalysisRequest(BaseModel):
    imageKeys: List[str]
    peopleCount: int
    inventory: Optional[List[Any]] = None

class AnalysisResponse(BaseModel):
    inventory: List[Any]
    recipes: List[Any]
    swapTips: List[Any]
    totalCarbonImpact: float
    analysisTime: float

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_fridge_images(request: AnalysisRequest):
    """Analyze uploaded fridge images and return insights"""
    start_time = time.time()
    
    try:
        # Step 1: Analyze images using AWS Rekognition
        detected_items = await analyze_images(request.imageKeys)
        
        # Step 2: Normalize ingredient names
        normalized_inventory = normalize_ingredients(detected_items)
        
        # Step 3: Calculate carbon impact
        carbon_data = calculate_carbon_impact(normalized_inventory)
        
        # Step 4: Generate recipes based on inventory and people count
        recipes = generate_recipes(normalized_inventory, request.peopleCount)
        
        # Step 5: Generate swap tips for high-carbon items
        swap_tips = []
        for item in normalized_inventory:
            if item.get('carbonImpact') == 'high':
                swap_tips.append({
                    'id': f"swap_{item['id']}",
                    'original': item['name'],
                    'suggestion': get_eco_alternative(item['name']),
                    'reason': f"Reduce carbon footprint by {get_carbon_savings(item['name'])}%",
                    'carbonSavings': get_carbon_savings(item['name'])
                })
        
        analysis_time = time.time() - start_time
        
        return AnalysisResponse(
            inventory=normalized_inventory,
            recipes=recipes,
            swapTips=swap_tips,
            totalCarbonImpact=sum(item.get('carbonValue', 0) for item in normalized_inventory),
            analysisTime=round(analysis_time, 2)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

def get_eco_alternative(item_name: str) -> str:
    """Get eco-friendly alternative for high-carbon items"""
    alternatives = {
        'beef': 'Lentils',
        'ground beef': 'Lentils',
        'steak': 'Mushrooms',
        'lamb': 'Tofu',
        'pork': 'Chickpeas',
        'chicken': 'Quinoa',
        'dairy': 'Oat milk',
        'milk': 'Almond milk',
        'cheese': 'Nutritional yeast'
    }
    
    item_lower = item_name.lower()
    for key, alternative in alternatives.items():
        if key in item_lower:
            return alternative
    
    return 'Plant-based alternative'

def get_carbon_savings(item_name: str) -> int:
    """Get carbon savings percentage for alternatives"""
    savings = {
        'beef': 85,
        'ground beef': 85,
        'steak': 80,
        'lamb': 90,
        'pork': 75,
        'chicken': 70,
        'dairy': 60,
        'milk': 65,
        'cheese': 55
    }
    
    item_lower = item_name.lower()
    for key, saving in savings.items():
        if key in item_lower:
            return saving
    
    return 50
=======
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
>>>>>>> 85cfca634be5e8ef45cb4dc555da76c75924dfa3
