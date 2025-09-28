# backend/app/tests/test_recipes_post.py
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services import recipes_llm
import os
import json  # <-- needed

client = TestClient(app)

def test_post_recipes_demo_returns_list():
    payload = {"panry":["tofu","rice","spinach"], "people":2, "flags":["veg_ok"]}
    # ^ if you intentionally misspelled pantry above, fix to "pantry"
    payload = {"pantry":["tofu","rice","spinach"], "people":2, "flags":["veg_ok"]}
    r = client.post("/recipes?demo=true", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list) and len(data) >= 1
    assert {"id","title","servings","ingredients","steps"}.issubset(data[0].keys())

def test_generator_falls_back_without_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    ctx = recipes_llm.LLMContext(pantry=["eggs","pepper"], people=2, flags=[])
    out = recipes_llm.generate(ctx, demo=False)
    assert len(out) >= 1
    assert out[0].title in {"Pantry Bowl","Quick Skillet","Hearty Stir-fry"}

def test_generator_uses_cache(monkeypatch):
    # start with a clean cache to avoid interference
    recipes_llm._cache_clear()

    calls = {"n": 0}
    def fake_call(ctx: recipes_llm.LLMContext) -> str:
        calls["n"] += 1
        return json.dumps({
            "recipes": [{
                "id": "x",
                "title": "Cached",
                "servings": ctx.people,
                "ingredients": [
                    {"name": ctx.pantry[0], "quantity": None, "unit": None}
                ],
                "steps": [
                    {"number": 1, "text": "do", "duration_minutes": 0}
                ],
                "sustainability_notes": {
                    "carbon_score_0_100": None,
                    "summary": None,
                    "swaps": []
                },
                "source": "llm"
            }]
        })

    # Patch the internal LLM call so generate() uses our deterministic JSON
    monkeypatch.setattr(recipes_llm, "_call_llm_strict_json", fake_call)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")

    ctx = recipes_llm.LLMContext(pantry=["tofu","rice"], people=2, flags=[])
    out1 = recipes_llm.generate(ctx, demo=False)
    out2 = recipes_llm.generate(ctx, demo=False)

    assert out1[0].title == "Cached"
    assert out2[0].title == "Cached"
    assert calls["n"] == 1  # second call should hit the cache
