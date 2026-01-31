import logging
from fastapi import APIRouter, HTTPException, status, Request
from app import schemas
from app.services.story_generator import llm_generate_story, StoryGeneratorException
from app.core.rate_limiter import limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/story", tags=["Story endpoints"])


# we have one endpoint for both starting a new story and continuing an existing one:
@router.post("/generate")
@limiter.limit("10/minute")  # Limit to 10 requests per minute per IP
async def generate_story(request: Request, story_request: schemas.StoryRequest):
    """ 
    This endpoint is used to start a new story or continue an existing one:
    - if StoryRequest only contains a seed prompt, it starts a new story
    - if it contains a history of paragraphs and a choice,
      it'll continue the existing story based on the selected choice
    
    In both cases, it returns the next paragraph of the story and a list of
    choices for the next step.
    """
    
    if story_request.history and not story_request.choice:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Story choice missing."
        )    
    if story_request.choice and not story_request.history:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Story history missing."
        )

    try:
        paragraph, choices, stage_plan = await llm_generate_story(story_request)
    except StoryGeneratorException as exc:
        logger.error(f"Story generation failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )

    history = story_request.history
    history.append(paragraph)
    
    return schemas.StoryResponse(history=history, choices=choices, stage_plan=stage_plan)
