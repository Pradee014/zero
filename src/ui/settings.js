console.log("Settings Window Loaded");

/**
 * Communicates with the Backend (PyObjC or Mock).
 * @param {string} type - The type of message (e.g., 'drag', 'save_keys').
 * @param {any} data - Payload to send.
 */
function sendMessage(type, data = {}) {
    const payload = { type, data };

    if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.zero) {
        window.webkit.messageHandlers.zero.postMessage(JSON.stringify(payload));
    } else {
        console.log(`[Mock Backend] ${type}:`, data);
        if (type === 'save_keys') {
            console.log("_keys saved (mock)_");
        }
    }
}

// Listen for messages from parent window or backend
window.updateCortex = function (data) {
    // data: { tasks: [], memories: [] }
    renderTasks(data.tasks || []);
    renderMemories(data.memories || []);
}

/* --- Settings UI Logic --- */
const closeSettingsBtn = document.getElementById('close-settings');
const saveSettingsBtn = document.getElementById('save-settings');

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
        const tabName = tab.getAttribute('data-tab');
        const targetId = `tab-${tabName}`;
        const targetPanel = document.getElementById(targetId);
        if (targetPanel) targetPanel.classList.add('active');

        // Auto-refresh Cortex when tab is opened
        if (tabName === 'cortex') {
            refreshCortex();
        }
    });
});

// Save Functionality
if (saveSettingsBtn) {
    saveSettingsBtn.addEventListener('click', () => {
        const keys = {
            notion: document.getElementById('key-notion').value,
            trello: document.getElementById('key-trello').value,
            github: document.getElementById('key-github').value,
        };

        sendMessage('save_keys', keys);

        // UI Feedback
        const originalText = saveSettingsBtn.textContent;
        saveSettingsBtn.textContent = "Saved!";
        setTimeout(() => {
            saveSettingsBtn.textContent = originalText;
        }, 2000);

        // Clear inputs for security
        // document.getElementById('key-notion').value = "";
        // document.getElementById('key-trello').value = "";
        // document.getElementById('key-github').value = "";
    });
}

// Close Button
if (closeSettingsBtn) {
    closeSettingsBtn.addEventListener('click', () => {
        window.close();
    });
}


/* --- Cortex Logic --- */
const cortexTasksList = document.getElementById('cortex-tasks-list');
const cortexMemoriesList = document.getElementById('cortex-memories-list');
const refreshCortexBtn = document.getElementById('refresh-cortex-btn');

if (refreshCortexBtn) {
    refreshCortexBtn.addEventListener('click', refreshCortex);
}

function refreshCortex() {
    // Show loading state
    if (cortexTasksList) cortexTasksList.innerHTML = '<div class="cortex-empty">Loading tasks...</div>';
    if (cortexMemoriesList) cortexMemoriesList.innerHTML = '<div class="cortex-empty">Loading memories...</div>';

    // Request Data
    sendMessage('get_cortex_data');
}

function renderTasks(tasks) {
    if (!cortexTasksList) return;
    cortexTasksList.innerHTML = '';
    if (tasks.length === 0) {
        cortexTasksList.innerHTML = '<div class="cortex-empty">No active tasks found in connected tools.</div>';
        return;
    }

    tasks.forEach(task => {
        // task: { id, title, source, status }
        const card = document.createElement('div');
        card.className = 'cortex-card';
        // Click to copy to clipboard or something since we can't easily paste to parent chat input without messaging
        card.onclick = () => {
            // Maybe copy to clipboard?
            // navigator.clipboard.writeText(`Checking ${task.source} task: ${task.title}`);
        };

        const source = document.createElement('div');
        source.className = 'card-source';
        // Icons based on source
        let icon = '📝';
        if (task.source === 'github') icon = '🐱';
        if (task.source === 'trello') icon = '📋';
        if (task.source === 'notion') icon = 'N';

        source.innerHTML = `${icon} ${task.source.toUpperCase()}`;

        const title = document.createElement('div');
        title.className = 'card-title';
        title.textContent = task.title;

        card.appendChild(source);
        card.appendChild(title);
        cortexTasksList.appendChild(card);
    });
}

function renderMemories(memories) {
    if (!cortexMemoriesList) return;
    cortexMemoriesList.innerHTML = '';
    if (memories.length === 0) {
        cortexMemoriesList.innerHTML = '<div class="cortex-empty">No memories yet.</div>';
        return;
    }

    memories.forEach(mem => {
        const text = typeof mem === 'string' ? mem : mem.text;

        const item = document.createElement('div');
        item.className = 'memory-item';
        item.textContent = text;

        cortexMemoriesList.appendChild(item);
    });
}
