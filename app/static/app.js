const state = {
  sessionId: null,
  busy: false,
};

const els = {
  messages: document.querySelector("#messages"),
  form: document.querySelector("#chatForm"),
  input: document.querySelector("#messageInput"),
  send: document.querySelector("#sendButton"),
  sessionId: document.querySelector("#sessionId"),
  sessionStatus: document.querySelector("#sessionStatus"),
  domain: document.querySelector("#domainSelect"),
  region: document.querySelector("#regionInput"),
  stream: document.querySelector("#streamToggle"),
  stageStrip: document.querySelector("#stageStrip"),
  clear: document.querySelector("#clearButton"),
  newChat: document.querySelector("#newChatButton"),
};

els.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = els.input.value.trim();
  if (!message || state.busy) return;

  addMessage("user", "你", message);
  els.input.value = "";
  resizeInput();
  setBusy(true);
  clearStages();

  const payload = buildPayload(message);
  try {
    if (els.stream.checked) {
      await sendStream(payload);
    } else {
      const response = await fetchJson("/legal-qa", payload);
      applyFinalResponse(response);
    }
  } catch (error) {
    addMessage("assistant", "法律 RAG 助手", `请求失败: ${error.message}`, { status: "error" });
    setStatus("error");
  } finally {
    setBusy(false);
  }
});

els.input.addEventListener("input", resizeInput);
els.input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    els.form.requestSubmit();
  }
});

els.clear.addEventListener("click", () => {
  els.messages.innerHTML = "";
  addMessage("assistant", "法律 RAG 助手", "页面消息已清空。当前 session 保留, 你可以继续追问。");
});

els.newChat.addEventListener("click", () => {
  state.sessionId = null;
  els.sessionId.textContent = "未创建";
  setStatus("待提问");
  clearStages();
  els.messages.innerHTML = "";
  addMessage("assistant", "法律 RAG 助手", "已开启新对话。请描述你的问题, 我会按事实、依据和风险来整理。");
});

function buildPayload(message) {
  return {
    session_id: state.sessionId,
    message,
    legal_domain: els.domain.value || null,
    region: els.region.value.trim() || null,
  };
}

async function fetchJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message || data.detail || `HTTP ${response.status}`);
  }
  return data;
}

