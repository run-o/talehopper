from fastapi import APIRouter

from app.api.routes import story, feedback


api_router = APIRouter()
api_router.include_router(story.router)
api_router.include_router(feedback.router)
