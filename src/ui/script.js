// Placeholder for frontend logic
console.log("Zero UI loaded");

const userInput = document.getElementById('user-input');
const chatContainer = document.getElementById('chat-container');

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

function addMessage(role, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;

    // Icon
    const icon = document.createElement('span');
    icon.className = 'icon';
    icon.textContent = role === 'user' ? 'U' : 'Z';

    // Text
    const p = document.createElement('p');
    p.textContent = text;

    msgDiv.appendChild(icon);
    msgDiv.appendChild(p);

    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}
