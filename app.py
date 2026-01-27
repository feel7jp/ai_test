import os
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
import requests

load_dotenv()
app = Flask(__name__)

try:
    from google import genai
except Exception:  # pragma: no cover - handled at runtime
    genai = None


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set in the environment.")
    if genai is None:
        raise RuntimeError(
            "google-genai is not installed. Run: pip install -r requirements.txt"
        )
    http_options = {}
    api_version = os.getenv("GEMINI_API_VERSION")
    if api_version:
        http_options["api_version"] = api_version
    return genai.Client(api_key=api_key, http_options=http_options or None)


def get_provider(payload):
    return (payload.get("provider") or os.getenv("LLM_PROVIDER") or "gemini").lower()


def normalize_history(raw_history, max_items):
    normalized = []
    for item in raw_history[-max_items:]:
        role = item.get("role")
        content = (item.get("content") or "").strip()
        if role in {"user", "model"} and content:
            normalized.append({"role": role, "content": content})
    return normalized


def build_gemini_history(history):
    return [
        {"role": item["role"], "parts": [{"text": item["content"]}]}
        for item in history
    ]


def build_lmstudio_messages(history, message):
    messages = []
    for item in history:
        mapped_role = "assistant" if item["role"] == "model" else "user"
        messages.append({"role": mapped_role, "content": item["content"]})
    messages.append({"role": "user", "content": message})
    return messages


def call_gemini(message, history, model_override=None):
    client = get_client()
    contents = build_gemini_history(history)
    model_name = model_override or os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")
    chat_session = client.chats.create(model=model_name, history=contents)
    response = chat_session.send_message(message)
    return response.text or ""


def list_lmstudio_models():
    base_url = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1").rstrip("/")
    api_key = os.getenv("LMSTUDIO_API_KEY")
    endpoint = f"{base_url}/models"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    response = requests.get(endpoint, headers=headers, timeout=10)
    if not response.ok:
        raise RuntimeError(
            f"LM Studio models error: {response.status_code} {response.text}"
        )
    data = response.json()
    return [item.get("id") for item in data.get("data", []) if item.get("id")]


def call_lmstudio(message, history, model_override=None):
    base_url = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1").rstrip("/")
    api_key = os.getenv("LMSTUDIO_API_KEY")
    endpoint = f"{base_url}/chat/completions"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    model = model_override or os.getenv("LMSTUDIO_MODEL")
    if not model or model == "auto":
        models = list_lmstudio_models()
        if not models:
            raise RuntimeError("No LM Studio models are available.")
        model = models[0]

    payload = {
        "model": model,
        "messages": build_lmstudio_messages(history, message),
        "temperature": float(os.getenv("LMSTUDIO_TEMPERATURE", "0.7")),
    }
    response = requests.post(endpoint, json=payload, headers=headers, timeout=60)
    if not response.ok:
        raise RuntimeError(f"LM Studio error: {response.status_code} {response.text}")
    data = response.json()
    return (data.get("choices") or [{}])[0].get("message", {}).get("content", "") or ""


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/models")
def models():
    provider = get_provider(request.args or {})
    if provider == "gemini":
        model_name = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")
        return jsonify({"models": [model_name]})
    if provider == "lmstudio":
        try:
            return jsonify({"models": list_lmstudio_models()})
        except Exception as exc:  # pragma: no cover
            return jsonify({"error": str(exc)}), 500
    return jsonify({"error": f"Unknown provider: {provider}"}), 400


@app.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    message = (payload.get("message") or "").strip()
    history = payload.get("history") or []
    model_override = (payload.get("model") or "").strip() or None

    if not message:
        return jsonify({"error": "Message is required."}), 400
    max_chars = int(os.getenv("MAX_MESSAGE_CHARS", "4000"))
    if len(message) > max_chars:
        return jsonify({"error": f"Message is too long (max {max_chars})."}), 400

    try:
        provider = get_provider(payload)
        max_history = int(os.getenv("MAX_HISTORY", "20"))
        normalized_history = normalize_history(history, max_history)
        if provider == "gemini":
            reply = call_gemini(message, normalized_history, model_override)
        elif provider == "lmstudio":
            reply = call_lmstudio(message, normalized_history, model_override)
        else:
            return jsonify({"error": f"Unknown provider: {provider}"}), 400
        return jsonify({"reply": reply})
    except Exception as exc:  # pragma: no cover - return error to UI
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(debug=True, port=port)
