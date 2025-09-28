#!/usr/bin/env python3
"""
Smart Fridge Backend Server
Person B - Vision Ingestion Service

This script starts the FastAPI server for the Smart Fridge application.
The Vision Ingestion Service handles food detection from images using AWS Rekognition.
"""

import uvicorn
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir.parent))

def main():
    """Start the FastAPI server"""
    print("🍃 Starting Smart Fridge Backend Server...")
    print("👁️  Vision Ingestion Service (Person B)")
    print("=" * 50)
    
    # Environment variables for configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    print(f"🌐 Server will run on http://{host}:{port}")
    print(f"🔄 Auto-reload: {'enabled' if reload else 'disabled'}")
    print(f"📝 API docs available at http://{host}:{port}/docs")
    print("=" * 50)
    
    # Start the server
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    main()
