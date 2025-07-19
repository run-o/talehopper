import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.main import api_router
from app.services import story_generator
from app.core.config import settings
from app.core.rate_limiter import limiter, rate_limit_handler


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthCheckLogFilter(logging.Filter):
    """ Custom log filter to exclude health check logs """
    def filter(self, record: logging.LogRecord) -> bool:
        return "/health" not in record.getMessage()

# Filter out /health check logs from the access log:
logging.getLogger("uvicorn.access").addFilter(HealthCheckLogFilter())


@asynccontextmanager
async def lifespan(app: FastAPI):
    """ The lifespan startup context manager allows us to define code that
        should be executed before the application starts up and when the app
        is shutting down (potential cleanup steps).
    """
    story_generator.initialize()
    yield
    # do cleanup here if necessary


app = FastAPI(lifespan=lifespan)

# Set up a rate limiter:
app.state.limiter = limiter
app.add_exception_handler(429, rate_limit_handler)


# Enable CORS
cors_origins = settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get('/')
async def root():
    return {"message": "Welcome to Tale Hopper!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
