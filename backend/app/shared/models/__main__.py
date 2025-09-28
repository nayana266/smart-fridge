from .recipe import Recipe
import json
print(json.dumps(Recipe.model_json_schema(), indent=2))