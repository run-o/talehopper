from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # we're using Groq API here which is OpenAI compatible:
    LLM_API_URL: str = "https://api.groq.com/openai/v1"
    LLM_API_KEY: str
    LLM_MODEL: str = "meta-llama/llama-4-maverick-17b-128e-instruct" #"llama-3.3-70b-versatile"
    
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")
    
settings = Settings()

