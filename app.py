import os
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

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


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    message = (payload.get("message") or "").strip()
    history = payload.get("history") or []

    if not message:
        return jsonify({"error": "Message is required."}), 400

    try:
        client = get_client()
        contents = []
        for item in history:
            role = item.get("role")
            content = item.get("content")
            if role in {"user", "model"} and content:
                contents.append({"role": role, "parts": [{"text": content}]})

        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        chat_session = client.chats.create(model=model_name, history=contents)
        response = chat_session.send_message(message)
        reply = response.text or ""
        return jsonify({"reply": reply})
    except Exception as exc:  # pragma: no cover - return error to UI
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(debug=True, port=port)
