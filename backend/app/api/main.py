from fastapi import APIRouter

from app.api.routes import story


api_router = APIRouter()
api_router.include_router(story.router)
