import logging
import json
from openai import AsyncOpenAI, OpenAIError
from app.schemas import StoryRequest, StoryPrompt
from app.core.config import settings
from typing import List, Optional

logger = logging.getLogger(__name__)

class StoryGeneratorException(Exception):
    pass



def build_story_prompt(prompt: StoryPrompt, history: List[str], choice: Optional[str]) -> str:
    instructions = []
    # Base instruction
    instructions.append(
        f"Write a fun, engaging Choose-your-own-adventure style story for a {prompt.age}-year-old child in {prompt.language}."
    )

    # Optional parameters
    if prompt.characters:
        char_desc = ", ".join(f"{c.name} who is a {c.type}" for c in prompt.characters)
        instructions.append(f"The story includes the following characters: {char_desc}.")

    if prompt.environment:
        instructions.append(f"The story takes place in the following environment: {prompt.environment}")

    if prompt.theme:
        instructions.append(f"The theme of the story is: {prompt.theme}.")

    if prompt.prompt:
        instructions.append(f"The story should also follow this prompt: {prompt.prompt}")

    instructions.append("")  # Spacer

    if history and choice:
        instructions.append("Here is the story so far:")
        for i, para in enumerate(history, 1):
            instructions.append(f"Part {i}: {para}")
        instructions.append("")  # Spacer

        instructions.append((
            f"The child chose the following option for the next part of the story: '{choice}'."
            "Continue the story based on that choice."
        ))

    # Instruction to generate next part
    instructions.append("Now write the next paragraph of the story, only write one paragraph at a time.")
    instructions.append("Then offer 2 or 3 engaging choices for what could happen next.")
    instructions.append("Choices should be short descriptions and make sense with story.")

    instructions.append((
        "Format the response as a JSON object with a 'paragraph' field containing the generated story paragraph"
        "and a 'choices' field containing the list of choices for the next step."
        "Only return the JSON object, do not include any additional text or formatting."
        "Example: {\"paragraph\": \"next paragraph\"', \"choices\": [\"Choice 1\", \"Choice 2\", \"Choice 3\"]}"
    ))

    return "\n".join(instructions)


async def llm_generate_story(request: StoryRequest) -> dict:
    """ Call an LLM to generate a Choose-your-own-adventure style story. """
    
    client = AsyncOpenAI(base_url=settings.LLM_API_URL, api_key=settings.LLM_API_KEY)
    
    logger.info(f"Generating story based on story request: {request}")
    
    prompt = build_story_prompt(request.prompt, request.history, request.choice)
    
    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a children's storyteller."},
                {"role": "user", "content": prompt}
            ]
        )
    except OpenAIError as exc:
        raise StoryGeneratorException(f"Error calling LLM API: {str(exc)}")
    
    try:
        content = response.choices[0].message.content
        print(f"LLM response: {content}")
        # strip whitespace, backticks and quotes:
        content = content.strip().strip("`'\"")
        story = json.loads(content)
    except (KeyError, IndexError, AttributeError, json.decoder.JSONDecodeError) as exc:
        raise StoryGeneratorException(f"Invalid LLM response: {str(exc)}")
    
    return story["paragraph"], story["choices"]