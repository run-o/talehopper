import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api.main import api_router


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """ The lifespan startup context manager allows us to define code that
        should be executed before the application starts up and when the app
        is shutting down (potential cleanup steps).
    """
    yield
    # do cleanup here if necessary

app = FastAPI(lifespan=lifespan)

app.include_router(api_router)

@app.get('/')
async def root():
    return {"message": "Welcome to Tale Hopper!"}