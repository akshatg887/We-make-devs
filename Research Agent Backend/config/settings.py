import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Keys with fallbacks
    CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY", "demo_key")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "demo_key")
    SEARCHAPI_API_KEY = os.getenv("SEARCHAPI_API_KEY", "demo_key")
    
    # Model Configurations with updated Groq models
    MODELS = {
        "gpt_oss_120b": {"cerebras": "llama-4-Maverick", "groq": "llama-3.1-70b-versatile"},
        "llama_70b": {"cerebras": "llama-4-Maverick", "groq": "llama-3.1-70b-versatile"},
        "qwen_480b": {"cerebras": "llama-4-Maverick", "groq": "llama-3.1-8b-instant"}
    }
    
    # Provider priority
    PROVIDER_PRIORITY = ["cerebras", "groq"]
    
    # Development settings
    USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "False").lower() == "true"

settings = Settings()