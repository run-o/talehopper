from typing import List, Optional, Literal
from pydantic import BaseModel, Field

# TODO: replace some of the Literal types with enums for better validation and readability

class Character(BaseModel):
    name: str
    type: str = Field(..., description="Type of character: child, animal, dragon etc")
    gender: Optional[str] = Field(None, description="Character's gender")
    personality: Optional[str] = Field(None, description="Character's personality")

class StoryPrompt(BaseModel):
    age: int = Field(..., ge=1, le=12, description="Child's age in years (1-12)")
    language: Literal["english", "french"] = Field(..., description="Language")
    length: int = Field(..., ge=3, le=60, description="Number of paragraphs in the story")
    
    prompt: Optional[str] = Field(None, description="Custom prompt to guide the story")
    characters: Optional[List[Character]] = Field(None, description="List of characters")
    environment: Optional[str] = Field(None, description="Environment setting: forest, space, ocean, etc")
    theme: Optional[str] = Field(None, description="Story theme: friendship, magic, adventure, etc")
    
    tone: Optional[str] = Field(None, description="Tone: friendly, silly, adventurous, mysterious, wholesome, etc")
    conflict_type: Optional[str] = Field(None, description="Conflict type: quest, problem, villain, lost item, etc")
    ending_style: Optional[str] = Field(None, description="Ending style: happy, twist, moral, open")
    

class StoryRequest(BaseModel):
    prompt: StoryPrompt
    history: List[str] = Field(default_factory=list, description="All previously generated story paragraphs")
    choice: Optional[str] = Field(None, description="Reader's choice for the next step in the story")

    
class StoryResponse(BaseModel):
    choices: List[str] = Field(..., description="List of options for the next step of the story")
    history: List[str] = Field(..., description="Ordered list of all story steps up to this point")