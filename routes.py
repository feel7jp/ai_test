from flask import Blueprint, jsonify, render_template, request

from services.chat import available_models, chat_reply, normalize_history
from settings import get_provider, gemini_model, max_history, max_message_chars

routes = Blueprint("routes", __name__)


@routes.get("/")
def index():
    return render_template("index.html")


@routes.get("/api/models")
def models():
    provider = get_provider(request.args or {})
    if provider == "gemini":
        try:
            models = available_models(provider)
        except Exception:  # pragma: no cover
            models = []
        if not models:
            models = [gemini_model()]
        return jsonify({"models": models})
    if provider == "lmstudio":
        try:
            return jsonify({"models": available_models(provider)})
        except Exception as exc:  # pragma: no cover
            return jsonify({"error": str(exc)}), 500
    return jsonify({"error": f"Unknown provider: {provider}"}), 400


@routes.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    message = (payload.get("message") or "").strip()
    history = payload.get("history") or []
    model_override = (payload.get("model") or "").strip() or None

    if not message:
        return jsonify({"error": "Message is required."}), 400
    max_chars = max_message_chars()
    if len(message) > max_chars:
        return jsonify({"error": f"Message is too long (max {max_chars})."}), 400

    try:
        provider = get_provider(payload)
        normalized_history = normalize_history(history, max_history())
        reply = chat_reply(provider, message, normalized_history, model_override)
        return jsonify({"reply": reply})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:  # pragma: no cover - return error to UI
        return jsonify({"error": str(exc)}), 500
