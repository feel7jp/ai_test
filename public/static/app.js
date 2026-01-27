const chatEl = document.getElementById("chat");
const formEl = document.getElementById("chat-form");
const messageEl = document.getElementById("message");
const providerEl = document.getElementById("provider");
const modelEl = document.getElementById("model");

const history = [];

const appendMessage = (role, text) => {
  const wrapper = document.createElement("div");
  wrapper.className = `bubble ${role}`;
  wrapper.textContent = text;
  chatEl.appendChild(wrapper);
  chatEl.scrollTop = chatEl.scrollHeight;
};

let loadingBubble = null;

const setLoading = (isLoading) => {
  formEl.querySelector("button").disabled = isLoading;
  messageEl.disabled = isLoading;
  if (isLoading) {
    loadingBubble = document.createElement("div");
    loadingBubble.className = "bubble model";
    loadingBubble.textContent = "...";
    chatEl.appendChild(loadingBubble);
    chatEl.scrollTop = chatEl.scrollHeight;
  } else if (loadingBubble) {
    loadingBubble.remove();
    loadingBubble = null;
  }
};

formEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = messageEl.value.trim();
  if (!text) return;

  appendMessage("user", text);
  history.push({ role: "user", content: text });
  messageEl.value = "";

  setLoading(true);
  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        history,
        provider: providerEl ? providerEl.value : "gemini",
        model: modelEl ? modelEl.value : "",
      }),
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error || "Unknown error");
    }
    setLoading(false);
    appendMessage("model", data.reply);
    history.push({ role: "model", content: data.reply });
  } catch (err) {
    setLoading(false);
    appendMessage("model", `エラー: ${err.message}`);
  } finally {
    setLoading(false);
  }
});

messageEl.addEventListener("input", () => {
  messageEl.style.height = "auto";
  messageEl.style.height = `${messageEl.scrollHeight}px`;
});

const loadModels = async () => {
  if (!providerEl || !modelEl) return;
  modelEl.innerHTML = "";
  const res = await fetch(`/api/models?provider=${providerEl.value}`);
  const data = await res.json();
  if (!res.ok) {
    appendMessage("model", `モデル取得エラー: ${data.error || "Unknown error"}`);
    return;
  }
  (data.models || []).forEach((name) => {
    const option = document.createElement("option");
    option.value = name;
    option.textContent = name;
    modelEl.appendChild(option);
  });
};

if (providerEl) {
  providerEl.addEventListener("change", loadModels);
  loadModels();
}
