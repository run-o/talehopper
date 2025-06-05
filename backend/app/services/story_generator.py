import logging
import json
import requests
from openai import AsyncOpenAI, OpenAIError
from app.schemas import StoryRequest, StoryPrompt
from app.core.config import settings
from typing import List, Optional

logger = logging.getLogger(__name__)

class StoryGeneratorException(Exception):
    pass

LLM_SYSTEM_PROMPT = "You are a children's storyteller."

def build_story_prompt(prompt: StoryPrompt, history: List[str], choice: Optional[str]) -> str:
    instructions = []
    # Base instruction
    instructions.append(
        f"Write a fun, engaging Choose-your-own-adventure style story for a {prompt.age}-year-old child in {prompt.language}."
    )

    # Optional parameters
    if prompt.characters:
        char_desc = ", ".join(
            f"{c.name} who is a {c.type}"
            + (f" with a {c.gender} gender" if c.gender else "")
            + (f" and a {c.personality} personality" if c.personality else "")
            for c in prompt.characters
        )
        instructions.append(f"The story includes the following characters: {char_desc}.")

    if prompt.environment:
        instructions.append(f"The story takes place in the following environment: {prompt.environment}")

    if prompt.theme:
        instructions.append(f"The theme of the story is: {prompt.theme}.")

    if prompt.prompt:
        instructions.append(f"The story should also follow this prompt: '{prompt.prompt}'")
        
    if prompt.tone:
        instructions.append(f"The story should have a {prompt.tone} tone.")
        
    if prompt.ending_style:
        instructions.append(f"The story ending style should be: {prompt.ending_style} style.")
        
    if prompt.conflict_type:
        instructions.append(f"The story should include a conflict of type: {prompt.conflict_type}.")

    instructions.append("")

    if history and choice:
        instructions.append("Here is the story so far:")
        for i, para in enumerate(history, 1):
            instructions.append(f"Part {i}: {para}")
        instructions.append("")

        instructions.append((
            f"The child chose the following option for the next part of the story: '{choice}'."
            "Continue the story based on that choice."
        ))

    # Instruction to generate next part
    instructions.append("Now write the next paragraph of the story, only write one paragraph at a time.")
    if len(history) < prompt.length - 1:
        instructions.append("Then offer 2 or 3 engaging choices for what could happen next.")
        instructions.append("Choices should be short descriptions and make sense with the story.")
    
    if len(history) == prompt.length - 2:
        instructions.append("The story is getting close to the end, so make sure to start wrapping it up.")
    elif len(history) == prompt.length - 1:
        instructions.append("The story has reached the desired length, so end it with a satisfying conclusion.")
        instructions.append("Do not generate choices.")
        

    instructions.append((
        "Format the response as a JSON object with a 'paragraph' field containing the generated story paragraph "
        "and a 'choices' field containing the list of choices for the next step.\n"
        "Only return the JSON object, do not include any additional text or formatting.\n"
        "Example: {\"paragraph\": \"next paragraph\"', \"choices\": [\"Choice 1\", \"Choice 2\", \"Choice 3\"]}"
    ))
    
    return "\n".join(instructions)


async def llm_get_story_json_openAI(prompt) -> str:
    client = AsyncOpenAI(
        base_url=settings.LLM_OPENAI_API_URL,
        api_key=settings.LLM_OPENAI_API_KEY
    )
    try:
        response = await client.chat.completions.create(
            model=settings.LLM_OPENAI_MODEL,
            messages=[
                {"role": "system", "content": LLM_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
        )
    except OpenAIError as exc:
        raise StoryGeneratorException(f"Error calling LLM API: {str(exc)}")
    
    try:
        return response.choices[0].message.content
    except (KeyError, IndexError, AttributeError) as exc:
        raise StoryGeneratorException(f"Invalid LLM response: {str(exc)}")
    

async def llm_get_story_json_ollama(prompt) -> str:
    try:
        response = requests.post(
            settings.LLM_OLLAMA_API_URL,
            json={
                "model": settings.LLM_OLLAMA_MODEL,
                "system": LLM_SYSTEM_PROMPT,
                "prompt": prompt,
                "stream": False
            }
        )
        return response.json()["response"]
    except requests.RequestException as exc:
        raise StoryGeneratorException(f"Error calling ollama LLM: {str(exc)}")
    except (KeyError, IndexError, AttributeError) as exc:
        raise StoryGeneratorException(f"Invalid LLM response: {str(exc)}")  
    

async def llm_generate_story(request: StoryRequest):
    """ Call an LLM to generate a Choose-your-own-adventure style story. """
        
    logger.info(f"Generating story based on story request: {request}")
    
    prompt = build_story_prompt(request.prompt, request.history, request.choice)
    logger.info(f"Generated prompt for LLM: {prompt}")
    
    if settings.LLM_METHOD == "openai":
        json_content = await llm_get_story_json_openAI(prompt)
    elif settings.LLM_METHOD == "ollama":
        json_content = await llm_get_story_json_ollama(prompt)
    else:
        raise StoryGeneratorException(f"Unsupported LLM method: {settings.LLM_METHOD}") 
    
    try:
        # strip whitespace, backticks and quotes:
        json_content = json_content.strip().strip("`'\"")
        story = json.loads(json_content)
    except json.JSONDecodeError as exc:
        logger.error(f"LLM response content: {json_content}")
        raise StoryGeneratorException(f"Invalid JSON from LLM: {str(exc)}")
    
    return story["paragraph"], story["choices"]