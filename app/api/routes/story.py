import logging
from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException, status
from app import schemas
from app.services.story_generator import llm_generate_story

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/story", tags=["Story endpoints"])

# we have one endpoint for both starting a new story and continuing an existing one:
@router.post("/generate")
async def generate_story(request: schemas.StoryRequest):
    """ 
    This endpoint is used to start a new story or continue an existing one:
    - if StoryRequest only contains a seed prompt, it starts a new story
    - if it contains a history of paragraphs and a choice,
      it'll continue the existing story
    
    In both cases, it returns the next paragraph of the story and a list of
    choices for the next step.
    """
    prompt = request.prompt
    history = request.history
    choice = request.choice
    
    # TODO: raise an error if:
    # - if request.prompt is None
    # - if request.choice is None and request.history is not empty
    # - if request.choice is not None and request.history is empty

    paragraph, choices = await llm_generate_story(request)
    
    history.append(paragraph)
    return schemas.StoryResponse(history=history, choices=choices)    
        
    
    