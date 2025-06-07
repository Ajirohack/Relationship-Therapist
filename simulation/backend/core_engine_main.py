from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
import json

# Change from relative to absolute import
from core_engine_router import router as core_engine_router

# Create FastAPI app
app = FastAPI(
    title="Core Engine API",
    description="API for the Core Engine relationship stage orchestration system",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(core_engine_router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Core Engine API",
        "docs": "/docs",
        "version": "0.1.0"
    }

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "healthy"}

# Config endpoint
@app.get("/config")
async def get_config():
    config_path = Path(__file__).resolve().parent.parent / "config" / "core_engine_config.json"
    
    if not config_path.exists():
        # Create default config if it doesn't exist
        default_config = {
            "app_name": "Core Engine",
            "version": "0.1.0",
            "stages": ["APP", "FPP", "RPP"],
            "default_stage": "APP",
            "scoring": {
                "trust_threshold": 60,
                "openness_threshold": 40,
                "window_size": 10
            },
            "ui": {
                "show_stage": True,
                "show_scores": True,
                "show_recommendations": True
            }
        }
        
        # Ensure config directory exists
        config_path.parent.mkdir(exist_ok=True, parents=True)
        
        # Write default config
        with open(config_path, "w") as f:
            json.dump(default_config, f, indent=2)
            
        return default_config
    
    # Load existing config
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"error": "Invalid config file"}

# Run the app if executed directly
def start():
    """
    Start the FastAPI application using uvicorn
    """
    uvicorn.run(
        "core_engine_main:app",  # Use the local module name instead of the full path
        host="0.0.0.0",
        port=8001,  # Changed port from 8000 to 8001
        reload=True
    )

if __name__ == "__main__":
    start()