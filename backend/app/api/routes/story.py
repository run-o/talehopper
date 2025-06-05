import logging
from fastapi import APIRouter, HTTPException, status
from app import schemas
from app.services.story_generator import llm_generate_story, StoryGeneratorException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/story", tags=["Story endpoints"])

# we have one endpoint for both starting a new story and continuing an existing one:
@router.post("/generate")
async def generate_story(request: schemas.StoryRequest):
    """ 
    This endpoint is used to start a new story or continue an existing one:
    - if StoryRequest only contains a seed prompt, it starts a new story
    - if it contains a history of paragraphs and a choice,
      it'll continue the existing story based on the selected choice
    
    In both cases, it returns the next paragraph of the story and a list of
    choices for the next step.
    """
    
    if request.history and not request.choice:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Story choice missing."
        )    
    if request.choice and not request.history:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Story history missing."
        )

    try:
        paragraph, choices = await llm_generate_story(request)
    except StoryGeneratorException as exc:
        logger.error(f"Story generation failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )

    history = request.history
    history.append(paragraph)
    
    return schemas.StoryResponse(history=history, choices=choices)    
        
    
    