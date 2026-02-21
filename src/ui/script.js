// Zero UI Logic
console.log("Zero UI loaded");

/**
 * Communicates with the Backend (PyObjC or Mock).
 * @param {string} type - The type of message (e.g., 'drag', 'save_keys').
 * @param {any} data - Payload to send.
 */
function sendMessage(type, data = {}) {
    // Construct payload
    // If data is simple string, wrap it? No, keeping protocol: { type, data }
    const payload = { type, data };

    if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.zero) {
        // iOS/macOS WKWebView Handler
        // We always JSON.stringify to avoid ObjC dict conversion issues
        window.webkit.messageHandlers.zero.postMessage(JSON.stringify(payload));
    } else {
        console.log(`[Mock Backend] ${type}:`, data);
        // Simulate responses for testing in browser
        if (type === 'save_keys') {
            setTimeout(() => receiveResponse("_keys saved (mock)_"), 500);
        } else if (type === 'chat') {
            setTimeout(() => receiveResponse(`Echo: ${data}`), 500);
        }
    }
}

/**
 * Sends a raw chat message (legacy support).
 * @param {string} text 
 */
function sendChat(text) {
    if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.zero) {
        // Backend expects raw string for chat, or JSON object?
        // Current backend: if JSON decode fails, treats as chat.
        // So we can send raw string.
        window.webkit.messageHandlers.zero.postMessage(text);
    } else {
        console.log(`[Mock Chat]`, text);
        setTimeout(() => receiveResponse("This is a mock response. Backend not connected."), 1000);
    }
}


/* --- Window Dragging --- */
document.addEventListener('mousedown', (e) => {
    // Defines what is "interactive" and should NOT trigger drag
    const interactiveTags = ['INPUT', 'TEXTAREA', 'BUTTON', 'A'];

    // Check if target is inside an interactive element
    let el = e.target;
    let isInteractive = false;

    while (el && el !== document.body) {
        if (interactiveTags.includes(el.tagName) ||
            el.classList.contains('message-content') || // Allow text selection
            el.classList.contains('icon-btn')) {
            isInteractive = true;
            break;
        }
        el = el.parentElement;
    }

    if (!isInteractive) {
        sendMessage('drag');
    }
});

/* --- Chat Interface --- */
const userInput = document.getElementById('user-input');
const chatContainer = document.getElementById('chat-container');
const contextAppName = document.getElementById('context-app-name');

// Display Context Info
window.updateContext = function (data) {
    if (!data) return;

    // data: { app: "Code", title: "project - VS Code" }
    let text = data.app;

    if (data.title && data.title !== data.app) {
        contextAppName.title = `${data.app}: ${data.title}`;
    } else {
        contextAppName.title = data.app;
    }

    contextAppName.textContent = text;
}

// User Input
userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        const text = userInput.value.trim();
        if (text) {
            addMessage('user', text);
            userInput.value = '';

            // Send to backend
            // For standard chat, we send raw text as per current protocol
            sendChat(text);
        }
    }
});

/* --- Response Handling --- */

// Append full response (legacy)
window.receiveResponse = function (text) {
    addMessage('system', text);
}

// Stream response chunk
window.streamResponse = function (chunk) {
    const lastMsg = chatContainer.lastElementChild;

    // Check if last message is from system
    if (lastMsg && lastMsg.classList.contains('system')) {
        const p = lastMsg.querySelector('.message-content');

        // Append to raw text storage
        let raw = p.getAttribute('data-raw') || "";
        raw += chunk;
        p.setAttribute('data-raw', raw);

        // Render Markdown
        // Optimization TODO: buffer updates or use a streaming markdown parser
        p.innerHTML = marked.parse(raw);

        // scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
    } else {
        // Start new message
        addMessage('system', chunk);
        // Ensure data-raw is set on the new message
        const newMsg = chatContainer.lastElementChild;
        const p = newMsg.querySelector('.message-content');
        if (p) p.setAttribute('data-raw', chunk);
    }
}

/**
 * Adds a message bubble to the chat.
 * @param {string} role - 'user' or 'system'
 * @param {string} text - Content (Markdown supported)
 */
function addMessage(role, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;

    // Icon
    const icon = document.createElement('span');
    icon.className = 'icon';
    icon.textContent = role === 'user' ? 'U' : '0';

    // Content Bubble
    const p = document.createElement('div');
    p.className = 'message-content';
    p.innerHTML = marked.parse(text);

    msgDiv.appendChild(icon);
    msgDiv.appendChild(p);

    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}


/* --- Settings UI --- */
const settingsBtn = document.getElementById('settings-btn');
// const settingsModal ... removed
// const cancelSettings ... removed
// const saveSettings ... removed

function openSettingsWindow() {
    window.open('settings.html', 'ZeroSettings', 'width=800,height=600');
}

if (settingsBtn) {
    settingsBtn.addEventListener('click', openSettingsWindow);
}


/* --- Vertical Sidebar Logic --- */
const newChatBtn = document.getElementById('new-chat-btn');
const navHistory = document.getElementById('nav-history');
// const navTools ... removed
const navSettings = document.getElementById('nav-settings');

if (newChatBtn) {
    newChatBtn.addEventListener('click', () => {
        chatContainer.innerHTML = '';
        sendMessage('new_chat');
        addMessage('system', 'Started a new thread.');
    });
}

