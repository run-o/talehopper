import logging
import json
import httpx
import random
from enum import StrEnum
from fastapi.concurrency import run_in_threadpool
from openai import AsyncOpenAI, OpenAIError
from app.schemas import StoryRequest, StoryPrompt
from app.core.config import settings
from typing import Dict, List, Optional, Tuple
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

logger = logging.getLogger(__name__)


# OpenAI parameters:
openai_client = None
# huggingface parameters:
hf_pipeline = None

LLM_SYSTEM_PROMPT = "You are a children's storyteller."

class StoryGeneratorException(Exception):
    pass


def initialize():
    """ Initialize the LLMs and pipelines based on configuration. """
    global openai_client
    global hf_pipeline
    
    if settings.LLM_METHOD == "openai":
        openai_client = AsyncOpenAI(
            base_url=settings.LLM_OPENAI_API_URL,
            api_key=settings.LLM_OPENAI_API_KEY
        )
    elif settings.LLM_METHOD == "huggingface":
        hf_tokenizer = AutoTokenizer.from_pretrained(settings.LLM_HUGGINGFACE_MODEL)
        hf_model = AutoModelForCausalLM.from_pretrained(settings.LLM_HUGGINGFACE_MODEL, device_map="auto")
        hf_pipeline = pipeline("text-generation", model=hf_model, tokenizer=hf_tokenizer)


class Stage(StrEnum):
    INTRO = "Introduction"
    RISING = "Rising Action"
    CLIMAX = "Climax"
    RESOLUTION = "Resolution"
    
class StageManager:
    
    STAGE_HINTS = {
        Stage.INTRO: "This is the introduction. Focus on setting the scene, introducing characters, and hinting at the quest or conflict.",
        Stage.RISING: "This is the rising action. Add challenges, discoveries, or surprises that keep the story moving toward the climax.",
        Stage.CLIMAX: "This is the climax. Make this the most exciting and important challenge of the quest. Set up the resolution.",
        Stage.RESOLUTION: "This is the resolution. Wrap up the story with a satisfying, happy conclusion that ties back to the quest."
    }

    def __init__(self, total_steps: int, stage_plan: Optional[Dict[str, int]] = None):
        self.total_steps = total_steps
        self.stage_order = [Stage.INTRO, Stage.RISING, Stage.CLIMAX, Stage.RESOLUTION]
        # generate a plan if not provided:
        if stage_plan is None:
            self.plan = self.generate_plan(total_steps)
        else:
            # Convert string keys to Stage enum keys
            self.plan = self._convert_string_plan_to_enum(stage_plan)

    def generate_plan(self, total_steps: int) -> Dict[Stage, int]:
        proportions = {
            Stage.INTRO: (0.1, 0.2),        # 10-20% of steps
            Stage.RISING: (0.4, 0.6),       # 40-60% of steps
            Stage.CLIMAX: (0.15, 0.25),     # 15-25% of steps
            Stage.RESOLUTION: (0.1, 0.2)    # 10-20% of steps
        }
        # Randomly allocate a fraction for each stage:
        raw_alloc = {
            s: random.uniform(lo, hi)
            for s, (lo, hi) in proportions.items()
        }
        # Normalize so total fraction = 1:
        total_frac = sum(raw_alloc.values())
        norm_alloc = {
            stage: frac / total_frac
            for stage, frac in raw_alloc.items()
        }
        # convert to step counts:
        stage_steps = {
            stage: int(round(norm_alloc[stage] * total_steps))
            for stage in norm_alloc
        }
        # Adjust step count for rounding errors:
        diff = total_steps - sum(stage_steps.values())
        while diff != 0:
            stage = random.choice(self.stage_order)
            if diff > 0:
                stage_steps[stage] += 1
                diff -= 1
            elif diff < 0 and stage_steps[stage] > 1:
                stage_steps[stage] -= 1
                diff += 1

        return stage_steps

    def _convert_string_plan_to_enum(self, stage_plan: Dict[str, int]) -> Dict[Stage, int]:
        """ Convert string keys to Stage enum keys. """
        enum_plan = {}
        for stage_name, count in stage_plan.items():
            # Find the matching Stage enum by value
            for stage_enum in Stage:
                if stage_enum.value == stage_name:
                    enum_plan[stage_enum] = count
                    break
        return enum_plan
    
    def get_plan_as_strings(self) -> Dict[str, int]:
        """ Convert the internal enum-based plan to string keys for API response. """
        return {stage.value: count for stage, count in self.plan.items()}

    def get_stage_guidance(self, step: int) -> str:
        """ Return the stage for the given step (1-indexed). """
        cumulative = 0
        for stage in self.stage_order:
            cumulative += self.plan[stage]
            if step <= cumulative:
                return self.STAGE_HINTS[stage]
        # fallback
        stage = self.stage_order[-1]
        return self.STAGE_HINTS[stage]


