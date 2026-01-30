// Placeholder for frontend logic
console.log("Zero UI loaded");

// Window Drag Logic
document.addEventListener('mousedown', (e) => {
    // Defines what is "interactive" and should NOT trigger drag
    // Inputs, Buttons, Links, Scrollbars (sometimes), etc.
    // If the target is strictly the body, app container, or specific layout divs, we drag.

    // Check if target is interactive
    const target = e.target;
    const interactiveTags = ['INPUT', 'TEXTAREA', 'BUTTON', 'A'];

    // Recursive check for interactivity (e.g. clicking icon inside button)
    let el = target;
    let isInteractive = false;
    while (el && el !== document.body) {
        if (interactiveTags.includes(el.tagName) ||
            el.classList.contains('message-content') ||  // Allow text selection
            el.classList.contains('icon-btn') ||
            el.classList.contains('settings-modal')) {
            isInteractive = true;
            break;
        }
        el = el.parentElement;
    }

    if (!isInteractive) {
        // Trigger Native Drag
        if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.zero) {
            window.webkit.messageHandlers.zero.postMessage({ type: 'drag' });
        }
    }
});

const userInput = document.getElementById('user-input');
const chatContainer = document.getElementById('chat-container');
const contextAppName = document.getElementById('context-app-name');

window.updateContext = function (data) {
    if (!data) return;

    // Show App Name on Top Left
    // Format: "App Name" (maybe tooltip has title?)
    // User wants "current running application name"

    let text = data.app;
    // We could add title to tooltip?
    if (data.title && data.title !== data.app) {
        contextAppName.title = `${data.app}: ${data.title}`;
    } else {
        contextAppName.title = data.app;
    }

    contextAppName.textContent = text;
}

userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        const text = userInput.value.trim();
        if (text) {
            addMessage('user', text);
            userInput.value = '';

            // Send to Backend
            if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.zero) {
                window.webkit.messageHandlers.zero.postMessage(text);

                // Add temporary loading indicator or just wait
                // For now, we wait for receiveResponse
            } else {
                console.log("Zero Backend not found (Browser mode?)");
                // Mock response for testing in browser
                setTimeout(() => receiveResponse("This is a mock response. Backend not connected."), 1000);
            }
        }
    }
});

// Called by Python backend
window.receiveResponse = function (text) {
    addMessage('system', text);
}

// Called by Python backend for streaming
window.streamResponse = function (chunk) {
    const lastMsg = chatContainer.lastElementChild;
    // Check if last message is from system
    if (lastMsg && lastMsg.classList.contains('system')) {
        const p = lastMsg.querySelector('.message-content');
        // Simple append for now
        // TODO: Smarter markdown rendering for partials? 
        // For now, we append text and re-render the whole block to keep markdown valid
        // But re-rendering markdown on every char is expensive/flickery.
        // Let's just append raw text for now? 
        // Or keep a data attribute with raw text?

        // Strategy: Append to raw text, then re-render.
        let raw = p.getAttribute('data-raw') || "";
        raw += chunk;
        p.setAttribute('data-raw', raw);
        p.innerHTML = marked.parse(raw);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    } else {
        // Start new message
        addMessage('system', chunk);
        // Ensure data-raw is set on the new message
        const newMsg = chatContainer.lastElementChild;
        const p = newMsg.querySelector('.message-content');
        p.setAttribute('data-raw', chunk);
    }
}

function addMessage(role, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;

    // Icon
    const icon = document.createElement('span');
    icon.className = 'icon';
    icon.textContent = role === 'user' ? 'U' : '0'; // Changed 'Z' to '0' for system icon

    // Text
    const p = document.createElement('div'); // Changed to div to contain markdown HTML
    p.className = 'message-content';
    p.innerHTML = marked.parse(text);

    msgDiv.appendChild(icon);
    msgDiv.appendChild(p);

    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

/* --- Settings Logic --- */
const settingsBtn = document.getElementById('settings-btn');
const settingsModal = document.getElementById('settings-modal');
const cancelSettings = document.getElementById('cancel-settings');
const saveSettings = document.getElementById('save-settings');

// Toggle Modal
settingsBtn.addEventListener('click', () => {
    settingsModal.classList.remove('hidden');
});

cancelSettings.addEventListener('click', () => {
    settingsModal.classList.add('hidden');
});

// Close on outside click
settingsModal.addEventListener('click', (e) => {
    if (e.target === settingsModal) {
        settingsModal.classList.add('hidden');
    }
});

// Save Keys
saveSettings.addEventListener('click', () => {
    const keys = {
        notion: document.getElementById('key-notion').value,
        trello: document.getElementById('key-trello').value,
        github: document.getElementById('key-github').value,
        // Only send if not empty to avoid clearing existing? 
        // For now, backend handles empty = delete, so we send what is there.
        // Ideally we should mask inputs and only send changed ones, 
        // but for high security we might just treat this as a write-only interface.
    };

    // Send to Backend
    if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.zero) {
        window.webkit.messageHandlers.zero.postMessage(JSON.stringify({
            type: 'save_keys',
            data: keys
        }));
        // Close
        settingsModal.classList.add('hidden');
        // Clear inputs for security
        document.getElementById('key-notion').value = "";
        document.getElementById('key-trello').value = "";
        document.getElementById('key-github').value = "";

        // Feedback
        addMessage('system', "_Keys saved securely to Keychain._");
    } else {
        console.log("Mock Save:", keys);
        settingsModal.classList.add('hidden');
        addMessage('system', "_[Mock] Keys saved securely._");
    }
});

