const API_BASE = "/api";

const state = {
  threadId: null,
  threads: [],
  uploadedFiles: {}, // { threadId: [{ name, documents }] }
  isStreaming: false,
  isUploading: false,
  abortController: null,
};

// ── DOM Elements ───────────────────────────────────────────────────────────

const el = {
  sidebar: document.getElementById("sidebar"),
  sidebarBackdrop: document.getElementById("sidebarBackdrop"),
  menuToggleBtn: document.getElementById("menuToggleBtn"),
  newChatBtn: document.getElementById("newChatBtn"),
  threadList: document.getElementById("threadList"),
  healthStatus: document.getElementById("healthStatus"),
  activeThreadBadge: document.getElementById("activeThreadBadge"),
  pdfBadges: document.getElementById("pdfBadges"),
  toastBanner: document.getElementById("toastBanner"),
  messagesContainer: document.getElementById("messagesContainer"),
  emptyState: document.getElementById("emptyState"),
  messagesList: document.getElementById("messagesList"),
  chatForm: document.getElementById("chatForm"),
  messageInput: document.getElementById("messageInput"),
  sendBtn: document.getElementById("sendBtn"),
  stopBtn: document.getElementById("stopBtn"),
  uploadBtn: document.getElementById("uploadBtn"),
  pdfInput: document.getElementById("pdfInput"),
  dropZone: document.getElementById("dropZone"),
  dropOverlay: document.getElementById("dropOverlay"),
};

