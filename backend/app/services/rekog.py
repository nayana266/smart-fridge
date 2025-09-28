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
    def __init__(self, region_name: str = "us-east-2"):
        # Use environment variables or default credential chain
        import os
        self.rekognition = boto3.client(
            'rekognition',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=region_name
        )
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
                    MaxLabels=10,  # Even more focused on top detections
                    MinConfidence=0.80  # Much higher threshold for accuracy
                )
                
                return response.get('Labels', [])
                
            except (ClientError, BotoCoreError) as e:
                if attempt == max_retries - 1:
                    logger.error(f"Failed to detect labels for {key} after {max_retries} attempts: {e}")
                    logger.error(f"Error type: {type(e).__name__}")
                    raise
                
                # Exponential backoff
                wait_time = 2 ** attempt
                logger.warning(f"Attempt {attempt + 1} failed for {key}, retrying in {wait_time}s: {e}")
                await asyncio.sleep(wait_time)
        
        return []
    
    async def detect_food_items(self, s3_keys: List[str], bucket: str = "smart-fridge-images-nayana") -> List[DetectionResult]:
        """
        Detect food items from multiple S3 images
        Returns normalized results with counts and confidence scores
        """
        logger.info(f"Starting detect_food_items for {len(s3_keys)} images in bucket {bucket}")
        logger.info(f"Image keys: {s3_keys}")
        all_labels = []
        
        # Process images concurrently but with rate limiting
        tasks = []
        for key in s3_keys:
            task = self._detect_labels_with_retry(bucket, key)
            tasks.append(task)
        
        # Execute all detection tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        logger.info(f"Got {len(results)} results from AWS Rekognition")
        
        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to process image {s3_keys[i]}: {result}")
                continue
            
            logger.info(f"Processing {len(result)} labels from image {s3_keys[i]}")
            for label in result:
                all_labels.append({
                    'name': label['Name'].lower(),
                    'confidence': label['Confidence']
                })
                logger.info(f"Added label: {label['Name']} (confidence: {label['Confidence']:.1f}%)")
        
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
        
        # Specific food items only - no generic terms like "food", "fruit"
        specific_foods = [
                   # Proteins
                   'egg', 'eggs', 'chicken', 'beef', 'pork', 'fish', 'salmon', 'tofu', 
                   'bean', 'lentil', 'nut', 'nuts', 'almond', 'walnut', 'cashew',
                   'sausage', 'salami', 'ham', 'bacon', 'turkey', 'lamb',
                   
                   # Dairy
                   'milk', 'cheese', 'yogurt', 'butter', 'cream', 'cottage cheese',
                   
                   # Fruits (specific)
                   'apple', 'banana', 'orange', 'grape', 'grapes', 'peach', 'apricot', 
                   'plum', 'pear', 'lemon', 'lime', 'strawberry', 'blueberry', 
                   'raspberry', 'blackberry', 'cherry', 'kiwi', 'mango', 'pineapple',
                   
                   # Vegetables (specific)
                   'tomato', 'carrot', 'lettuce', 'spinach', 'broccoli', 'pepper', 
                   'bell pepper', 'mushroom', 'onion', 'garlic', 'potato', 'sweet potato',
                   'cucumber', 'celery', 'corn', 'peas', 'beans', 'cabbage', 'cauliflower',
                   
                   # Grains & carbs
                   'bread', 'rice', 'pasta', 'noodle', 'oats', 'cereal', 'flour', 'quinoa',
                   
                   # Other specific foods
                   'pizza', 'sandwich', 'burger', 'soup', 'salad', 'pasta', 'pancake',
                   'cookie', 'cake', 'pie', 'tart', 'muffin', 'bagel', 'cracker',
                   'olive', 'olive oil', 'avocado', 'honey', 'sugar', 'salt', 'vinegar'
               ]
        
        for name, confidence in item_counts.items():
            # Only include specific food items - no generic terms
            is_specific_food = any(food in name.lower() for food in specific_foods)
            logger.info(f"Processing item: {name} (confidence: {confidence:.1f}%, is_specific_food: {is_specific_food})")
            
            if is_specific_food:
                # Use dynamic confidence thresholds based on item type
                confidence_threshold = self._get_confidence_threshold(name, confidence)
                
                if confidence >= confidence_threshold:
                    detection_results.append(DetectionResult(
                        name=name,
                        count=1,  # Rekognition doesn't provide exact counts, assume 1 per detection
                        confidence=confidence / 100.0  # Convert to 0-1 scale
                    ))
        
        logger.info(f"Returning {len(detection_results)} detection results")
        return detection_results
    
    def _get_confidence_threshold(self, name: str, confidence: float) -> float:
        """
        Dynamic confidence thresholds based on item type and context.
        This helps capture more items while maintaining quality.
        """
        name_lower = name.lower()
        
        # High confidence items (common, easily identifiable)
        high_confidence_items = [
            'banana', 'apple', 'orange', 'milk', 'bread', 'egg', 'eggs', 'cheese', 
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
        
        # Special case for eggs - very high confidence required
        if 'egg' in name_lower:
            return 85.0  # Very high threshold for eggs specifically
            
        if any(item in name_lower for item in high_confidence_items):
            return 75.0  # High threshold for accuracy
        elif any(item in name_lower for item in medium_confidence_items):
            return 65.0  # High threshold
        elif any(item in name_lower for item in special_cases):
            return 60.0  # High threshold for special items
        elif any(item in name_lower for item in lower_confidence_items):
            return 75.0  # Very high threshold for generic terms
        else:
            return 70.0  # High default threshold

# Global instance
rekognition_service = RekognitionService()
