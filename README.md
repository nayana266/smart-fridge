# Smart Fridge

Lightweight demo app for experimenting with AI-assisted meal planning and fridge inventory tooling.

## Backend Shared Recipe Schema

- Canonical Pydantic models live in `backend/app/shared/models/recipe.py`; all backend services should import from here to stay aligned.
- The JSON fixture at `backend/app/dev/fixtures/recipe_demo.json` mirrors the model and is used by the `/recipes` demo endpoint and unit tests.

### Recipe Schema (contract)

```json
{
  "id": "string",
  "title": "string",
  "servings": 1,
  "ingredients": [{ "name": "string", "quantity": 0, "unit": "g|tsp|..." }],
  "steps": [{ "number": 1, "text": "string", "duration_minutes": 0 }],
  "sustainability_notes": {
    "carbon_score_0_100": 0,
    "summary": "string",
    "swaps": [{ "from_item": "string", "to_item": "string" }]
  },
  "source": "demo|llm|curated|url"
}
```

### Regenerating the JSON schema

Run the schema exporter and capture the output (create the `backend/app/dev/schemas` folder if it is missing):

```
python -m backend.app.shared.models > backend/app/dev/schemas/recipe.schema.json
```

### Validation

- FastAPI routes can use `Recipe` as a response model to guarantee contract parity.
- The unit test `backend/app/tests/test_recipe_model.py` ensures the demo fixture stays valid.