if (navSettings) {
    navSettings.addEventListener('click', openSettingsWindow);
}

const historyMenu = document.getElementById('history-menu');
let historyHideTimer = null;

function showHistory() {
    if (historyMenu) {
        if (historyHideTimer) clearTimeout(historyHideTimer);
        historyMenu.classList.remove('hidden');
        sendMessage('get_history'); // Refresh list
    }
}

function hideHistory() {
    if (historyMenu) {
        historyHideTimer = setTimeout(() => {
            historyMenu.classList.add('hidden');
        }, 300); // Short delay to allow moving mouse to menu
    }
}

if (navHistory) {
    // Hover logic
    navHistory.addEventListener('mouseenter', showHistory);
    navHistory.addEventListener('mouseleave', hideHistory);
}

if (historyMenu) {
    // Keep open when hovering the menu itself
    historyMenu.addEventListener('mouseenter', () => {
        if (historyHideTimer) clearTimeout(historyHideTimer);
    });
    historyMenu.addEventListener('mouseleave', () => {
        historyMenu.classList.add('hidden');
    });
}




// --- History & Chat Loading ---

const historyList = document.getElementById('history-panel'); // Old placeholder
const historyMenuList = document.getElementById('history-menu-list'); // New Flyout List

window.updateHistoryList = function (conversations) {
    // Target the flyout list prefers
    const targetList = historyMenuList || historyList;
    if (!targetList) return;

    targetList.innerHTML = '';

    // Create Header if needed, or just list
    // const header = document.createElement('div');
    // header.className = 'history-group-header';
    // header.textContent = "Recent";
    // historyList.appendChild(header);

    conversations.forEach(conv => {
        const item = document.createElement('div');
        item.className = 'history-item';
        // Container for title and actions
        const titleSpan = document.createElement('span');
        titleSpan.className = 'history-title';
        titleSpan.textContent = conv.title || "New Chat";

        // Actions Container (Hidden by default, shown on hover)
        const actionsContainer = document.createElement('div');
        actionsContainer.className = 'history-inline-actions';

        // Edit Button
        const editBtn = document.createElement('span');
        editBtn.className = 'action-icon edit-icon';
        editBtn.innerHTML = '&#9998;'; // Pencil
        editBtn.title = 'Rename';
        editBtn.onclick = (e) => {
            e.stopPropagation();
            actionsContainer.classList.add('hidden-during-rename');
            startRename(conv.id, titleSpan, actionsContainer);
        };

        // Delete Button
        // Delete Button
        const deleteBtn = document.createElement('span');
        deleteBtn.className = 'action-icon delete-icon';
        const trashSvg = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>`;
        deleteBtn.innerHTML = trashSvg;
        deleteBtn.title = 'Delete';

        deleteBtn.onclick = (e) => {
            e.stopPropagation();
            if (deleteBtn.classList.contains('confirming')) {
                sendMessage('delete_chat', { id: conv.id });
                item.remove();
            } else {
                deleteBtn.classList.add('confirming');
                deleteBtn.textContent = '?';
                deleteBtn.style.color = '#ef4444';
                setTimeout(() => {
                    deleteBtn.classList.remove('confirming');
                    deleteBtn.innerHTML = trashSvg;
                    deleteBtn.style.removeProperty('color');
                }, 3000);
            }
        };

        actionsContainer.appendChild(editBtn);
        actionsContainer.appendChild(deleteBtn);

        item.appendChild(titleSpan);
        item.appendChild(actionsContainer);

        item.addEventListener('click', () => {
            sendMessage('load_conversation', { id: conv.id });
            if (historyMenu) historyMenu.classList.add('hidden');
        });
        targetList.appendChild(item);
    });
}

function startRename(id, titleSpan, actionsContainer) {
    if (actionsContainer) actionsContainer.style.display = 'none'; // Force hide
    const currentTitle = titleSpan.textContent;
    const input = document.createElement('input');
    input.type = 'text';
    input.value = currentTitle;
    input.className = 'rename-input';

    // Replace span with input
    titleSpan.replaceWith(input);
    input.focus();

    const save = () => {
        const newTitle = input.value.trim() || currentTitle;
        titleSpan.textContent = newTitle;
        input.replaceWith(titleSpan);
        if (actionsContainer) actionsContainer.style.display = ''; // Restore
        if (actionsContainer) actionsContainer.classList.remove('hidden-during-rename');

        if (newTitle !== currentTitle) {
            sendMessage('rename_chat', { id: id, title: newTitle });
        }
    };

    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') save();
        if (e.key === 'Escape') {
            titleSpan.textContent = currentTitle;
            input.replaceWith(titleSpan);
            if (actionsContainer) actionsContainer.style.display = '';
        }
    });

    input.addEventListener('blur', save);

    // Stop propagation on input click to prevent chat load
    input.onclick = (e) => e.stopPropagation();
}

window.loadChatMessages = function (messages) {
    chatContainer.innerHTML = '';
    messages.forEach(msg => {
        addMessage(msg.role, msg.content);
    });
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Initialize
// Give backend a moment to be ready if needed, or just call
setTimeout(() => sendMessage('get_history'), 500);


