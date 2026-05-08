const API_BASE_URL = "http://127.0.0.1:8000";

const CHAT_STORAGE_KEY = "rag_chat_sessions";

let selectedFile = null;
let uploadedFileName = "";
let currentDocumentId = "";
let isDocumentUploaded = false;
let isUploading = false;

let currentChatId = null;

function getEl(id) {
    return document.getElementById(id);
}

function escapeHtml(text) {
    return String(text || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function scrollChatToBottom() {
    const chat = getEl("answerResult");

    requestAnimationFrame(() => {
        chat.scrollTop = chat.scrollHeight;
    });
}

function autoResizeTextarea(textarea) {
    textarea.style.height = "auto";
    textarea.style.height = Math.min(textarea.scrollHeight, 130) + "px";
}

/* =========================================================
   CHAT STORAGE
========================================================= */

function getChats() {
    try {
        return JSON.parse(localStorage.getItem(CHAT_STORAGE_KEY) || "[]");
    } catch {
        return [];
    }
}

function saveChats(chats) {
    localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(chats));
}

function createNewChat(filename) {

    const chats = getChats();

    const chat = {
        id: Date.now(),
        filename: filename,
        document_id: "",
        messages: [],
        created_at: new Date().toISOString()
    };

    chats.unshift(chat);

    saveChats(chats);

    currentChatId = chat.id;

    renderRecentChats();

    return chat;
}

function updateCurrentChat() {

    const chats = getChats();

    const index = chats.findIndex(c => c.id === currentChatId);

    if (index === -1) return;

    chats[index].filename = uploadedFileName;
    chats[index].document_id = currentDocumentId;

    saveChats(chats);

    renderRecentChats();
}

function addMessageToChat(type, content) {

    const chats = getChats();

    const index = chats.findIndex(c => c.id === currentChatId);

    if (index === -1) return;

    chats[index].messages.push({
        type,
        content
    });

    saveChats(chats);
}

function renderRecentChats() {

    const list = getEl("recentSearchList");

    const chats = getChats();

    if (!chats.length) {

        list.innerHTML = `
            <div class="recent-empty">
                No recent chats yet.
            </div>
        `;

        return;
    }

    list.innerHTML = chats.map(chat => `
        <button class="recent-item" onclick="loadChat(${chat.id})">
            <span class="recent-icon">📄</span>
            <span>${escapeHtml(chat.filename)}</span>
        </button>
    `).join("");
}

function loadChat(chatId) {

    const chats = getChats();

    const chat = chats.find(c => c.id === chatId);

    if (!chat) return;

    currentChatId = chat.id;

    uploadedFileName = chat.filename;
    currentDocumentId = chat.document_id;

    isDocumentUploaded = true;

    const answerResult = getEl("answerResult");

    answerResult.innerHTML = "";

    chat.messages.forEach(msg => {
        addMessage(msg.type, msg.content, true, false);
    });

    updateAskControls();

    scrollChatToBottom();
}

function clearRecentChats() {

    localStorage.removeItem(CHAT_STORAGE_KEY);

    renderRecentChats();
}

/* =========================================================
   UI
========================================================= */

function renderWelcomeMessage() {

    const answerResult = getEl("answerResult");

    answerResult.innerHTML = `
        <div class="message bot">
            <div class="message-avatar">🤖</div>

            <div class="message-content welcome-message">
                <strong>Hello 👋</strong>

                <p>
                    Upload your document using the plus button in the search bar,
                    then ask questions related to that document.
                </p>
            </div>
        </div>
    `;
}

function setUploadStatus(message, type = "info") {

    const box = getEl("uploadStatus");

    box.textContent = message;

    box.className = "upload-status-box " + type;
}

function updateUploadStrip() {

    const uploadStrip = getEl("uploadStrip");

    const selectedFileText = getEl("selectedFileText");

    if (selectedFile || uploadedFileName) {

        uploadStrip.classList.add("show");

        selectedFileText.textContent =
            uploadedFileName || selectedFile.name;

    } else {

        uploadStrip.classList.remove("show");
    }
}

function updateAskControls() {

    const questionInput = getEl("questionInput");

    const sendButton = getEl("sendButton");

    const uploadButton = getEl("uploadButton");

    const askLockHint = getEl("askLockHint");

    const canAsk =
        isDocumentUploaded &&
        currentDocumentId &&
        !isUploading;

    questionInput.disabled = !canAsk;

    sendButton.disabled = !canAsk;

    uploadButton.disabled =
        !selectedFile || isUploading || isDocumentUploaded;

    if (canAsk) {

        questionInput.placeholder =
            "Ask a question about " + uploadedFileName + "...";

        askLockHint.innerHTML =
            `Document ready: ${uploadedFileName}. You can ask questions now.`;

        askLockHint.className = "ask-lock-hint ready";

    } else {

        questionInput.placeholder =
            "Upload a document first to ask questions...";

        askLockHint.innerHTML =
            "Upload a document to start asking questions.";

        askLockHint.className = "ask-lock-hint";
    }

    updateUploadStrip();
}

function validateFile(file) {

    const allowed = ["pdf", "txt", "md"];

    const ext = file.name.split(".").pop().toLowerCase();

    return allowed.includes(ext);
}

/* =========================================================
   FILE SELECT
========================================================= */

function handleFileSelection(event) {

    const file = event.target.files[0];

    if (!file) return;

    if (!validateFile(file)) {

        setUploadStatus(
            "❌ Only PDF, TXT and MD files are allowed.",
            "error"
        );

        return;
    }

    selectedFile = file;

    uploadedFileName = file.name;

    currentDocumentId = "";

    isDocumentUploaded = false;

    createNewChat(file.name);

    updateAskControls();

    setUploadStatus(
        "Selected file: " + file.name,
        "info"
    );
}

/* =========================================================
   UPLOAD
========================================================= */

async function uploadSelectedDocument() {

    if (!selectedFile) return;

    const formData = new FormData();

    formData.append("file", selectedFile);

    try {

        isUploading = true;

        updateAskControls();

        setUploadStatus(
            "Uploading and processing...",
            "uploading"
        );

        const response = await fetch(
            API_BASE_URL + "/upload-document",
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail || "Upload failed"
            );
        }

        currentDocumentId = data.document_id;

        uploadedFileName = data.filename;

        isUploading = false;

        isDocumentUploaded = true;

        updateCurrentChat();

        updateAskControls();

        setUploadStatus(
            "✅ Document uploaded successfully.",
            "success"
        );

        addMessage(
            "bot",
            "✅ Document uploaded successfully. You can now ask questions from this document."
        );

    } catch (error) {

        isUploading = false;

        setUploadStatus(
            "❌ " + error.message,
            "error"
        );
    }
}

