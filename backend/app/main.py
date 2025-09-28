from fastapi import FastAPI
from .routes import recipes, analyze, health, presign  # keep others you already had

app = FastAPI()
app.include_router(recipes.router)
app.include_router(analyze.router)
app.include_router(health.router)
app.include_router(presign.router)