// ── Utilities ──────────────────────────────────────────────────────────────

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function renderMarkdown(rawText) {
  if (!rawText) return "";

  // Extract fenced code blocks first so inline formatting doesn't touch them
  const codeBlocks = [];
  let text = rawText.replace(/```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g, (_, lang, code) => {
    const idx = codeBlocks.length;
    const escapedCode = escapeHtml(code.replace(/\n$/, ""));
    codeBlocks.push(
      `<pre><button class="copy-code-btn" type="button">Copy</button><code class="lang-${escapeHtml(lang)}">${escapedCode}</code></pre>`
    );
    return `@@CODE_BLOCK_${idx}@@`;
  });

  text = escapeHtml(text);

  // Inline code
  text = text.replace(/`([^`\n]+)`/g, "<code>$1</code>");
  // Bold & italic
  text = text.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  text = text.replace(/\*([^*\n]+)\*/g, "<em>$1</em>");
  // Links
  text = text.replace(
    /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
    '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>'
  );

  // Line-by-line block formatting (headings, blockquotes, lists, paragraphs)
  const lines = text.split("\n");
  const html = [];
  let inUl = false;
  let inOl = false;

  const closeLists = () => {
    if (inUl) { html.push("</ul>"); inUl = false; }
    if (inOl) { html.push("</ol>"); inOl = false; }
  };

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) {
      closeLists();
      continue;
    }

    if (/^@@CODE_BLOCK_\d+@@$/.test(trimmed)) {
      closeLists();
      html.push(trimmed);
      continue;
    }

    const hMatch = trimmed.match(/^(#{1,3})\s+(.+)$/);
    if (hMatch) {
      closeLists();
      const lvl = hMatch[1].length;
      html.push(`<h${lvl}>${hMatch[2]}</h${lvl}>`);
      continue;
    }

    if (trimmed.startsWith("&gt; ")) {
      closeLists();
      html.push(`<blockquote>${trimmed.slice(5)}</blockquote>`);
      continue;
    }

    const ulMatch = trimmed.match(/^[-*]\s+(.+)$/);
    if (ulMatch) {
      if (inOl) { html.push("</ol>"); inOl = false; }
      if (!inUl) { html.push("<ul>"); inUl = true; }
      html.push(`<li>${ulMatch[1]}</li>`);
      continue;
    }

    const olMatch = trimmed.match(/^\d+\.\s+(.+)$/);
    if (olMatch) {
      if (inUl) { html.push("</ul>"); inUl = false; }
      if (!inOl) { html.push("<ol>"); inOl = true; }
      html.push(`<li>${olMatch[1]}</li>`);
      continue;
    }

    closeLists();
    html.push(`<p>${trimmed}</p>`);
  }
  closeLists();

  let output = html.join("\n");
  codeBlocks.forEach((block, idx) => {
    output = output.replace(`@@CODE_BLOCK_${idx}@@`, block);
  });

  return output;
}

let toastTimer = null;
function showToast(message, type = "info", durationMs = 4500) {
  el.toastBanner.textContent = message;
  el.toastBanner.className = `toast-banner ${type}`;
  el.toastBanner.hidden = false;
  if (toastTimer) clearTimeout(toastTimer);
  if (durationMs > 0) {
    toastTimer = setTimeout(() => {
      el.toastBanner.hidden = true;
    }, durationMs);
  }
}

function hideToast() {
  el.toastBanner.hidden = true;
}

function scrollToBottom() {
  el.messagesContainer.scrollTop = el.messagesContainer.scrollHeight;
}

function autoResizeTextarea() {
  el.messageInput.style.height = "auto";
  el.messageInput.style.height = `${Math.min(el.messageInput.scrollHeight, 180)}px`;
}

function setSidebarOpen(open) {
  el.sidebar.classList.toggle("open", open);
  el.sidebarBackdrop.classList.toggle("visible", open);
}

// ── UI Rendering ───────────────────────────────────────────────────────────

function updateHeaderMeta() {
  el.activeThreadBadge.textContent = state.threadId || "New Session";
  const files = state.threadId ? state.uploadedFiles[state.threadId] || [] : [];
  el.pdfBadges.innerHTML = "";
  for (const file of files) {
    const chip = document.createElement("span");
    chip.className = "pdf-chip";
    chip.textContent = `${file.name} (${file.documents} chunks)`;
    el.pdfBadges.appendChild(chip);
  }
}

function renderThreadList() {
  el.threadList.innerHTML = "";
  if (!state.threads.length) {
    const empty = document.createElement("div");
    empty.className = "thread-empty";
    empty.textContent = "No saved threads yet.";
    el.threadList.appendChild(empty);
    return;
  }

  // Show most recently listed threads first
  const ordered = [...state.threads].reverse();
  for (const tid of ordered) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = `thread-item${tid === state.threadId ? " active" : ""}`;
    btn.title = tid;
    btn.innerHTML = `<span class="thread-item-label">${escapeHtml(tid)}</span>`;
    btn.addEventListener("click", () => {
      selectThread(tid);
      setSidebarOpen(false);
    });
    el.threadList.appendChild(btn);
  }
}

function appendMessage(role, content, isError = false) {
  el.emptyState.hidden = true;

  const row = document.createElement("div");
  row.className = `message-row ${role}${isError ? " error" : ""}`;

  if (role === "assistant") {
    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = "AI";
    row.appendChild(avatar);
  }

  const bubble = document.createElement("div");
  bubble.className = role === "assistant" ? "message-bubble markdown-body" : "message-bubble";

  if (role === "user") {
    bubble.textContent = content;
  } else if (content) {
    bubble.innerHTML = renderMarkdown(content);
  } else {
    bubble.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
  }

  row.appendChild(bubble);
  el.messagesList.appendChild(row);
  scrollToBottom();
  return { row, bubble };
}

function setBusyState(streaming) {
  state.isStreaming = streaming;
  el.sendBtn.hidden = streaming;
  el.stopBtn.hidden = !streaming;
  el.uploadBtn.disabled = streaming || state.isUploading;
  el.messageInput.disabled = streaming;
  if (!streaming) {
    el.messageInput.focus();
  }
}

// ── API Calls ──────────────────────────────────────────────────────────────

async function checkHealth() {
  try {
    const res = await fetch("/health");
    if (!res.ok) throw new Error("Unhealthy");
    el.healthStatus.className = "health-pill online";
    el.healthStatus.querySelector(".health-text").textContent = "Backend online";
  } catch {
    el.healthStatus.className = "health-pill offline";
    el.healthStatus.querySelector(".health-text").textContent = "Backend offline";
  }
}

async function fetchThreads() {
  try {
    const res = await fetch(`${API_BASE}/threads`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    state.threads = Array.isArray(data.thread_ids) ? data.thread_ids : [];
    renderThreadList();
  } catch (err) {
    el.threadList.innerHTML = `<div class="thread-empty">Failed to load threads</div>`;
    console.error("Failed to fetch threads:", err);
  }
}

async function selectThread(threadId) {
  if (state.isStreaming) return;
  hideToast();
  state.threadId = threadId;
  updateHeaderMeta();
  renderThreadList();

  el.messagesList.innerHTML = "";
  el.emptyState.hidden = true;

  try {
    const res = await fetch(`${API_BASE}/threads/${encodeURIComponent(threadId)}/history`);
    if (res.status === 404) {
      el.emptyState.hidden = false;
      return;
    }
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }

    const data = await res.json();
    const msgs = (data.messages || []).filter(
      (m) => m.role === "user" || m.role === "assistant"
    );

    if (!msgs.length) {
      el.emptyState.hidden = false;
      return;
    }

    for (const msg of msgs) {
      if (msg.content) {
        appendMessage(msg.role, msg.content);
      }
    }
  } catch (err) {
    showToast(`Could not load thread history: ${err.message}`, "error");
    el.emptyState.hidden = false;
  }
}

function startNewChat() {
  if (state.isStreaming) return;
  hideToast();
  state.threadId = null;
  el.messagesList.innerHTML = "";
  el.emptyState.hidden = false;
  updateHeaderMeta();
  renderThreadList();
  el.messageInput.focus();
}

async function handlePdfUpload(file) {
  if (!file) return;
  if (!file.name.toLowerCase().endsWith(".pdf")) {
    showToast("Only PDF files are supported.", "error");
    return;
  }
  if (state.isStreaming || state.isUploading) return;

  state.isUploading = true;
  el.uploadBtn.disabled = true;
  showToast(`Uploading & indexing "${file.name}"...`, "info", 0);

  const formData = new FormData();
  formData.append("file", file);
  if (state.threadId) {
    formData.append("thread_id", state.threadId);
  }

  try {
    const res = await fetch(`${API_BASE}/upload`, {
      method: "POST",
      body: formData,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(data.detail || `Upload failed (HTTP ${res.status})`);
    }

    state.threadId = data.thread_id;
    if (!state.threads.includes(state.threadId)) {
      state.threads.push(state.threadId);
    }

    state.uploadedFiles[state.threadId] = state.uploadedFiles[state.threadId] || [];
    state.uploadedFiles[state.threadId].push({
      name: file.name,
      documents: data.documents,
    });

    updateHeaderMeta();
    renderThreadList();
    showToast(
      `Indexed "${file.name}" (${data.documents} chunks). Ask a question about it below.`,
      "success"
    );
  } catch (err) {
    showToast(err.message || "PDF upload failed.", "error");
  } finally {
    state.isUploading = false;
    el.uploadBtn.disabled = state.isStreaming;
    el.pdfInput.value = "";
  }
}

async function sendMessage(text) {
  const message = text.trim();
  if (!message || state.isStreaming) return;

  hideToast();
  appendMessage("user", message);
  el.messageInput.value = "";
  autoResizeTextarea();

  const { row: assistantRow, bubble: assistantBubble } = appendMessage("assistant", "");
  const abortController = new AbortController();
  state.abortController = abortController;
  setBusyState(true);

  let accumulated = "";

  try {
    const res = await fetch(`${API_BASE}/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        thread_id: state.threadId,
      }),
      signal: abortController.signal,
    });

    const returnedTid = res.headers.get("X-Thread-Id");
    if (returnedTid && !state.threadId) {
      state.threadId = returnedTid;
      updateHeaderMeta();
    }

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `Request failed (HTTP ${res.status})`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true }).replace(/\r\n/g, "\n");
      const frames = buffer.split("\n\n");
      buffer = frames.pop() || "";

      for (const frame of frames) {
        if (!frame.trim()) continue;
        let eventType = "message";
        const dataLines = [];

        for (const line of frame.split("\n")) {
          if (line.startsWith("event:")) {
            eventType = line.slice(6).trim();
          } else if (line.startsWith("data:")) {
            // Strip single optional leading space per SSE specification
            dataLines.push(line.startsWith("data: ") ? line.slice(6) : line.slice(5));
          }
        }

        const payload = dataLines.join("\n");
        if (eventType === "error") {
          throw new Error(payload || "Stream error occurred.");
        }
        if (payload === "[DONE]") {
          continue;
        }

        accumulated += payload;
        assistantBubble.innerHTML = renderMarkdown(accumulated);
        scrollToBottom();
      }
    }

    if (!accumulated) {
      assistantBubble.innerHTML = renderMarkdown("*(No response received)*");
    }

    await fetchThreads();
  } catch (err) {
    if (err.name === "AbortError") {
      if (!accumulated) {
        assistantBubble.innerHTML = renderMarkdown("*(Generation stopped)*");
      }
    } else {
      assistantRow.classList.add("error");
      assistantBubble.textContent = `Error: ${err.message}`;
    }
  } finally {
    state.abortController = null;
    setBusyState(false);
  }
}

// ── Event Listeners ────────────────────────────────────────────────────────

el.chatForm.addEventListener("submit", (e) => {
  e.preventDefault();
  sendMessage(el.messageInput.value);
});

el.messageInput.addEventListener("input", autoResizeTextarea);

el.messageInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage(el.messageInput.value);
  }
});

el.stopBtn.addEventListener("click", () => {
  if (state.abortController) {
    state.abortController.abort();
  }
});

el.newChatBtn.addEventListener("click", () => {
  startNewChat();
  setSidebarOpen(false);
});

el.uploadBtn.addEventListener("click", () => {
  el.pdfInput.click();
});

el.pdfInput.addEventListener("change", (e) => {
  const file = e.target.files?.[0];
  if (file) handlePdfUpload(file);
});

el.menuToggleBtn.addEventListener("click", () => {
  setSidebarOpen(!el.sidebar.classList.contains("open"));
});

el.sidebarBackdrop.addEventListener("click", () => {
  setSidebarOpen(false);
});

// Starter prompt chips
document.querySelectorAll(".starter-chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    const prompt = chip.getAttribute("data-prompt");
    if (prompt) sendMessage(prompt);
  });
});

// Copy code button delegation
el.messagesList.addEventListener("click", async (e) => {
  const btn = e.target.closest(".copy-code-btn");
  if (!btn) return;
  const codeEl = btn.parentElement?.querySelector("code");
  if (!codeEl) return;
  try {
    await navigator.clipboard.writeText(codeEl.textContent || "");
    btn.textContent = "Copied";
    setTimeout(() => { btn.textContent = "Copy"; }, 1500);
  } catch {
    btn.textContent = "Failed";
  }
});

// Drag & drop PDF upload
let dragDepth = 0;
el.dropZone.addEventListener("dragenter", (e) => {
  e.preventDefault();
  dragDepth++;
  el.dropOverlay.classList.add("visible");
});

el.dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
});

el.dropZone.addEventListener("dragleave", () => {
  dragDepth = Math.max(0, dragDepth - 1);
  if (dragDepth === 0) {
    el.dropOverlay.classList.remove("visible");
  }
});

el.dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dragDepth = 0;
  el.dropOverlay.classList.remove("visible");
  const file = e.dataTransfer?.files?.[0];
  if (file) handlePdfUpload(file);
});

// ── Boot ───────────────────────────────────────────────────────────────────

checkHealth();
fetchThreads();
updateHeaderMeta();

