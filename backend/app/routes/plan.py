from fastapi import APIRouter, Query
from ..models.plan import PlanResponse, InventoryItem, SwapSuggestion, LLMContext
from ..utils.llm_swaps import suggest_swap
from sentence_transformers import SentenceTransformer, util
import json, os


router = APIRouter()


# Load your carbon dataset
CARBON_LIST = json.load(open(os.path.join("data","carbon_impact.json")))
CARBON = {entry["name"].lower(): {
            "tag": entry["tag"],
            "co2e_100g": entry["co2e_kg_per_kg"]/10,  # kg -> 100gs
            "category": entry["category"]
          } for entry in CARBON_LIST}


model = SentenceTransformer("all-MiniLM-L6-v2")


KEYS = list(CARBON.keys())
EMBEDDINGS = model.encode(KEYS, convert_to_tensor=True)

def compute_score(inventory):
    base = 100
    for item in inventory:
        if item.impact == "high":
            base -= 10
        elif item.impact == "medium":
            base -= 5
    return max(base, 0)

def normalize_name(name: str):
    return name.lower().replace("origin unknown", "").strip()

def semantic_lookup(query: str):
    query_emb = model.encode(query.lower(), convert_to_tensor=True)
    scores = util.cos_sim(query_emb, EMBEDDINGS)[0]
    best_idx = scores.argmax().item()
    best_score = scores[best_idx].item()

    # Add threshold (e.g., 0.6 = 60% similarity)
    if best_score < 0.6:
        return {"tag": "unknown", "co2e_100g": None, "category": "other"}

    best_key = KEYS[best_idx]
    return CARBON[best_key]


@router.post("/plan", response_model=PlanResponse)
def plan(
    items: list[str],
    people: int = 2,
    flags: list[str] = [],
    demo: bool = Query(False)
):
   

    inventory = []
    swaps = []

    for item in items:
        entry = semantic_lookup(item)
        impact = entry["tag"]
        category = entry.get("category", "other")
        co2e_100g = entry["co2e_100g"]

        inventory.append(InventoryItem(
            name=item, count=1, impact=impact, category=category, co2e_100g=co2e_100g
        ))

        # Generate intelligent swaps for medium/high impact items
        if impact in ["medium", "high"]:
            to_item, why = suggest_swap(item, category, co2e_100g)
            if to_item:
                t_data = semantic_lookup(normalize_name(to_item))
                reduction = None
                if t_data is not None and t_data.get("co2e_100g") is not None and co2e_100g is not None and co2e_100g != 0:
                    reduction = 100 * (1 - (t_data["co2e_100g"] / co2e_100g))
                swaps.append(SwapSuggestion(
                    from_item=item, to=to_item, why=why, reduction=reduction
                ))

    llm_context = LLMContext(pantry=items, people=people, flags=flags)
    score = compute_score(inventory)
    return PlanResponse(inventory=inventory, swaps=swaps, llm_context=llm_context, score = score)