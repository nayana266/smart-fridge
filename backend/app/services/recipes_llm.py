import hashlib, json, os, time
from typing import List
from app.shared.models.recipe import Recipe
from app.shared.models.recipe import Ingredient, Step
from app.shared.models.recipe import SustainabilityNotes
from app.shared.models.recipe import Swap
from app.shared.models.recipe import LLMContext
from openai import OpenAI  # pip install openai

_CACHE = {}  # key -> (ts, [Recipe])

def _cache_get(k: str):
    ts_rec = _CACHE.get(k)
    if not ts_rec: return None
    ts, recipes = ts_rec
    if time.time() - ts > TTL_SECONDS:
        _CACHE.pop(k, None)
        return None
    return recipes

def _cache_set(k: str, recipes: List[Recipe]):
    _CACHE[k] = (time.time(), recipes)


def _cache_clear() -> None:
    """Clear the in-memory recipe cache."""
    _CACHE.clear()

TTL_SECONDS = 1800  # 30 min

def _build_prompt(ctx: LLMContext) -> str:
    return f"""
You are a sustainability-aware chef.
Use ONLY these pantry items (plus water/salt/pepper/oil): {ctx.pantry}
People to serve: {ctx.people}
Dietary flags: {ctx.flags or []}
Return STRICT JSON ONLY:
{{
 "recipes":[
   {{
     "id":"string",
     "title":"string",
     "servings": {ctx.people},
     "ingredients":[{{"name":"string from pantry"}}],
     "steps":[{{"number":1,"text":"..."}},{{"number":2,"text":"..."}}],
     "sustainability_notes":{{"carbon_score_0_100":null,"summary":null,"swaps":[]}},
     "source":"llm"
   }}
 ]
}}
No extra text. No markdown. Max 3 recipes. Steps <= 8.
""".strip()

def _call_llm_strict_json(ctx):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = _build_prompt(ctx)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a sustainability-minded chef that always replies with strict JSON recipes."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        response_format={"type": "json_object"},
    )
    return resp.choices[0].message.content

def _key(ctx: LLMContext) -> str:
    norm = {
        "pantry": sorted([x.lower() for x in ctx.pantry]),
        "people": ctx.people,
        "flags": sorted([x.lower() for x in (ctx.flags or [])]),
    }
    return hashlib.sha256(json.dumps(norm, separators=(",",":")).encode()).hexdigest()

def _fallback(ctx: LLMContext) -> List[Recipe]:
    # Simple template recipes that only use pantry items; always valid.
    base = Recipe(
        id=f"fallback-{_key(ctx)[:8]}-1",
        title="Pantry Bowl",
        servings=ctx.people,
        ingredients=[Ingredient(name=i) for i in ctx.pantry[:6]],
        steps=[Step(number=1, text="Prep ingredients."),
               Step(number=2, text="Cook and assemble.")],
        sustainability_notes=SustainabilityNotes(summary="Uses what you have; plant-lean if available."),
        source="fallback",
    )
    return [base, base.model_copy(update={"id": base.id.replace("-1","-2"), "title":"Quick Skillet"}),
            base.model_copy(update={"id": base.id.replace("-1","-3"), "title":"Hearty Stir-fry"})]

def generate(ctx: LLMContext, demo: bool = False) -> List[Recipe]:
    k = _key(ctx)
    hit = _cache_get(k)
    if hit is not None:
        return hit

    if demo:
        from pathlib import Path
        APP_DIR = Path(__file__).resolve().parents[1]  # backend/app
        data = json.loads((APP_DIR / "dev" / "fixtures" / "recipe_demo.json").read_text())
        out = [Recipe(**data)]
        _cache_set(k, out)
        return out

    try:
        if not os.getenv("OPENAI_API_KEY"):
            print("recipes_llm: no OPENAI_API_KEY, using fallback")
            raise RuntimeError("no OPENAI_API_KEY")

        raw = _call_llm_strict_json(ctx)
        obj = json.loads(raw)
        out = [Recipe(**r) for r in obj["recipes"]]
        _cache_set(k, out)
        print("recipes_llm: used LLM path")
        return out
    except Exception as e:
        print("recipes_llm: falling back due to:", repr(e))
        out = _fallback(ctx)
        _cache_set(k, out)
        return out


