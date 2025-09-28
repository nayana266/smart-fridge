from typing import List, Dict, Any

def calculate_carbon_impact(inventory: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate carbon impact for inventory items"""
    
    total_carbon = 0
    high_impact_items = []
    medium_impact_items = []
    low_impact_items = []
    
    for item in inventory:
        carbon_value = item.get('carbonValue', 1.0)
        total_carbon += carbon_value
        
        if item.get('carbonImpact') == 'high':
            high_impact_items.append(item)
        elif item.get('carbonImpact') == 'medium':
            medium_impact_items.append(item)
        else:
            low_impact_items.append(item)
    
    return {
        'totalCarbon': round(total_carbon, 2),
        'highImpactItems': high_impact_items,
        'mediumImpactItems': medium_impact_items,
        'lowImpactItems': low_impact_items,
        'impactBreakdown': {
            'high': len(high_impact_items),
            'medium': len(medium_impact_items),
            'low': len(low_impact_items)
        }
    }

def get_carbon_tips(inventory: List[Dict[str, Any]]) -> List[str]:
    """Generate carbon reduction tips based on inventory"""
    tips = []
    
    high_carbon_items = [item for item in inventory if item.get('carbonImpact') == 'high']
    
    if high_carbon_items:
        tips.append("Consider reducing high-carbon items like meat and dairy")
        tips.append("Try plant-based alternatives for protein sources")
    
    if any('beef' in item['name'].lower() for item in inventory):
        tips.append("Beef has the highest carbon footprint - consider chicken or plant proteins")
    
    if any('dairy' in item['name'].lower() for item in inventory):
        tips.append("Try plant-based milk alternatives to reduce carbon impact")
    
    if len(inventory) > 10:
        tips.append("You have many items - plan meals to reduce food waste")
    
    return tips[:3]  # Return top 3 tips
