# backend/app/utils/demo.py
from pathlib import Path
import json

def read_fixture(rel_path: str):
    p = Path(__file__).parents[1] / rel_path
    return json.loads(p.read_text())

def demo_inventory():
    # what /vision/detect would roughly return after normalization
    return {
        "items": [
            {"name": "egg", "count": 4, "confidence": 0.98},
            {"name": "spinach", "count": 1, "confidence": 0.94},
            {"name": "tortilla", "count": 2, "confidence": 0.92}
        ]
    }

def demo_plan(inventory):
    # what /plan might return: score + swaps (keep it simple)
    # You can later call services.scoring and services.carbon
    return {
        "score": 72,  # pretend overall sustainability/health score
        "swaps": [
            {"from_item": "egg", "to_item": "tofu", "rationale": "Lower footprint"}
        ]
    }
