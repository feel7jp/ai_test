from providers.llm import list_models, send_message


def normalize_history(raw_history, max_items):
    normalized = []
    for item in raw_history[-max_items:]:
        role = item.get("role")
        content = (item.get("content") or "").strip()
        if role in {"user", "model"} and content:
            normalized.append({"role": role, "content": content})
    return normalized


def chat_reply(provider, message, history, model_override=None):
    return send_message(provider, message, history, model_override)


def available_models(provider):
    return list_models(provider)
