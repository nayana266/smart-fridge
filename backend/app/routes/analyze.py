# backend/app/routes/analyze.py
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional, List, Any
import json
from pathlib import Path

from backend.app.shared.models.recipe import Recipe, LLMContext
from backend.app.services import recipes_llm
from backend.app.utils.demo import demo_inventory, demo_plan

router = APIRouter()

class AnalyzeRequest(BaseModel):
    # Extend later (e.g., user prefs, budget, dietary flags)
    budget: Optional[float] = None
    people: Optional[int] = None
    flags: Optional[List[str]] = None  # e.g. ["vegetarian", "no_pork"]

class AnalyzeResponse(BaseModel):
    inventory: Any
    score: float
    swaps: List[dict]
    recipes: List[Recipe]

@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(payload: AnalyzeRequest, demo: bool = Query(False)):
    """
    Orchestrator:
    - demo=true: uses stubbed outputs for /vision and /plan and appends the demo recipe
    - demo=false: (for now) placeholder inventory/plan, then calls the recipes service
    """
    # 1) Inventory detection/normalization
    if demo:
        inventory = demo_inventory()
        plan = demo_plan(inventory)
        # Demo recipe fixture
        fixture_path = Path(__file__).resolve().parents[1] / "dev" / "fixtures" / "recipe_demo.json"  # parents[1] = backend/app
        demo_recipe = Recipe(**json.loads(fixture_path.read_text()))
        recipes = [demo_recipe]
    else:
        # TODO: replace these placeholders once /vision/detect and /plan are live
        inventory = {"items": []}          # e.g., [{"name":"tofu","count":1,"confidence":0.91}, ...]
        plan = {"score": 0, "swaps": []}   # e.g., {"score": 86, "swaps": [{"from":"beef","to":"tofu","why":"..."}]}

        # 3) Recipes via LLM (or fallback/cached) using the shared LLMContext
        ctx = LLMContext(
                pantry=[it["name"] for it in inventory.get("items", [])],
                people=payload.people or 2,
                flags=payload.flags or []
        )
        recipes = recipes_llm.generate(ctx, demo=False)

    return AnalyzeResponse(
        inventory=inventory,
        score=plan["score"],
        swaps=plan["swaps"],
        recipes=recipes
    )
