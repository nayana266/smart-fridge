from typing import List, Dict, Any
import re

def normalize_ingredients(detected_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Normalize and clean up detected ingredients"""
    normalized_items = []
    
    for item in detected_items:
        normalized_item = item.copy()
        
        # Normalize name
        normalized_item['name'] = normalize_name(item['name'])
        
        # Ensure all required fields exist
        if 'id' not in normalized_item:
            normalized_item['id'] = f"item_{len(normalized_items) + 1}"
        
        if 'category' not in normalized_item:
            normalized_item['category'] = 'Other'
        
        if 'quantity' not in normalized_item:
            normalized_item['quantity'] = '1 item'
        
        if 'confidence' not in normalized_item:
            normalized_item['confidence'] = 0.8
        
        if 'carbonImpact' not in normalized_item:
            normalized_item['carbonImpact'] = 'low'
        
        if 'carbonValue' not in normalized_item:
            normalized_item['carbonValue'] = 1.0
        
        normalized_items.append(normalized_item)
    
    # Remove duplicates based on name similarity
    unique_items = remove_duplicates(normalized_items)
    
    return unique_items

def normalize_name(name: str) -> str:
    """Normalize ingredient names"""
    # Convert to lowercase
    name = name.lower().strip()
    
    # Remove common prefixes/suffixes
    name = re.sub(r'^(fresh|organic|raw|ripe|green|red|yellow)\s+', '', name)
    name = re.sub(r'\s+(fresh|organic|raw|ripe|green|red|yellow)$', '', name)
    
    # Standardize common variations
    name_mappings = {
        'tomatoes': 'tomato',
        'carrots': 'carrot',
        'onions': 'onion',
        'apples': 'apple',
        'bananas': 'banana',
        'oranges': 'orange',
        'potatoes': 'potato',
        'broccoli': 'broccoli',
        'lettuce': 'lettuce',
        'spinach': 'spinach',
        'chicken breast': 'chicken',
        'ground beef': 'beef',
        'beef steak': 'beef',
        'milk carton': 'milk',
        'cheese block': 'cheese',
        'bread loaf': 'bread',
        'pasta box': 'pasta'
    }
    
    for key, value in name_mappings.items():
        if key in name:
            name = value
            break
    
    # Capitalize first letter
    name = name.capitalize()
    
    return name

def remove_duplicates(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate items based on name similarity"""
    unique_items = []
    seen_names = set()
    
    for item in items:
        name = item['name'].lower()
        
        # Check if we've seen a similar name
        is_duplicate = False
        for seen_name in seen_names:
            if name in seen_name or seen_name in name:
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_items.append(item)
            seen_names.add(name)
    
    return unique_items
