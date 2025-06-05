from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    LLM_METHOD: str = "openai"
    
    LLM_OPENAI_API_URL: str = "https://api.groq.com/openai/v1" # Groq API is OpenAI compatible
    LLM_OPENAI_API_KEY: str
    LLM_OPENAI_MODEL: str = "meta-llama/llama-4-maverick-17b-128e-instruct" #"llama-3.3-70b-versatile"
    
    LLM_OLLAMA_MODEL: str = "mistral"
    LLM_OLLAMA_API_URL: str = "http://localhost:11434/api/generate"
    
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")
    
settings = Settings()

