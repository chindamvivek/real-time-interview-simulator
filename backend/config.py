import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

# --- Gemini LLM Config ---
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# --- Resume Upload Config ---
MAX_FILE_SIZE_MB: int = 5
ALLOWED_EXTENSIONS: list[str] = [".pdf", ".docx"]

# --- Session Config ---
SESSION_TTL_HOURS: int = 2

# --- CORS Config (Next.js dev server) ---
ALLOWED_ORIGINS: list[str] = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

def validate_config() -> None:
    """
    Call this at startup to catch missing required config early.
    Raises ValueError if a required config value is missing.
    """
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is not set. "
            "Create a backend/.env file and add: GEMINI_API_KEY=your_key_here"
        )
