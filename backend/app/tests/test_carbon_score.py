from fastapi.testclient import TestClient
from fastapi import FastAPI
import backend.app.routes.plan as plan_mod
from backend.app.routes.plan import router


def fake_semantic_lookup(query: str):
    q = query.lower()
    if "beef" in q:
        return {"tag": "high", "co2e_100g": 80.0, "category": "meat"}
    if "dragonfruit" in q:
        return {"tag": "low", "co2e_100g": 3.0, "category": "fruit"}
    if "eggs" in q:
        return {"tag": "medium", "co2e_100g": 20.0, "category": "dairy"}
    return {"tag": "unknown", "co2e_100g": None, "category": "other"}


def fake_suggest_swap(item_name: str, category: str, co2e_100g: float):
    if "beef" in item_name.lower() or (co2e_100g and co2e_100g > 30):
        return ("tofu", "plant-based alternative with lower emissions")
    if "eggs" in item_name.lower() or (co2e_100g and co2e_100g > 10):
        return ("chickpeas", "plant-based protein with lower emissions")
    return (None, None)


# Apply the mocks directly to the module so the router uses them
plan_mod.semantic_lookup = fake_semantic_lookup
plan_mod.suggest_swap = fake_suggest_swap


def test_plan_with_fake_vision():
    test_app = FastAPI()
    test_app.include_router(router)
    client = TestClient(test_app)

    fake_vision_items = [
        {"name": "Beef, rump, raw", "count": 1, "confidence": 0.91},
        {"name": "Dragonfruit, raw", "count": 1, "confidence": 0.88},
        {"name": "Eggs, chicken, free-range", "count": 1, "confidence": 0.95}
    ]
    item_names = [item["name"] for item in fake_vision_items]

    resp = client.post("/plan", json={"items": item_names, "people": 2, "flags": []})
    assert resp.status_code == 200, resp.text
    data = resp.json()

    # Inventory length
    assert len(data["inventory"]) == 3

    # There should be swaps for high/medium items where we returned a swap
    high_medium_swaps = [s for s in data["swaps"] if s.get("to") is not None]
    assert len(high_medium_swaps) >= 1

    # Score key
    assert "score" in data and isinstance(data["score"], int)
