from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_analyze_demo_shape():
    resp = client.post("/analyze?demo=true", json={"people": 2, "budget": 10})
    assert resp.status_code == 200
    body = resp.json()
    assert "inventory" in body and "score" in body and "swaps" in body and "recipes" in body
    assert isinstance(body["recipes"], list) and len(body["recipes"]) >= 1
    r = body["recipes"][0]
    assert {"id","title","servings","ingredients","steps"}.issubset(r.keys())
