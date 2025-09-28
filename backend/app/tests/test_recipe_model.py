import json
from pathlib import Path
from backend.app.shared.models.recipe import Recipe

def test_fixture_is_valid_recipe():
    p = Path(__file__).parents[1] / "dev" / "fixtures" / "recipe_demo.json"
    data = json.loads(p.read_text())
    r = Recipe(**data)
    assert r.title and r.servings >= 1
    assert len(r.ingredients) > 0
    assert all(s.number >= 1 and s.text for s in r.steps)