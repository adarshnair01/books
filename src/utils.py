import os
from dotenv import load_dotenv

def load_env():
    """Load environment variables and check for API keys."""
    load_dotenv()
    if not os.getenv("GEMINI_API_KEY"):
        raise EnvironmentError(
            "GEMINI_API_KEY not found in environment variables. "
            "Please add it to the .env file."
        )

def get_gemini_api_key():
    return os.getenv("GEMINI_API_KEY")