async function sendStream(payload) {
  const response = await fetch("/legal-qa/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/x-ndjson" },
    body: JSON.stringify(payload),
  });
  if (!response.ok || !response.body) {
    const text = await response.text();
    throw new Error(text || `HTTP ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";
    for (const line of lines) {
      if (!line.trim()) continue;
      handleStreamEvent(JSON.parse(line));
    }
  }
  if (buffer.trim()) handleStreamEvent(JSON.parse(buffer));
}

function handleStreamEvent(event) {
  if (event.type === "session") {
    setSession(event.session_id);
    return;
  }
  if (event.type === "stage") {
    addStage(event.agent, event.message);
    return;
  }
  if (event.type === "final") {
    applyFinalResponse(event.data);
    return;
  }
  if (["clarification_needed", "fact_conflict", "general_reference", "insufficient_basis", "error"].includes(event.type)) {
    setStatus(event.type);
  }
}

function applyFinalResponse(data) {
  setSession(data.session_id);
  setStatus(data.status);

  if (data.status === "clarification_needed") {
    const text = ["我需要先确认几个关键信息:", ...(data.questions || []).map((item) => `- ${item}`)].join("\n");
    addMessage("assistant", "法律 RAG 助手", text, data);
    return;
  }

  if (data.status === "fact_conflict") {
    const lines = ["我发现前后事实可能有冲突, 请先确认:"];
    for (const conflict of data.conflicts || []) {
      lines.push(`- ${conflict.question}`);
    }
    addMessage("assistant", "法律 RAG 助手", lines.join("\n"), data);
    return;
  }

  const answer = data.final_answer || data.message || "没有生成可展示的回答。";
  addMessage("assistant", "法律 RAG 助手", answer, data);
}

function addMessage(role, name, text, meta = null) {
  const article = document.createElement("article");
  article.className = `message ${role}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "user" ? "你" : "律";

  const bubble = document.createElement("div");
  bubble.className = "bubble";

  const head = document.createElement("div");
  head.className = "message-head";
  head.innerHTML = `<strong>${escapeHtml(name)}</strong><span>${new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>`;

  const content = document.createElement("div");
  content.className = "content";
  content.append(...renderText(text));

  bubble.append(head, content);
  if (meta) bubble.append(renderMeta(meta));
  article.append(avatar, bubble);
  els.messages.appendChild(article);
  els.messages.scrollTop = els.messages.scrollHeight;
}

function renderText(text) {
  const normalized = String(text || "").trim();
  const sectionPattern = /(?=^[一二三四五六七八九十]、)/m;
  const chunks = normalized.split(sectionPattern).filter(Boolean);
  if (chunks.length > 1) {
    return chunks.map((chunk) => {
      const [title, ...rest] = chunk.split("\n");
      const section = document.createElement("section");
      section.className = "answer-section";
      const heading = document.createElement("h3");
      heading.textContent = title.trim();
      section.appendChild(heading);
      for (const paragraph of rest.join("\n").split(/\n{2,}/).filter(Boolean)) {
        const p = document.createElement("p");
        p.textContent = paragraph.trim();
        section.appendChild(p);
      }
      return section;
    });
  }

  return normalized.split(/\n{1,2}/).filter(Boolean).map((paragraph) => {
    const p = document.createElement("p");
    p.textContent = paragraph.trim();
    return p;
  });
}

function renderMeta(meta) {
  const wrap = document.createElement("div");

  const badges = document.createElement("div");
  badges.className = "badge-row";
  if (meta.status) badges.appendChild(badge(`状态: ${meta.status}`, meta.status === "completed" ? "ok" : "warn"));
  if (meta.legal_domain) badges.appendChild(badge(`领域: ${domainLabel(meta.legal_domain)}`));
  if (meta.region) badges.appendChild(badge(`地区: ${meta.region}`));
  if (meta.review?.passed) badges.appendChild(badge("Review 已通过", "ok"));
  wrap.appendChild(badges);

  if (Array.isArray(meta.sources) && meta.sources.length) {
    const sources = document.createElement("div");
    sources.className = "sources";
    for (const source of meta.sources) {
      const card = document.createElement("div");
      card.className = "source-card";
      card.innerHTML = `<h4>${escapeHtml(source.title || "未命名来源")}</h4><p>${escapeHtml(source.source || "")} ${escapeHtml(source.url || "")}</p><p>${escapeHtml(source.quote_text || source.snippet || "")}</p>`;
      sources.appendChild(card);
    }
    wrap.appendChild(sources);
  }
  return wrap;
}

function badge(text, tone = "") {
  const el = document.createElement("span");
  el.className = `badge ${tone}`.trim();
  el.textContent = text;
  return el;
}

function addStage(agent, message) {
  els.stageStrip.hidden = false;
  const chip = document.createElement("span");
  chip.className = "stage-chip";
  chip.textContent = `${agent}: ${message}`;
  els.stageStrip.appendChild(chip);
  els.stageStrip.scrollLeft = els.stageStrip.scrollWidth;
}

function clearStages() {
  els.stageStrip.innerHTML = "";
  els.stageStrip.hidden = true;
}

function setBusy(value) {
  state.busy = value;
  els.send.disabled = value;
  els.input.disabled = value;
}

function setSession(sessionId) {
  state.sessionId = sessionId || state.sessionId;
  els.sessionId.textContent = state.sessionId || "未创建";
}

function setStatus(status) {
  els.sessionStatus.textContent = status || "待提问";
}

function resizeInput() {
  els.input.style.height = "auto";
  els.input.style.height = `${Math.min(180, Math.max(42, els.input.scrollHeight))}px`;
}

function domainLabel(value) {
  const map = {
    labor: "劳动争议",
    contract: "合同纠纷",
    marriage_family: "婚姻家事",
    tort: "侵权责任",
    private_lending: "民间借贷",
    housing_lease: "房屋租赁",
    consumer_rights: "消费维权",
    unknown: "未知",
  };
  return map[value] || value;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

resizeInput();

