# backend/api/recipes.py
from fastapi import APIRouter, Query
import json
from pathlib import Path
from typing import List
from backend.app.shared.models.recipe import Recipe, LLMContext
from backend.app.services.recipes_llm import generate

router = APIRouter()

APP_DIR = Path(__file__).resolve().parents[1]

@router.get("/recipes", response_model=Recipe)
def get_recipe_demo():
    p = APP_DIR / "dev" / "fixtures" / "recipe_demo.json"
    data = json.loads(p.read_text())
    return Recipe(**data)

@router.post("/recipes", response_model=List[Recipe])
def post_recipes(ctx: LLMContext, demo: bool = Query(False)):
    return generate(ctx, demo=demo)