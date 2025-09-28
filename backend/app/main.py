from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import health, presign, analyze, recipes
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Smart Fridge API",
    description="AI-powered food analysis and recipe recommendations",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(presign.router, prefix="/api", tags=["upload"])
app.include_router(analyze.router, prefix="/api", tags=["analysis"])
app.include_router(recipes.router, prefix="/api", tags=["recipes"])

# Also include the same routers at root for compatibility with tests and some clients
# (this registers endpoints both at /api/... and at /...)
app.include_router(health.router, tags=["health"])
app.include_router(presign.router, tags=["upload"])
app.include_router(analyze.router, tags=["analysis"])
app.include_router(recipes.router, tags=["recipes"])

@app.get("/")
async def root():
    return {"message": "Smart Fridge API is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
