import os

class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "a_long_random_fallback_secret_key_if_env_not_loaded_PLEASE_CHANGE_ME")
    UPLOAD_FOLDER = 'uploads'
    CHROMA_DB_DIR = 'chroma_db'
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    # Interview specific configs
    MAX_FOUNDATIONAL_QUESTIONS = 3
    JOB_ROLE = "Software Engineer" # Default job role for LLM prompts

    # Ensure necessary folders exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(CHROMA_DB_DIR, exist_ok=True)

    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not found in .env file. Please set it.")
    if SECRET_KEY == "a_long_random_fallback_secret_key_if_env_not_loaded_PLEASE_CHANGE_ME":
        print("WARNING: FLASK_SECRET_KEY not set in .env. Using a default. Please set a strong, random key in your .env for production!")