/* =========================================================
   MESSAGE
========================================================= */

function addMessage(type, content, isHtml = false, save = true) {

    const answerResult = getEl("answerResult");

    const message = document.createElement("div");

    message.className = "message " + type;

    if (type === "bot") {

        message.innerHTML = `
            <div class="message-avatar">🤖</div>

            <div class="message-content">
                ${isHtml ? content : escapeHtml(content)}
            </div>
        `;

    } else {

        message.innerHTML = `
            <div class="message-content">
                ${escapeHtml(content)}
            </div>
        `;
    }

    answerResult.appendChild(message);

    scrollChatToBottom();

    if (save) {
        addMessageToChat(type, content);
    }
}

/* =========================================================
   ASK QUESTION
========================================================= */

async function askQuestion() {

    const questionInput = getEl("questionInput");

    const question = questionInput.value.trim();

    if (!question) return;

    addMessage("user", question);

    questionInput.value = "";

    autoResizeTextarea(questionInput);

    try {

        const response = await fetch(
            API_BASE_URL + "/ask",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    document_id: currentDocumentId,
                    question: question
                })
            }
        );

        const data = await response.json();

        addMessage(
            "bot",
            data.answer || "No answer found.",
            true
        );

    } catch (error) {

        addMessage(
            "bot",
            "Failed to connect backend."
        );
    }
}

/* =========================================================
   NEW CHAT
========================================================= */

function startNewChat() {

    selectedFile = null;

    uploadedFileName = "";

    currentDocumentId = "";

    isDocumentUploaded = false;

    currentChatId = null;

    getEl("documentInput").value = "";

    renderWelcomeMessage();

    updateAskControls();

    setUploadStatus(
        "Select a document to begin.",
        "info"
    );
}

/* =========================================================
   EVENTS
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    renderWelcomeMessage();

    renderRecentChats();

    updateAskControls();

    setUploadStatus(
        "Select a document to begin.",
        "info"
    );

    getEl("newChatButton")
        .addEventListener("click", startNewChat);

    getEl("clearRecentButton")
        .addEventListener("click", clearRecentChats);

    getEl("filePickerButton")
        .addEventListener("click", () => {
            getEl("documentInput").click();
        });

    getEl("documentInput")
        .addEventListener("change", handleFileSelection);

    getEl("uploadButton")
        .addEventListener("click", uploadSelectedDocument);

    getEl("sendButton")
        .addEventListener("click", askQuestion);

    getEl("questionInput")
        .addEventListener("input", function () {
            autoResizeTextarea(this);
        });

    getEl("questionInput")
        .addEventListener("keydown", function (e) {

            if (e.key === "Enter" && !e.shiftKey) {

                e.preventDefault();

                askQuestion();
            }
        });
});

window.loadChat = loadChat;