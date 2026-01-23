// Placeholder for frontend logic
console.log("Zero UI loaded");

const userInput = document.getElementById('user-input');
const chatContainer = document.getElementById('chat-container');
const contextBadge = document.getElementById('context-badge');
const contextText = document.getElementById('context-text');

window.updateContext = function (data) {
    if (!data) return;

    // Format: "App Name | Window Title"
    // If Title is same as App Name, just show App Name
    let text = data.app;
    if (data.title && data.title !== data.app) {
        // Truncate title if too long
        let displayTitle = data.title;
        if (displayTitle.length > 30) {
            displayTitle = displayTitle.substring(0, 30) + "...";
        }
        text = `${data.app} | ${displayTitle}`;
    }

    contextText.textContent = text;
    contextBadge.classList.remove('hidden');
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
