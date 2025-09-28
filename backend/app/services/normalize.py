<<<<<<< HEAD
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
=======
import json
import os
import logging
from typing import List, Dict, Optional, Tuple
from rapidfuzz import fuzz, process
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class NormalizedItem:
    canonical_name: str
    raw_name: str
    confidence: float
    count: int

class FoodNormalizer:
    def __init__(self, aliases_file_path: str = None):
        if aliases_file_path is None:
            # Default path relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            aliases_file_path = os.path.join(current_dir, "../../../data/ingredient_aliases.json")
        
        self.aliases = self._load_aliases(aliases_file_path)
        self.canonical_items = list(self.aliases.keys())
    
    def _load_aliases(self, file_path: str) -> Dict[str, List[str]]:
        """Load ingredient aliases from JSON file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Aliases file not found at {file_path}, using default mappings")
            return self._get_default_aliases()
    
    def _get_default_aliases(self) -> Dict[str, List[str]]:
        """Default food aliases mapping"""
        return {
            "beef": ["beef", "steak", "ground beef", "hamburger", "roast beef"],
            "chicken": ["chicken", "chicken breast", "chicken thigh", "poultry"],
            "pork": ["pork", "bacon", "ham", "pork chop", "sausage"],
            "fish": ["fish", "salmon", "tuna", "cod", "tilapia", "seafood"],
            "tofu": ["tofu", "soy", "bean curd"],
            "milk": ["milk", "dairy milk", "cow milk"],
            "cheese": ["cheese", "cheddar", "mozzarella", "parmesan", "dairy"],
            "eggs": ["eggs", "egg", "chicken eggs"],
            "bread": ["bread", "loaf", "sandwich bread", "sliced bread"],
            "rice": ["rice", "white rice", "brown rice", "grain"],
            "pasta": ["pasta", "noodles", "spaghetti", "macaroni"],
            "potatoes": ["potatoes", "potato", "russet potato", "sweet potato"],
            "onions": ["onions", "onion", "yellow onion", "white onion"],
            "carrots": ["carrots", "carrot", "baby carrots"],
            "tomatoes": ["tomatoes", "tomato", "cherry tomatoes", "canned tomatoes"],
            "lettuce": ["lettuce", "leaf lettuce", "iceberg", "romaine"],
            "spinach": ["spinach", "baby spinach", "leafy greens"],
            "broccoli": ["broccoli", "broccoli florets"],
            "bell peppers": ["bell peppers", "pepper", "red pepper", "green pepper"],
            "mushrooms": ["mushrooms", "mushroom", "button mushrooms"],
            "bananas": ["bananas", "banana"],
            "apples": ["apples", "apple", "red apple", "green apple"],
            "oranges": ["oranges", "orange", "citrus"],
            "lemons": ["lemons", "lemon", "citrus"],
            "limes": ["limes", "lime", "citrus"],
            "yogurt": ["yogurt", "greek yogurt", "dairy"],
            "butter": ["butter", "dairy butter", "salted butter"],
            "olive oil": ["olive oil", "extra virgin olive oil", "oil"],
            "vegetable oil": ["vegetable oil", "canola oil", "cooking oil"],
            "salt": ["salt", "sea salt", "table salt"],
            "pepper": ["pepper", "black pepper", "ground pepper"],
            "garlic": ["garlic", "garlic cloves", "minced garlic"],
            "ginger": ["ginger", "fresh ginger", "ginger root"],
            "soy sauce": ["soy sauce", "soy"],
            "vinegar": ["vinegar", "white vinegar", "balsamic vinegar"],
            "honey": ["honey", "raw honey"],
            "sugar": ["sugar", "white sugar", "granulated sugar"],
            "flour": ["flour", "all purpose flour", "white flour"],
            "lentils": ["lentils", "red lentils", "green lentils", "legumes"],
            "beans": ["beans", "black beans", "kidney beans", "legumes"],
            "chickpeas": ["chickpeas", "garbanzo beans", "legumes"],
            "quinoa": ["quinoa", "grain", "superfood"],
            "oats": ["oats", "oatmeal", "rolled oats", "grain"],
            "nuts": ["nuts", "almonds", "walnuts", "cashews", "tree nuts"],
            "avocado": ["avocado", "avocados", "guacamole"],
            "coconut": ["coconut", "coconut milk", "coconut oil"],
            "chocolate": ["chocolate", "dark chocolate", "cocoa", "candy"]
        }
    
    def normalize_item(self, raw_name: str, confidence: float, count: int = 1) -> Optional[NormalizedItem]:
        """
        Normalize a raw food item name to canonical form using fuzzy matching
        
        Args:
            raw_name: Raw name from Rekognition
            confidence: Confidence score from Rekognition
            count: Number of items detected
            
        Returns:
            NormalizedItem or None if no good match found
        """
        raw_name = raw_name.lower().strip()
        
        # First try exact match in aliases
        for canonical, aliases in self.aliases.items():
            if raw_name in aliases:
                return NormalizedItem(
                    canonical_name=canonical,
                    raw_name=raw_name,
                    confidence=confidence,
                    count=count
                )
        
        # Try fuzzy matching with high threshold
        best_match = process.extractOne(
            raw_name,
            self.canonical_items,
            scorer=fuzz.token_sort_ratio,
            score_cutoff=75  # Require 75% similarity
        )
        
        if best_match:
            canonical_name, score, _ = best_match
            # Adjust confidence based on fuzzy match quality
            adjusted_confidence = confidence * (score / 100.0)
            
            return NormalizedItem(
                canonical_name=canonical_name,
                raw_name=raw_name,
                confidence=adjusted_confidence,
                count=count
            )
        
        # Try partial matching for compound names
        for canonical, aliases in self.aliases.items():
            for alias in aliases:
                if fuzz.partial_ratio(raw_name, alias) >= 80:
                    return NormalizedItem(
                        canonical_name=canonical,
                        raw_name=raw_name,
                        confidence=confidence * 0.9,  # Slight penalty for partial match
                        count=count
                    )
        
        return None
    
    def normalize_items(self, raw_items: List[Dict[str, any]]) -> List[NormalizedItem]:
        """
        Normalize a list of raw food items
        
        Args:
            raw_items: List of dicts with 'name', 'confidence', 'count' keys
            
        Returns:
            List of NormalizedItem objects
        """
        normalized = []
        
        for item in raw_items:
            normalized_item = self.normalize_item(
                raw_name=item.get('name', ''),
                confidence=item.get('confidence', 0.0),
                count=item.get('count', 1)
            )
            
            if normalized_item:
                normalized.append(normalized_item)
        
        # Merge duplicates (same canonical name)
        merged = {}
        for item in normalized:
            key = item.canonical_name
            if key in merged:
                # Keep higher confidence, sum counts
                if item.confidence > merged[key].confidence:
                    merged[key].confidence = item.confidence
                merged[key].count += item.count
            else:
                merged[key] = item
        
        return list(merged.values())

# Global instance
food_normalizer = FoodNormalizer()
>>>>>>> 85cfca634be5e8ef45cb4dc555da76c75924dfa3
