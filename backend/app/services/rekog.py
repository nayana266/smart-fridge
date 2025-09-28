import boto3
import os
from typing import List, Dict, Any
import json

# Initialize Rekognition client
rekognition_client = boto3.client(
    'rekognition',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'your-access-key'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'your-secret-key'),
    region_name=os.getenv('AWS_REGION', 'us-east-1')
)

BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'smart-fridge-uploads')

async def analyze_images(image_keys: List[str]) -> List[Dict[str, Any]]:
    """Analyze images using AWS Rekognition to detect food items"""
    detected_items = []
    
    for image_key in image_keys:
        try:
            # Use Rekognition to detect labels
            response = rekognition_client.detect_labels(
                Image={'S3Object': {'Bucket': BUCKET_NAME, 'Name': image_key}},
                MaxLabels=20,
                MinConfidence=70
            )
            
            # Filter for food-related labels
            food_labels = []
            for label in response['Labels']:
                if is_food_item(label['Name']):
                    food_labels.append({
                        'name': label['Name'],
                        'confidence': label['Confidence']
                    })
            
            # Add detected items to inventory
            for item in food_labels:
                detected_items.append({
                    'id': f"{image_key}_{item['name']}",
                    'name': item['name'],
                    'confidence': item['confidence'] / 100,
                    'source_image': image_key,
                    'category': categorize_food(item['name']),
                    'quantity': estimate_quantity(item['name']),
                    'carbonImpact': get_carbon_impact(item['name']),
                    'carbonValue': get_carbon_value(item['name'])
                })
                
        except Exception as e:
            print(f"Error analyzing image {image_key}: {e}")
            continue
    
    return detected_items

def is_food_item(label_name: str) -> bool:
    """Check if a label represents a food item"""
    food_keywords = [
        'food', 'fruit', 'vegetable', 'meat', 'dairy', 'bread', 'grain',
        'apple', 'banana', 'orange', 'tomato', 'carrot', 'lettuce', 'onion',
        'chicken', 'beef', 'pork', 'fish', 'milk', 'cheese', 'yogurt',
        'bread', 'pasta', 'rice', 'potato', 'broccoli', 'spinach'
    ]
    
    label_lower = label_name.lower()
    return any(keyword in label_lower for keyword in food_keywords)

def categorize_food(item_name: str) -> str:
    """Categorize food items"""
    item_lower = item_name.lower()
    
    if any(word in item_lower for word in ['apple', 'banana', 'orange', 'grape', 'berry']):
        return 'Fruits'
    elif any(word in item_lower for word in ['tomato', 'carrot', 'lettuce', 'onion', 'broccoli']):
        return 'Vegetables'
    elif any(word in item_lower for word in ['chicken', 'beef', 'pork', 'fish', 'meat']):
        return 'Meat'
    elif any(word in item_lower for word in ['milk', 'cheese', 'yogurt', 'butter']):
        return 'Dairy'
    elif any(word in item_lower for word in ['bread', 'pasta', 'rice', 'grain']):
        return 'Grains'
    else:
        return 'Other'

def estimate_quantity(item_name: str) -> str:
    """Estimate quantity based on item type"""
    item_lower = item_name.lower()
    
    if any(word in item_lower for word in ['apple', 'banana', 'orange']):
        return '1-3 pieces'
    elif any(word in item_lower for word in ['tomato', 'carrot', 'onion']):
        return '2-4 pieces'
    elif any(word in item_lower for word in ['lettuce', 'spinach', 'broccoli']):
        return '1 bunch'
    elif any(word in item_lower for word in ['milk', 'juice']):
        return '1 container'
    elif any(word in item_lower for word in ['bread', 'pasta']):
        return '1 package'
    else:
        return '1 item'

def get_carbon_impact(item_name: str) -> str:
    """Get carbon impact level"""
    item_lower = item_name.lower()
    
    high_carbon = ['beef', 'lamb', 'pork', 'cheese']
    medium_carbon = ['chicken', 'fish', 'milk', 'yogurt']
    
    if any(word in item_lower for word in high_carbon):
        return 'high'
    elif any(word in item_lower for word in medium_carbon):
        return 'medium'
    else:
        return 'low'

def get_carbon_value(item_name: str) -> float:
    """Get carbon value in kg CO2 equivalent"""
    item_lower = item_name.lower()
    
    carbon_values = {
        'beef': 27.0,
        'lamb': 21.0,
        'pork': 12.0,
        'cheese': 11.0,
        'chicken': 6.9,
        'fish': 6.0,
        'milk': 3.2,
        'yogurt': 3.2,
        'eggs': 4.2,
        'rice': 4.0,
        'bread': 1.4,
        'pasta': 1.4,
        'tomato': 2.0,
        'apple': 0.4,
        'banana': 0.7,
        'orange': 0.9
    }
    
    for key, value in carbon_values.items():
        if key in item_lower:
            return value
    
    return 1.0  # Default value
