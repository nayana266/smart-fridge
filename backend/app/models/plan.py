from pydantic import BaseModel
from typing import List


class InventoryItem(BaseModel):
    name: str
    count: int
    impact: str              
    category: str            
    co2e_100g: float | None  


class SwapSuggestion(BaseModel):
    from_item: str
    to: str
    why: str
    reduction: float | None  


class LLMContext(BaseModel):
    pantry: List[str]
    people: int
    flags: List[str]


class PlanResponse(BaseModel):
    inventory: List[InventoryItem]
    swaps: List[SwapSuggestion]
    llm_context: LLMContext
    score: int