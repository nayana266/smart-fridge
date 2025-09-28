from typing import List, Dict, Any
import random

def generate_recipes(inventory: List[Dict[str, Any]], people_count: int) -> List[Dict[str, Any]]:
    """Generate recipe recommendations based on inventory and people count"""
    
    # Sample recipe database
    recipe_database = [
        {
            'id': '1',
            'title': 'Mediterranean Pasta',
            'description': 'Fresh pasta with tomatoes, herbs, and olive oil',
            'ingredients': ['pasta', 'tomato', 'onion', 'garlic', 'olive oil', 'herbs'],
            'instructions': [
                'Cook pasta according to package directions',
                'Sauté diced onions and garlic in olive oil',
                'Add chopped tomatoes and simmer for 10 minutes',
                'Toss with cooked pasta and fresh herbs',
                'Serve immediately'
            ],
            'carbonImpact': 'low',
            'prepTime': 25,
            'servings': 4,
            'imageUrl': '/api/placeholder/400/300'
        },
        {
            'id': '2',
            'title': 'Garden Fresh Salad',
            'description': 'Mixed greens with seasonal vegetables',
            'ingredients': ['lettuce', 'tomato', 'carrot', 'onion', 'olive oil', 'vinegar'],
            'instructions': [
                'Wash and chop all vegetables',
                'Combine in a large bowl',
                'Whisk together olive oil and vinegar',
                'Drizzle dressing over salad',
                'Toss gently and serve'
            ],
            'carbonImpact': 'low',
            'prepTime': 15,
            'servings': 2,
            'imageUrl': '/api/placeholder/400/300'
        },
        {
            'id': '3',
            'title': 'Stir-Fry Vegetables',
            'description': 'Quick and healthy vegetable stir-fry',
            'ingredients': ['broccoli', 'carrot', 'onion', 'garlic', 'soy sauce', 'oil'],
            'instructions': [
                'Cut vegetables into bite-sized pieces',
                'Heat oil in a large pan or wok',
                'Add garlic and onions, stir for 1 minute',
                'Add remaining vegetables and stir-fry for 5-7 minutes',
                'Add soy sauce and serve over rice'
            ],
            'carbonImpact': 'low',
            'prepTime': 20,
            'servings': 3,
            'imageUrl': '/api/placeholder/400/300'
        },
        {
            'id': '4',
            'title': 'Fruit Smoothie Bowl',
            'description': 'Nutritious smoothie bowl with fresh fruits',
            'ingredients': ['banana', 'apple', 'milk', 'yogurt', 'honey'],
            'instructions': [
                'Blend banana, apple, and milk until smooth',
                'Pour into a bowl',
                'Top with yogurt and drizzle with honey',
                'Add fresh fruit slices as garnish',
                'Serve immediately'
            ],
            'carbonImpact': 'low',
            'prepTime': 10,
            'servings': 2,
            'imageUrl': '/api/placeholder/400/300'
        },
        {
            'id': '5',
            'title': 'Vegetable Soup',
            'description': 'Hearty vegetable soup perfect for any season',
            'ingredients': ['tomato', 'carrot', 'onion', 'garlic', 'broccoli', 'vegetable broth'],
            'instructions': [
                'Sauté onions and garlic until fragrant',
                'Add chopped vegetables and cook for 5 minutes',
                'Add vegetable broth and bring to a boil',
                'Simmer for 20-25 minutes until vegetables are tender',
                'Season with salt and pepper to taste'
            ],
            'carbonImpact': 'low',
            'prepTime': 35,
            'servings': 4,
            'imageUrl': '/api/placeholder/400/300'
        }
    ]
    
    # Filter recipes based on available ingredients
    available_ingredients = [item['name'].lower() for item in inventory]
    suitable_recipes = []
    
    for recipe in recipe_database:
        recipe_ingredients = [ingredient.lower() for ingredient in recipe['ingredients']]
        # Check if at least 60% of recipe ingredients are available
        available_count = sum(1 for ingredient in recipe_ingredients if any(avail in ingredient or ingredient in avail for avail in available_ingredients))
        if available_count >= len(recipe_ingredients) * 0.6:
            # Adjust servings based on people count
            adjusted_recipe = recipe.copy()
            adjusted_recipe['servings'] = people_count
            suitable_recipes.append(adjusted_recipe)
    
    # If no suitable recipes found, return some general recommendations
    if not suitable_recipes:
        suitable_recipes = random.sample(recipe_database, min(3, len(recipe_database)))
        for recipe in suitable_recipes:
            recipe['servings'] = people_count
    
    # Return top 3 recipes
    return suitable_recipes[:3]
