import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    # llama-3.1-70b-versatile is highly recommended for strict JSON adherence
    MODEL_NAME = "llama-3.3-70b-versatile"

settings = Settings()