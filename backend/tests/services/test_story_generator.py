import pytest
import json
from app.core.config import settings
from unittest.mock import AsyncMock, patch
from app.services.story_generator import (
    build_story_prompt,
    llm_generate_story,
    initialize,
    LLM_SYSTEM_PROMPT,
    StoryGeneratorException,
)
from app.schemas.story import StoryRequest, StoryPrompt, Character
from openai import OpenAIError


class TestBuildStoryPrompt:
    def test_new_story_basic_prompt(self):
        basic_prompt = StoryPrompt(age=9, language="english", length=10)
        prompt = build_story_prompt(basic_prompt, [], None)
        assert "Write a fun, engaging Choose-your-own-adventure" in prompt
        assert "9-year-old child in english" in prompt      
        assert "Now write the next paragraph of the story" in prompt
        assert "The story should have a total of 10 paragraphs" in prompt
        assert "Then offer 2 or 3 engaging choices for what could happen next." in prompt
        assert "Format the response as a JSON object" in prompt
        
        assert "Here is the story so far:" not in prompt
        assert "The child chose the following option for the next part of the story:" not in prompt

    def test_new_story_full_prompt(self):
        full_prompt = StoryPrompt(
            age=8,
            language="french",
            length=5,
            prompt="A story about Alice and Bob",
            characters=[
                Character(name="Alice", type="child", gender="girl", personality="brave"),
                Character(name="Bob", type="animal", gender="boy", personality="kind"),
            ],
            environment="forest",
            theme="friendship",
            tone="friendly",
            conflict_type="quest",
            ending_style="happy",
        )
        
        prompt = build_story_prompt(full_prompt, [], None)
        assert "The story should also follow this prompt: 'A story about Alice and Bob'" in prompt
        assert "Alice who is a child with a girl gender and a brave personality" in prompt
        assert "Bob who is a animal with a boy gender and a kind personality" in prompt
        assert "The story takes place in the following environment: forest" in prompt
        assert "The theme of the story is: friendship." in prompt
        assert "The story should have a friendly tone." in prompt
        assert "The story should include a conflict of type: quest." in prompt
        assert "The story ending style should be: happy style." in prompt
        
    def test_story_with_history_and_choice(self):
        history = ["Once upon a time, Alice and Bob went on an adventure.", "They found a cave."]
        choice = "Explore the cave"
        prompt = build_story_prompt(
            StoryPrompt(age=8, language="english", length=5),
            history,
            choice
        )
        assert "Here is the story so far:" in prompt
        assert f"Part 1: {history[0]}" in prompt
        assert f"Part 2: {history[1]}" in prompt
        assert f"The child chose the following option for the next part of the story: '{choice}'." in prompt
        assert "Continue the story based on that choice." in prompt
        
        assert "The story is getting close to the end" not in prompt
        assert "The story has reached the desired length" not in prompt
        
    def test_story_close_to_end(self):
        history = ["Once upon a time, Alice and Bob went on an adventure.", "They found a cave."]
        choice = "Explore the cave"
        prompt = build_story_prompt(
            StoryPrompt(age=8, language="english", length=4),
            history,
            choice
        )
        assert "The story is getting close to the end, so make sure to start wrapping it up." in prompt
        assert "The story has reached the desired length" not in prompt
        
    def test_story_ending(self):
        history = ["Once upon a time, Alice and Bob went on an adventure.", "They found a cave."]
        choice = "Explore the cave"
        prompt = build_story_prompt(
            StoryPrompt(age=8, language="english", length=3),
            history,
            choice
        )
        assert "The story is getting close to the end, so make sure to start wrapping it up." not in prompt
        assert "The story has reached the desired length, so end it with a satisfying conclusion." in prompt


@pytest.fixture
def sample_story_request():
    return StoryRequest(
        prompt=StoryPrompt(
            age=8,
            language="english",
            length=5,
            characters=[
                Character(name="Alice", type="child", gender="girl", personality="brave"),
                Character(name="Bob", type="animal", gender="boy", personality="kind"),
            ],
            environment="forest",
            theme="friendship",
            tone="friendly",
            conflict_type="quest",
            ending_style="happy",
        ),
        history=["Once upon a time, Alice and Bob went on an adventure."],
        choice="Explore the cave",
    )

@pytest.fixture
def mock_openai_client(mocker):
    """ Fixture to mock OpenAI client and LLM response. """
    mock_client = mocker.patch("app.services.story_generator.AsyncOpenAI").return_value
    # make sure to use AsyncMock to mock async method:
    mock_client.chat.completions.create = AsyncMock()
    # call initialize to ensure the mocked client is set up correctly:
    initialize()
    return mock_client

@pytest.fixture
def mock_ollama_client(mocker):
    """ Fixture to robustly mock Ollama client with async context manager. """
    # Create a mock client with async context manager support    
    mock_client = mocker.patch("httpx.AsyncClient").return_value
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.post = AsyncMock()    
    return mock_client

VALID_JSON_RESPONSE = {
    "paragraph": "Alice and Bob entered the cave.",
    "choices": ["Go deeper", "Leave the cave"]
}

class FakePostResponse():
    def __init__(self, status_code, response):
        self.status_code = status_code
        self.response = response

    def json(self):
        return {"response": self.response}

    def raise_for_status(self):
        pass


