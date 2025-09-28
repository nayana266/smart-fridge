def suggest_swap(item: str, category: str, co2e_100g: float | None) -> tuple[str | None, str]:
    """
    Suggest sustainable swaps for high-impact food items.
    Returns (suggested_item, reason) or (None, reason) if no good swap available.
    """
    
    # High-impact protein swaps
    if category == "protein" and co2e_100g and co2e_100g > 5.0:
        if "beef" in item.lower():
            return "lentils", "Lentils have ~95% lower carbon footprint than beef"
        elif "lamb" in item.lower():
            return "tofu", "Tofu has ~90% lower carbon footprint than lamb"
        elif "pork" in item.lower():
            return "chicken", "Chicken has ~60% lower carbon footprint than pork"
        elif "cheese" in item.lower():
            return "nuts", "Nuts have ~70% lower carbon footprint than cheese"
    
    # Dairy swaps
    elif category == "dairy" and co2e_100g and co2e_100g > 3.0:
        if "milk" in item.lower():
            return "oat milk", "Oat milk has ~60% lower carbon footprint than dairy milk"
        elif "butter" in item.lower():
            return "olive oil", "Olive oil has ~70% lower carbon footprint than butter"
        elif "yogurt" in item.lower():
            return "coconut yogurt", "Coconut yogurt has ~50% lower carbon footprint than dairy yogurt"
    
    # Processed food swaps
    elif "processed" in category.lower() or "packaged" in category.lower():
        if "chips" in item.lower() or "crackers" in item.lower():
            return "nuts", "Whole nuts have much lower processing footprint than packaged snacks"
        elif "soda" in item.lower() or "juice" in item.lower():
            return "water", "Water has virtually no carbon footprint compared to bottled drinks"
    
    # Generic suggestions for high-impact items
    elif co2e_100g and co2e_100g > 4.0:
        return "seasonal vegetables", f"Local seasonal vegetables typically have 80%+ lower carbon footprint than {item}"
    
    # No swap needed for low-impact items
    return None, f"{item} already has a relatively low carbon footprint"