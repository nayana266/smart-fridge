from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import os
import time
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
        
        if raw_results is None:
            logger.warning("Rekognition returned None, using empty results")
            raw_results = []
        
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
    """Full analysis pipeline using real AWS Rekognition and recipe generation"""
    try:
        logger.info(f"Starting full analysis for {len(request.imageKeys)} images, {request.peopleCount} people")
        
        # Step 1: Vision Detection using AWS Rekognition
        vision_request = VisionDetectRequest(
            keys=request.imageKeys,
            bucket="smart-fridge-images-nayana"
        )
        
        vision_response = await detect_food_items(vision_request)
        logger.info(f"Vision detection found {len(vision_response.items)} items")
        
        # Step 2: Convert vision results to inventory format and combine with manual inventory
        inventory = []
        
        # Add detected items from vision
        for item in vision_response.items:
            inventory.append({
                "id": f"detected-{item['name']}-{int(time.time())}",
                "name": item['name'],
                "category": "Detected",
                "quantity": f"{item['count']} piece(s)",
                "carbonImpact": "medium",  # Default, will be updated by planner
                "confidence": item['confidence']
            })
        
        # Add manually added items from frontend
        if request.inventory:
            logger.info(f"Adding {len(request.inventory)} manually added items to inventory")
            for item in request.inventory:
                # Skip items that might be duplicates of detected items
                is_duplicate = any(
                    detected['name'].lower() == item['name'].lower() 
                    for detected in vision_response.items
                )
                if not is_duplicate:
                    inventory.append({
                        "id": item.get('id', f"manual-{item['name']}-{int(time.time())}"),
                        "name": item['name'],
                        "category": item.get('category', 'Manual'),
                        "quantity": item.get('quantity', '1 piece(s)'),
                        "carbonImpact": item.get('carbonImpact', 'medium'),
                        "confidence": item.get('confidence', 1.0)  # Manual items have high confidence
                    })
                    logger.info(f"Added manual item: {item['name']}")
        
        logger.info(f"Final inventory has {len(inventory)} items total")
        
        # Step 3: Get carbon impact and swap suggestions from planner
        detected_food_names = [item['name'] for item in inventory]
        
        try:
            # Import plan logic
            from app.routes.plan import plan as plan_logic
            plan_response = plan_logic(
                items=detected_food_names,
                people=request.peopleCount,
                flags=[],
                demo=False
            )
            
            # Update inventory with carbon impact data
            for i, inventory_item in enumerate(inventory):
                if i < len(plan_response.inventory):
                    plan_item = plan_response.inventory[i]
                    inventory_item["carbonImpact"] = plan_item.impact
                    inventory_item["category"] = plan_item.category
            
            # Convert swap suggestions
            swap_tips = []
            for swap in plan_response.swaps:
                swap_tips.append({
                    "id": f"swap-{swap.from_item}",
                    "original": swap.from_item,
                    "suggestion": swap.to,
                    "reason": swap.why,
                    "carbonSavings": swap.reduction
                })
            
            total_carbon_impact = plan_response.score
            
        except Exception as e:
            logger.warning(f"Planner failed, using defaults: {e}")
            swap_tips = []
            total_carbon_impact = 50  # Default score
        
        # Step 4: Generate recipes using LLM
        recipes = []
        if detected_food_names:  # Only generate recipes if we have detected items
            try:
                from app.services.recipes_llm import generate as generate_recipes_llm
                from app.shared.models.recipe import LLMContext
                
                llm_context = LLMContext(
                    pantry=detected_food_names,
                    people=request.peopleCount,
                    flags=[]
                )
                
                generated_recipes = generate_recipes_llm(llm_context, demo=False)
                
                # Convert to frontend format
                for recipe in generated_recipes:
                    recipes.append({
                        "id": f"recipe-{recipe.title.lower().replace(' ', '-')}",
                        "title": recipe.title,
                        "description": f"Generated recipe using {', '.join(detected_food_names[:3])}",
                        "ingredients": [ing.name for ing in recipe.ingredients],
                        "instructions": [step.text for step in recipe.steps],
                        "carbonImpact": "medium",
                        "prepTime": 30,
                        "servings": request.peopleCount,
                        "imageUrl": "/api/placeholder/400/300"
                    })
                    
            except Exception as e:
                logger.warning(f"Recipe generation failed: {e}")
                # Fallback to simple recipes
                recipes = [{
                    "id": "recipe-fallback",
                    "title": f"Simple {detected_food_names[0]} Recipe",
                    "description": f"Quick recipe using {detected_food_names[0]}",
                    "ingredients": detected_food_names[:3],
                    "instructions": [
                        f"Prepare {detected_food_names[0]}",
                        "Cook according to your preference",
                        "Season and serve"
                    ],
                    "carbonImpact": "medium",
                    "prepTime": 15,
                    "servings": request.peopleCount,
                    "imageUrl": "/api/placeholder/400/300"
                }]
        else:
            # No items detected - provide helpful message
            logger.info("No food items detected in the uploaded images")
            recipes = [{
                "id": "no-items-detected",
                "title": "No Items Detected",
                "description": "We couldn't detect any food items in your images. Try uploading clearer images with visible food items.",
                "ingredients": [],
                "instructions": [
                    "Make sure your images show food items clearly",
                    "Ensure good lighting in your photos",
                    "Try taking photos from different angles",
                    "Upload images in JPEG format for best results"
                ],
                "carbonImpact": "low",
                "prepTime": 0,
                "servings": request.peopleCount,
                "imageUrl": "/api/placeholder/400/300"
            }]
        
        return AnalyzeResponse(
            inventory=inventory,
            recipes=recipes,
            swapTips=swap_tips,
            totalCarbonImpact=total_carbon_impact,
            analysisTime=time.time()
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
