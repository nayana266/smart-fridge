# backend/app/shared/models/recipe.py
from __future__ import annotations
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

Unit = Literal[
    "g","kg","ml","l","tsp","tbsp","cup","oz","lb","piece","slice","clove","leaf","pinch"
]

class Ingredient(BaseModel):
    name: str = Field(..., description="Canonical ingredient name (lowercase, singular)")
    quantity: Optional[float] = Field(None, ge=0)
    unit: Optional[Unit] = None
    # Optional links to canonicals from vision/ocr stages
    canonical_id: Optional[str] = Field(
        None, description="Internal canonical ingredient id (if mapped)"
    )
    notes: Optional[str] = None

class Step(BaseModel):
    number: int = Field(..., ge=1)
    text: str = Field(..., description="Instruction for this step")
    # Optional timing metadata for UX (progress bars, prep timers)
    duration_minutes: Optional[int] = Field(None, ge=0)

class Swap(BaseModel):
    from_item: str
    to_item: str
    rationale: Optional[str] = None
    est_carbon_delta_gCO2e: Optional[float] = None

class SustainabilityNotes(BaseModel):
    carbon_score_0_100: Optional[float] = Field(
        None, ge=0, le=100, description="Higher means greener (normalized)"
    )
    summary: Optional[str] = None
    swaps: Optional[List[Swap]] = None

class Recipe(BaseModel):
    id: str = Field(..., description="Stable id for caching & dedupe")
    title: str
    servings: int = Field(..., ge=1)
    ingredients: List[Ingredient]
    steps: List[Step]
    sustainability_notes: Optional[SustainabilityNotes] = None
    source: Optional[str] = Field(
        None, description="generator/source (demo, LLM, curated, url, etc.)"
    )
