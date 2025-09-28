from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
<<<<<<< HEAD
from app.routes import health, presign, analyze

app = FastAPI(
    title="Smart Fridge API",
    description="AI-powered food analysis and recipe recommendations",
    version="1.0.0"
)
=======
from app.routes import analyze, health, presign

app = FastAPI(title="Smart Fridge API", version="1.0.0")
>>>>>>> 85cfca634be5e8ef45cb4dc555da76c75924dfa3

# Configure CORS
app.add_middleware(
    CORSMiddleware,
<<<<<<< HEAD
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
=======
    allow_origins=["*"],  # Configure this properly for production
>>>>>>> 85cfca634be5e8ef45cb4dc555da76c75924dfa3
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
<<<<<<< HEAD
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(presign.router, prefix="/api", tags=["upload"])
app.include_router(analyze.router, prefix="/api", tags=["analysis"])

@app.get("/")
async def root():
    return {"message": "Smart Fridge API is running!"}
=======
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(presign.router, prefix="/presign", tags=["presign"])
app.include_router(analyze.router, prefix="/analyze", tags=["analyze"])
>>>>>>> 85cfca634be5e8ef45cb4dc555da76c75924dfa3

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
