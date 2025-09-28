import boto3
import asyncio
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging
from botocore.exceptions import ClientError, BotoCoreError
import json

logger = logging.getLogger(__name__)

@dataclass
class DetectionResult:
    name: str
    count: int
    confidence: float

class RekognitionService:
    def __init__(self, region_name: str = "us-east-1"):
        self.rekognition = boto3.client('rekognition', region_name=region_name)
        self.rate_limit_tokens = 10  # Simple token bucket
        self.max_tokens = 10
        self.last_refill = time.time()
        self.refill_rate = 1.0  # tokens per second
        
    async def _acquire_token(self):
        """Simple token bucket rate limiting"""
        current_time = time.time()
        time_passed = current_time - self.last_refill
        
        # Refill tokens based on time passed
        self.rate_limit_tokens = min(
            self.max_tokens,
            self.rate_limit_tokens + time_passed * self.refill_rate
        )
        self.last_refill = current_time
        
        # Wait if no tokens available
        if self.rate_limit_tokens < 1:
            wait_time = 1.0 / self.refill_rate
            logger.info(f"Rate limit hit, waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
            self.rate_limit_tokens = 1
        
        self.rate_limit_tokens -= 1
    
    async def _detect_labels_with_retry(self, bucket: str, key: str, max_retries: int = 3) -> List[Dict[str, Any]]:
        """Detect labels from S3 image with exponential backoff retry"""
        for attempt in range(max_retries):
            try:
                await self._acquire_token()
                
                response = self.rekognition.detect_labels(
                    Image={
                        'S3Object': {
                            'Bucket': bucket,
                            'Name': key
                        }
                    },
                    MaxLabels=50,
                    MinConfidence=0.45
                )
                
                return response.get('Labels', [])
                
            except (ClientError, BotoCoreError) as e:
                if attempt == max_retries - 1:
                    logger.error(f"Failed to detect labels for {key} after {max_retries} attempts: {e}")
                    raise
                
                # Exponential backoff
                wait_time = 2 ** attempt
                logger.warning(f"Attempt {attempt + 1} failed for {key}, retrying in {wait_time}s: {e}")
                await asyncio.sleep(wait_time)
        
        return []
    
    async def detect_food_items(self, s3_keys: List[str], bucket: str = "smart-fridge-images") -> List[DetectionResult]:
        """
        Detect food items from multiple S3 images
        Returns normalized results with counts and confidence scores
        """
        all_labels = []
        
        # Process images concurrently but with rate limiting
        tasks = []
        for key in s3_keys:
            task = self._detect_labels_with_retry(bucket, key)
            tasks.append(task)
        
        # Execute all detection tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to process image {s3_keys[i]}: {result}")
                continue
            
            for label in result:
                all_labels.append({
                    'name': label['Name'].lower(),
                    'confidence': label['Confidence']
                })
        
        # Group and count items
        item_counts = {}
        for label in all_labels:
            name = label['name']
            confidence = label['confidence']
            
            if name in item_counts:
                # Keep highest confidence
                item_counts[name] = max(item_counts[name], confidence)
            else:
                item_counts[name] = confidence
        
        # Convert to DetectionResult objects with food filtering
        detection_results = []
        
        # Food-related keywords to filter for (expanded for pantry scenarios)
        food_keywords = [
            'food', 'fruit', 'vegetable', 'meat', 'dairy', 'drink', 'beverage',
            'bread', 'milk', 'cheese', 'egg', 'eggs', 'chicken', 'beef', 'pork',
            'apple', 'banana', 'orange', 'tomato', 'carrot', 'lettuce', 'spinach',
            'broccoli', 'pepper', 'mushroom', 'onion', 'garlic', 'rice', 'pasta',
            'potato', 'fish', 'salmon', 'tofu', 'bean', 'lentil', 'nut', 'avocado',
            'olive', 'oil', 'butter', 'salt', 'pepper', 'honey', 'sugar', 'flour',
            'cereal', 'snack', 'cracker', 'chip', 'popcorn', 'juice', 'soda',
            'yogurt', 'ice cream', 'frozen', 'canned', 'sauce', 'condiment',
            'spice', 'herb', 'grain', 'seed', 'berry', 'citrus', 'leafy green',
            'protein', 'carbohydrate', 'vitamin', 'organic', 'fresh', 'raw',
            'grape', 'grapes', 'peach', 'apricot', 'plum', 'pear', 'lemon', 'lime',
            'strawberry', 'blueberry', 'raspberry', 'blackberry', 'cherry',
            'pepper', 'bell pepper', 'sausage', 'salami', 'ham', 'bacon',
            'pie', 'tart', 'quiche', 'cake', 'cookie', 'cracker'
        ]
        
        for name, confidence in item_counts.items():
            # Only include items that are likely food-related
            is_food = any(keyword in name.lower() for keyword in food_keywords)
            
            if is_food:
                # Use dynamic confidence thresholds based on item type
                confidence_threshold = self._get_confidence_threshold(name, confidence)
                
                if confidence >= confidence_threshold:
                    detection_results.append(DetectionResult(
                        name=name,
                        count=1,  # Rekognition doesn't provide exact counts, assume 1 per detection
                        confidence=confidence / 100.0  # Convert to 0-1 scale
                    ))
    
    def _get_confidence_threshold(self, name: str, confidence: float) -> float:
        """
        Dynamic confidence thresholds based on item type and context.
        This helps capture more items while maintaining quality.
        """
        name_lower = name.lower()
        
        # High confidence items (common, easily identifiable)
        high_confidence_items = [
            'banana', 'apple', 'orange', 'milk', 'bread', 'egg', 'cheese', 
            'chicken', 'beef', 'rice', 'pasta', 'tomato', 'carrot', 'lettuce'
        ]
        
        # Medium confidence items (somewhat identifiable)
        medium_confidence_items = [
            'fruit', 'vegetable', 'meat', 'dairy', 'beverage', 'juice', 
            'pepper', 'onion', 'garlic', 'potato', 'fish', 'yogurt'
        ]
        
        # Lower confidence items (generic or harder to identify)
        lower_confidence_items = [
            'food', 'snack', 'sauce', 'condiment', 'spice', 
            'herb', 'grain', 'seed', 'berry', 'citrus'
        ]
        
        # Items to exclude (too generic)
        excluded_items = [
            'produce'  # Too generic, doesn't add value
        ]
        
        # Special cases for items that are often missed
        special_cases = [
            'peach', 'apricot', 'plum', 'grape', 'grapes', 'strawberry', 
            'blueberry', 'raspberry', 'lemon', 'lime', 'kiwi', 'papaya',
            'bell pepper', 'broccoli', 'spinach', 'mushroom', 'avocado',
            'sausage', 'salami', 'ham', 'bacon', 'pie', 'tart', 'quiche'
        ]
        
        # Check if item should be excluded
        if any(item in name_lower for item in excluded_items):
            return 100.0  # Effectively exclude by setting impossible threshold
        
        if any(item in name_lower for item in high_confidence_items):
            return 60.0  # High threshold for common items
        elif any(item in name_lower for item in medium_confidence_items):
            return 50.0  # Medium threshold
        elif any(item in name_lower for item in special_cases):
            return 45.0  # Lower threshold for often-missed items
        elif any(item in name_lower for item in lower_confidence_items):
            return 55.0  # Higher threshold for generic terms
        else:
            return 50.0  # Default threshold

# Global instance
rekognition_service = RekognitionService()
