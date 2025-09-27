# backend/api/recipes.py
from fastapi import APIRouter
from backend.app.shared.models.recipe import Recipe
import json
from pathlib import Path

router = APIRouter()

@router.get("/recipes", response_model=Recipe)
def get_recipe_demo():
    p = Path(__file__).parents[2] / "dev" / "fixtures" / "recipe_demo.json"
    return Recipe(**json.loads(p.read_text()))
