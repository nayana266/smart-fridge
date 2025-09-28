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
