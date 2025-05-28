from typing import List, Optional, Literal
from pydantic import BaseModel, Field

# TODO: replace some of the Literal types with enums for better validation and readability

class Character(BaseModel):
    name: str
    type: str = Field(..., description="Type of character: 'boy', 'girl', 'animal' etc")


class StoryPrompt(BaseModel):
    age: int = Field(..., ge=1, le=12, description="Child's age in years (1-12)")
    language: Literal["english", "french"] = Field(..., description="Language")
    length: int = Field(..., ge=3, le=60, description="Approximate story length in steps or minutes")
    
    prompt: Optional[str] = Field(None, description="Optional custom prompt to guide the story")
    characters: Optional[List[Character]] = Field(None, description="Optional list of characters")
    environment: Optional[str] = Field(None, description="Optional environment setting, e.g., 'forest'")
    theme: Optional[str] = Field(None, description="Optional story theme, e.g., 'fairies'")
    
    tone: Optional[Literal["friendly", "silly", "adventurous", "mysterious", "wholesome"]] = None
    conflict_type: Optional[Literal["quest", "problem", "villain", "lost item"]] = None
    ending_style: Optional[Literal["happy", "twist", "moral", "open"]] = None
    

class StoryRequest(BaseModel):
    prompt: StoryPrompt
    history: List[str] = Field(default_factory=list, description="All previously generated story paragraphs")
    choice: Optional[str] = Field(None, description="The reader's selected choice, if continuing")

    
class StoryResponse(BaseModel):
    #story_id: str = Field(..., description="Unique identifier for this story session")
    choices: List[str] = Field(..., description="List of options for the next step of the story")
    history: List[str] = Field(..., description="Ordered list of all story steps up to this point")