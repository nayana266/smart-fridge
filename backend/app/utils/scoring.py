from typing import List, Dict, Any
import math

def calculate_confidence_score(detected_items: List[Dict[str, Any]]) -> float:
    """Calculate overall confidence score for detected items"""
    if not detected_items:
        return 0.0
    
    total_confidence = sum(item.get('confidence', 0) for item in detected_items)
    average_confidence = total_confidence / len(detected_items)
    
    # Boost score if we have multiple items
    item_count_boost = min(len(detected_items) * 0.05, 0.2)
    
    return min(average_confidence + item_count_boost, 1.0)

def calculate_sustainability_score(inventory: List[Dict[str, Any]]) -> float:
    """Calculate sustainability score based on carbon impact"""
    if not inventory:
        return 0.0
    
    total_carbon = sum(item.get('carbonValue', 1.0) for item in inventory)
    high_carbon_count = sum(1 for item in inventory if item.get('carbonImpact') == 'high')
    low_carbon_count = sum(1 for item in inventory if item.get('carbonImpact') == 'low')
    
    # Base score starts at 50%
    base_score = 0.5
    
    # Boost for low-carbon items
    low_carbon_boost = (low_carbon_count / len(inventory)) * 0.3
    
    # Penalty for high-carbon items
    high_carbon_penalty = (high_carbon_count / len(inventory)) * 0.2
    
    sustainability_score = base_score + low_carbon_boost - high_carbon_penalty
    
    return max(0.0, min(sustainability_score, 1.0))

def calculate_nutrition_score(inventory: List[Dict[str, Any]]) -> float:
    """Calculate nutrition score based on food categories"""
    if not inventory:
        return 0.0
    
    category_scores = {
        'Fruits': 0.9,
        'Vegetables': 0.9,
        'Grains': 0.7,
        'Dairy': 0.6,
        'Meat': 0.5,
        'Other': 0.4
    }
    
    total_score = 0
    for item in inventory:
        category = item.get('category', 'Other')
        score = category_scores.get(category, 0.4)
        total_score += score
    
    return total_score / len(inventory)

def get_overall_health_score(inventory: List[Dict[str, Any]]) -> Dict[str, float]:
    """Get overall health and sustainability scores"""
    return {
        'confidence': calculate_confidence_score(inventory),
        'sustainability': calculate_sustainability_score(inventory),
        'nutrition': calculate_nutrition_score(inventory),
        'overall': (
            calculate_confidence_score(inventory) * 0.3 +
            calculate_sustainability_score(inventory) * 0.4 +
            calculate_nutrition_score(inventory) * 0.3
        )
    }