def build_story_prompt(prompt: StoryPrompt, history: List[str], choice: Optional[str], stage_guidance: str) -> str:
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
        for i, para in enumerate(history, start=1):
            instructions.append(f"Part {i}: {para}")
        instructions.append("")

        instructions.append((
            f"The child chose the following option for the next part of the story: '{choice}'."
            "Continue the story based on that choice."
        ))

    # Instruction to generate next part
    instructions.append("Now write the next paragraph of the story, only write one paragraph at a time.")
    instructions.append(f"Current story stage: {stage_guidance}")
    instructions.append(f"The story should have a total of {prompt.length} paragraphs, so make sure to adjust the storyline and progression accordingly.")
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


async def llm_get_story_json_openai(prompt) -> str:
    try:
        response = await openai_client.chat.completions.create(
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
    

async def llm_get_story_json_ollama(prompt: str) -> str:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.LLM_OLLAMA_API_URL,
                json={
                    "model": settings.LLM_OLLAMA_MODEL,
                    "system": LLM_SYSTEM_PROMPT,
                    "prompt": prompt,
                    "stream": False
                },
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            response.raise_for_status()
            return response.json()["response"]
    except httpx.HTTPStatusError as exc:
        raise StoryGeneratorException(f"HTTP error from Ollama LLM:: {str(exc)}")
    except httpx.RequestError as exc:
        raise StoryGeneratorException(f"Network error calling Ollama LLM: {str(exc)}")
    except (KeyError, TypeError) as exc:
        raise StoryGeneratorException(f"Invalid LLM response: {str(exc)}")
    
    
async def llm_get_story_json_huggingface(prompt) -> str:
    try:
        prompt = f"{LLM_SYSTEM_PROMPT}\n\n{prompt}"
        result = await run_in_threadpool(
            hf_pipeline,
            prompt,
            max_new_tokens=300,
            temperature=0.8,
            do_sample=True
        )
        return result[0]["generated_text"]
    except Exception as exc:
        raise StoryGeneratorException(f"Error calling HuggingFace LLM: {str(exc)}")
        

async def llm_generate_story(request: StoryRequest):
    """ Call an LLM to generate a Choose-your-own-adventure style story. """
        
    logger.info(f"Generating story based on story request: {request}")

    # Create stage manager to get/create the stage plan:
    stage_manager = StageManager(request.prompt.length, request.stage_plan)
    stage_guidance = stage_manager.get_stage_guidance(len(request.history))
    stage_plan = stage_manager.get_plan_as_strings()
    logger.info(f"Story stage plan: {stage_plan}")

    prompt = build_story_prompt(request.prompt, request.history, request.choice, stage_guidance)
    logger.info(f"Generated prompt for LLM: {prompt}")
    
    if settings.LLM_METHOD == "openai":
        json_content = await llm_get_story_json_openai(prompt)
    elif settings.LLM_METHOD == "ollama":
        json_content = await llm_get_story_json_ollama(prompt)
    elif settings.LLM_METHOD == "huggingface":
        json_content = await llm_get_story_json_huggingface(prompt)
    else:
        raise StoryGeneratorException(f"Unsupported LLM method: {settings.LLM_METHOD}") 
    
    try:
        # strip whitespace, backticks and quotes:
        json_content = json_content.strip().strip("`'\"")
        logger.info(f"LLM response content: {json_content}")
        story = json.loads(json_content)
    except json.JSONDecodeError as exc:
        raise StoryGeneratorException(f"Invalid JSON from LLM: {str(exc)}")
    
    return story["paragraph"], story["choices"], stage_plan
