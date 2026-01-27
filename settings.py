import os
from dotenv import load_dotenv

load_dotenv()


def get_provider(payload):
    return (payload.get("provider") or os.getenv("LLM_PROVIDER") or "gemini").lower()


def gemini_api_key():
    return os.getenv("GEMINI_API_KEY")


def gemini_model():
    return os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")


def gemini_api_version():
    return os.getenv("GEMINI_API_VERSION")


def lmstudio_base_url():
    return os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1").rstrip("/")


def lmstudio_model():
    return os.getenv("LMSTUDIO_MODEL")


def lmstudio_api_key():
    return os.getenv("LMSTUDIO_API_KEY")


def lmstudio_temperature():
    return float(os.getenv("LMSTUDIO_TEMPERATURE", "0.7"))


def max_message_chars():
    return int(os.getenv("MAX_MESSAGE_CHARS", "4000"))


def max_history():
    return int(os.getenv("MAX_HISTORY", "20"))


def port():
    return int(os.getenv("PORT", "5000"))
