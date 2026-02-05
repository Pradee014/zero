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
            el.classList.contains('icon-btn') ||
            el.classList.contains('settings-modal')) {
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
const settingsModal = document.getElementById('settings-modal');
const cancelSettings = document.getElementById('cancel-settings');
const saveSettings = document.getElementById('save-settings');

// Tab Switching
const tabs = document.querySelectorAll('.tab-item');
const panels = document.querySelectorAll('.tab-panel');

tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        // Deactivate all
        tabs.forEach(t => t.classList.remove('active'));
        panels.forEach(p => p.classList.remove('active'));

        // Activate clicked
        tab.classList.add('active');
        const targetId = `tab-${tab.getAttribute('data-tab')}`;
        const targetPanel = document.getElementById(targetId);
        if (targetPanel) targetPanel.classList.add('active');
    });
});

// Modal Actions
function openSettings() {
    settingsModal.classList.remove('hidden');
}

function closeSettings() {
    settingsModal.classList.add('hidden');
}

settingsBtn.addEventListener('click', openSettings);
cancelSettings.addEventListener('click', closeSettings);

// Global Shortcuts
document.addEventListener('keydown', (e) => {
    // Cmd + , to toggle settings
    if ((e.metaKey || e.ctrlKey) && e.key === ',') {
        e.preventDefault();
        if (settingsModal.classList.contains('hidden')) {
            openSettings();
        } else {
            closeSettings();
        }
    }
    // Escape to close
    if (e.key === 'Escape' && !settingsModal.classList.contains('hidden')) {
        closeSettings();
    }
});

// Close on backdrop click
settingsModal.addEventListener('click', (e) => {
    if (e.target === settingsModal) {
        closeSettings();
    }
});

// Save Functionality
saveSettings.addEventListener('click', () => {
    const keys = {
        notion: document.getElementById('key-notion').value,
        trello: document.getElementById('key-trello').value,
        github: document.getElementById('key-github').value,
    };

    sendMessage('save_keys', keys);

    // UI Feedback
    closeSettings();

    // Clear inputs for security (good practice, though UX trade-off)
    document.getElementById('key-notion').value = "";
    document.getElementById('key-trello').value = "";
    document.getElementById('key-github').value = "";

    // Show system message
    addMessage('system', "_Keys saved securely to Keychain._");
});