class TestLLMGenerateStory:
    
    @pytest.mark.asyncio
    @patch("app.services.story_generator.settings.LLM_METHOD", "openai")
    async def test_llm_generate_story_openai(self, mocker, mock_openai_client, sample_story_request):
        mock_openai_client.chat.completions.create.return_value = mocker.Mock(
            choices=[mocker.Mock(message=mocker.Mock(content=json.dumps(VALID_JSON_RESPONSE)))]
        )
        paragraph, choices = await llm_generate_story(sample_story_request)
        
        expected_prompt = build_story_prompt(
            sample_story_request.prompt,
            sample_story_request.history,
            sample_story_request.choice
        )
        mock_openai_client.chat.completions.create.assert_called_once_with(
            model=settings.LLM_OPENAI_MODEL,
            messages=[
                {"role": "system", "content": LLM_SYSTEM_PROMPT},
                {"role": "user", "content": expected_prompt}
            ]
        )
        assert paragraph == VALID_JSON_RESPONSE["paragraph"]
        assert choices == VALID_JSON_RESPONSE["choices"]
        
    @pytest.mark.asyncio
    @patch("app.services.story_generator.settings.LLM_METHOD", "openai")
    async def test_openai_error_raises(self, mock_openai_client, sample_story_request):
        mock_openai_client.chat.completions.create.side_effect = OpenAIError("API Error")
        with pytest.raises(StoryGeneratorException, match="Error calling LLM API: API Error"):
            await llm_generate_story(sample_story_request)
            
    @pytest.mark.asyncio
    @patch("app.services.story_generator.settings.LLM_METHOD", "openai")
    async def test_openai_invalid_response_raises(self, mock_openai_client, sample_story_request):
        mock_openai_client.chat.completions.create.return_value = None
        with pytest.raises(StoryGeneratorException, match="Invalid LLM response"):
            await llm_generate_story(sample_story_request)
            
    @pytest.mark.asyncio
    @patch("app.services.story_generator.settings.LLM_METHOD", "openai")
    async def test_openai_invalid_json_raises(self, mocker, mock_openai_client, sample_story_request):
        mock_openai_client.chat.completions.create.return_value = mocker.Mock(
            choices=[mocker.Mock(message=mocker.Mock(content="invalid json"))]
        )
        with pytest.raises(StoryGeneratorException, match="Invalid JSON from LLM"):
            await llm_generate_story(sample_story_request)
    
    
    @pytest.mark.asyncio
    @patch("app.services.story_generator.settings.LLM_METHOD", "ollama")
    async def test_llm_generate_story_ollama(self, mock_ollama_client, sample_story_request):
        mock_ollama_client.post.return_value = FakePostResponse(
            status_code=200,
            response=json.dumps(VALID_JSON_RESPONSE)
        )
        paragraph, choices = await llm_generate_story(sample_story_request)
        
        expected_prompt = build_story_prompt(
            sample_story_request.prompt,
            sample_story_request.history,
            sample_story_request.choice
        )
        mock_ollama_client.post.assert_called_once_with(
            settings.LLM_OLLAMA_API_URL,
                json={
                    "model": settings.LLM_OLLAMA_MODEL,
                    "system": LLM_SYSTEM_PROMPT,
                    "prompt": expected_prompt,
                    "stream": False
                },
                headers={"Content-Type": "application/json"},
                timeout=60
        )
        assert paragraph == VALID_JSON_RESPONSE["paragraph"]
        assert choices == VALID_JSON_RESPONSE["choices"]
        
    # TODO: write tests for HuggingFace LLM, once it's working properly

"""
    @pytest.mark.asyncio
    @patch("app.services.story_generator.llm_get_story_json_ollama")
    async def test_llm_generate_story_ollama(mock_llm_get_story_json_ollama, sample_story_request):
        mock_llm_get_story_json_ollama.return_value = '{"paragraph": "Alice and Bob found a treasure.", "choices": ["Take the treasure", "Leave it"]}'
        
        with patch("app.services.story_generator.settings.LLM_METHOD", "ollama"):
            paragraph, choices = await llm_generate_story(sample_story_request)
        
        assert paragraph == "Alice and Bob found a treasure."
        assert choices == ["Take the treasure", "Leave it"]
        mock_llm_get_story_json_ollama.assert_called_once()


    @pytest.mark.asyncio
    @patch("app.services.story_generator.llm_get_story_json_huggingface")
    async def test_llm_generate_story_huggingface(mock_llm_get_story_json_huggingface, sample_story_request):
        mock_llm_get_story_json_huggingface.return_value = '{"paragraph": "Alice and Bob climbed a tree.", "choices": ["Climb higher", "Climb down"]}'
        
        with patch("app.services.story_generator.settings.LLM_METHOD", "huggingface"):
            paragraph, choices = await llm_generate_story(sample_story_request)
        
        assert paragraph == "Alice and Bob climbed a tree."
        assert choices == ["Climb higher", "Climb down"]
        mock_llm_get_story_json_huggingface.assert_called_once()


    @pytest.mark.asyncio
    async def test_llm_generate_story_invalid_method(sample_story_request):
        with patch("app.services.story_generator.settings.LLM_METHOD", "invalid_method"):
            with pytest.raises(StoryGeneratorException, match="Unsupported LLM method: invalid_method"):
                await llm_generate_story(sample_story_request)


    @pytest.mark.asyncio
    @patch("app.services.story_generator.llm_get_story_json_openai")
    async def test_llm_generate_story_invalid_json(mock_llm_get_story_json_openai, sample_story_request):
        mock_llm_get_story_json_openai.return_value = "Invalid JSON response"
        
        with patch("app.services.story_generator.settings.LLM_METHOD", "openai"):
            with pytest.raises(StoryGeneratorException, match="Invalid JSON from LLM"):
                await llm_generate_story(sample_story_request)
"""
