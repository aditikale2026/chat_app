from fastapi import APIRouter
from fastapi.responses import FileResponse
from pathlib import Path

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parents[3]


@router.get("/", response_class=FileResponse)
async def index():
    """Serve React SPA for root route"""
    spa_path = BASE_DIR / "static" / "dist" / "index.html"
    return FileResponse(spa_path)


@router.get("/{path_name:path}", response_class=FileResponse)
async def catch_all(path_name: str):
    """Catch all routes and serve React SPA
    React Router handles routing on the client side"""
    spa_path = BASE_DIR / "static" / "dist" / "index.html"
    
    # If file exists in static/dist (CSS, JS), serve it
    file_path = BASE_DIR / "static" / "dist" / path_name
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    
    # Otherwise, serve the React SPA entry point
    return FileResponse(spa_path)