from fastapi import APIRouter
from llm_service.app.routes.generate import router as generate_router

router = APIRouter()

router.include_router(generate_router)