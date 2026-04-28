"""
frontend_router.py
Serves the compiled React SPA.

Register this AFTER the API router in main.py so API routes take priority:

    app.include_router(api_router)          # /api/v1/...
    app.include_router(frontend_router)     # catch-all — must be last
"""

from fastapi import APIRouter
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

router = APIRouter()
BASE_DIR  = Path(__file__).resolve().parents[3]
DIST_DIR  = BASE_DIR / "static" / "dist"


@router.get("/", response_class=FileResponse, include_in_schema=False)
async def index():
    return FileResponse(DIST_DIR / "index.html")


@router.get("/{path_name:path}", response_class=FileResponse, include_in_schema=False)
async def catch_all(path_name: str):
    file_path = DIST_DIR / path_name
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    # React Router handles unknown paths client-side
    return FileResponse(DIST_DIR / "index.html")