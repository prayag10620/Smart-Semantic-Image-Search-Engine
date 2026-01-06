# backend/app/core/config.py
import os
from dotenv import load_dotenv #type:ignore

load_dotenv() # Load .env file

class Settings:
    
    # Get the backend directory (assuming this file is in app/core/)
    # We want to go up two levels: app/core/ -> app/ -> backend/
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Define the Data Directory inside backend/
    DATA_DIR = os.path.join(BASE_DIR, "data")

    # Specific sub-folders
    UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
    FACES_DIR = os.path.join(DATA_DIR, "faces")
    QDRANT_PATH = os.path.join(DATA_DIR, "qdrant_data")
    # AI PROVIDER SETTINGS
    # Options: "ollama", "groq"
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq") 
    
    # Ollama Settings
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("LLM_MODEL","llama3")

    # Groq Settings (Get key from console.groq.com)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = os.getenv("LLM_MODEL","openai/gpt-oss-120b") # Faster and smarter than local llama3

    # AUTH SETTINGS
    SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_random_string_change_this")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # Path for the User DB
    SQLITE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'users.db')}"
    
    def __init__(self):
        # Ensure these folders exist when the app starts
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        os.makedirs(self.FACES_DIR, exist_ok=True)
        os.makedirs(self.QDRANT_PATH, exist_ok=True)

settings = Settings()