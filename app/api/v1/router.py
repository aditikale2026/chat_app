# app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.endpoints.auth           import router as auth_router
from app.api.v1.endpoints.query          import router as query_router
from app.api.v1.endpoints.upload         import router as upload_router
from app.api.v1.endpoints.health         import router as health_router

router = APIRouter(prefix="/api/v1")

router.include_router(health_router)   # GET  /api/v1/health
router.include_router(auth_router)     # POST /api/v1/auth/...
router.include_router(query_router)    # POST /api/v1/rag/query
router.include_router(upload_router)   # POST /api/v1/rag/upload_document