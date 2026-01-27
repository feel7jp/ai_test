import requests

from settings import (
    gemini_api_key,
    gemini_api_version,
    gemini_model,
    lmstudio_api_key,
    lmstudio_base_url,
    lmstudio_model,
    lmstudio_temperature,
)

try:
    from google import genai
except Exception:  # pragma: no cover - handled at runtime
    genai = None


def _gemini_client():
    api_key = gemini_api_key()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set in the environment.")
    if genai is None:
        raise RuntimeError(
            "google-genai is not installed. Run: pip install -r requirements.txt"
        )
    http_options = {}
    api_version = gemini_api_version()
    if api_version:
        http_options["api_version"] = api_version
    return genai.Client(api_key=api_key, http_options=http_options or None)


def _gemini_history(history):
    return [
        {"role": item["role"], "parts": [{"text": item["content"]}]}
        for item in history
    ]


def _lmstudio_headers():
    headers = {"Content-Type": "application/json"}
    api_key = lmstudio_api_key()
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def _lmstudio_messages(history, message):
    messages = []
    for item in history:
        mapped_role = "assistant" if item["role"] == "model" else "user"
        messages.append({"role": mapped_role, "content": item["content"]})
    messages.append({"role": "user", "content": message})
    return messages


def list_models(provider):
    if provider == "gemini":
        client = _gemini_client()
        models = []
        for model in client.models.list():
            name = getattr(model, "name", None)
            if not name:
                continue
            if "embedding" in name or "imagen" in name or "veo" in name:
                continue
            models.append(name)
        return models
    if provider == "lmstudio":
        endpoint = f"{lmstudio_base_url()}/models"
        response = requests.get(endpoint, headers=_lmstudio_headers(), timeout=10)
        if not response.ok:
            raise RuntimeError(
                f"LM Studio models error: {response.status_code} {response.text}"
            )
        data = response.json()
        return [item.get("id") for item in data.get("data", []) if item.get("id")]
    raise ValueError(f"Unknown provider: {provider}")


def send_message(provider, message, history, model_override=None):
    if provider == "gemini":
        client = _gemini_client()
        contents = _gemini_history(history)
        model_name = model_override or gemini_model()
        chat_session = client.chats.create(model=model_name, history=contents)
        response = chat_session.send_message(message)
        return response.text or ""
    if provider == "lmstudio":
        endpoint = f"{lmstudio_base_url()}/chat/completions"
        model = model_override or lmstudio_model()
        if not model or model == "auto":
            models = list_models("lmstudio")
            if not models:
                raise RuntimeError("No LM Studio models are available.")
            model = models[0]

        payload = {
            "model": model,
            "messages": _lmstudio_messages(history, message),
            "temperature": lmstudio_temperature(),
        }
        response = requests.post(
            endpoint, json=payload, headers=_lmstudio_headers(), timeout=60
        )
        if not response.ok:
            raise RuntimeError(f"LM Studio error: {response.status_code} {response.text}")
        data = response.json()
        return (
            (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
            or ""
        )
    raise ValueError(f"Unknown provider: {provider}")
