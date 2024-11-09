// This is static/script.js

const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const modelSpan = document.getElementById('current-model');
let currentModel = null;

function scrollToBottom() {
    // Add smooth scrolling behavior
    chatMessages.scrollTo({
        top: chatMessages.scrollHeight,
        behavior: 'smooth'
    });
}

// Check available models on page load
async function checkModels() {
    try {
        console.log("Checking models...");
        const response = await fetch('/api/models');
        const data = await response.json();
        console.log("Raw response data:", data);  // Log the entire response
        console.log("Models array:", data.models); // Log just the models array
        
        if (data.models && data.models.length > 0) {
            currentModel = data.models[0];
            console.log("Selected model:", currentModel);
            modelSpan.textContent = currentModel;
            enableChat();
            await updateInstanceStatus();
        } else {
            console.log("No models found. Data:", data);
            modelSpan.textContent = 'No model available';
            disableChat();
        }
    } catch (error) {
        console.error("Error checking models:", error);
        modelSpan.textContent = 'Error checking models';
        disableChat();
    }
}

function enableChat() {
    userInput.disabled = false;
    sendButton.disabled = false;
}

function disableChat() {
    userInput.disabled = true;
    sendButton.disabled = true;
}

userInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

function formatTimestamp(isoString) {
    return new Date(isoString).toLocaleTimeString();
}

function addMessage(content, isUser, timestamp, model) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;
    
    const messageContent = document.createElement('div');
    messageContent.textContent = content;
    messageDiv.appendChild(messageContent);

    if (timestamp) {
        const timestampDiv = document.createElement('div');
        timestampDiv.className = 'timestamp';
        timestampDiv.textContent = formatTimestamp(timestamp);
        messageDiv.appendChild(timestampDiv);
    }

    if (!isUser && model) {
        const modelDiv = document.createElement('div');
        modelDiv.className = 'model-tag';
        modelDiv.textContent = `Model: ${model}`;
        messageDiv.appendChild(modelDiv);
    }

    chatMessages.appendChild(messageDiv);
    scrollToBottom(); // Replace direct scrollTop assignment with smooth scroll
}

const sessionId = Math.random().toString(36).substring(7);

async function resetChat() {
    try {
        await fetch('/api/reset', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId
            })
        });
        
        // Clear the chat messages from the UI
        chatMessages.innerHTML = '';
        
        // Add a system message indicating the chat was reset
        addMessage("Conversation has been reset.", false, new Date().toISOString(), 'System');
        
    } catch (error) {
        console.error('Error resetting chat:', error);
        addMessage("Error resetting conversation.", false, new Date().toISOString(), 'System');
    }
}

async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    disableChat();
    addMessage(message, true, new Date().toISOString());
    userInput.value = '';

    try {
        const eventSource = new EventSource(`/api/chat?session_id=${sessionId}&message=${encodeURIComponent(message)}`);
        let currentMessageDiv = null;
        let currentMessageContent = '';

        eventSource.onmessage = function(event) {
            const data = JSON.parse(event.data);
            
            if (data.error) {
                addMessage(`Error: ${data.error}`, false, new Date().toISOString());
                eventSource.close();
                enableChat();
                return;
            }
        
            if (!currentMessageDiv) {
                currentMessageDiv = document.createElement('div');
                currentMessageDiv.className = 'message assistant-message';
                
                const contentDiv = document.createElement('div');
                contentDiv.className = 'message-content';
                currentMessageDiv.appendChild(contentDiv);
                
                chatMessages.appendChild(currentMessageDiv);
            }
        
            if (data.chunk) {
                currentMessageContent += data.chunk;
                const contentDiv = currentMessageDiv.querySelector('.message-content');
                contentDiv.innerHTML = marked.parse(currentMessageContent);
                scrollToBottom(); // Add scroll after chunk update
            }
        
            if (data.translation) {
                const contentDiv = currentMessageDiv.querySelector('.message-content');
                contentDiv.innerHTML = marked.parse(data.translation);
                scrollToBottom(); // Add scroll after translation
            }
        
            if (data.done) {
                const timestampDiv = document.createElement('div');
                timestampDiv.className = 'timestamp';
                timestampDiv.textContent = formatTimestamp(new Date().toISOString());
                currentMessageDiv.appendChild(timestampDiv);
                
                eventSource.close();
                enableChat();
                scrollToBottom(); // Add final scroll after message is complete
            }
        };

        eventSource.onerror = function(error) {
            console.error('EventSource error:', error);
            eventSource.close();
            enableChat();
        };

    } catch (error) {
        addMessage(`Error: ${error.message}`, false, new Date().toISOString());
        enableChat();
    }
}

async function updateInstanceStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        const statusDiv = document.createElement('div');
        statusDiv.className = 'instance-status';
        
        data.instances.forEach(instance => {
            const instanceDiv = document.createElement('div');
            instanceDiv.className = `status-item ${instance.status}`;
            instanceDiv.innerHTML = `
                <span class="instance-name">${instance.name}</span>
                <span class="status-indicator ${instance.status}"></span>
            `;
            statusDiv.appendChild(instanceDiv);
        });
        
        // Update or create status display
        const existingStatus = document.querySelector('.instance-status');
        if (existingStatus) {
            existingStatus.replaceWith(statusDiv);
        } else {
            document.querySelector('.model-info').appendChild(statusDiv);
        }
    } catch (error) {
        console.error('Error updating instance status:', error);
    }
}

async function getCurrentTheme() {
    try {
        const response = await fetch('/api/theme');
        const data = await response.json();
        return data.theme;
    } catch (error) {
        console.error('Error getting theme:', error);
        return 'dark'; // Default theme
    }
}

async function toggleTheme() {
    const currentTheme = await getCurrentTheme();
    const newTheme = currentTheme === 'dark' ? 'bright' : 'dark';
    
    try {
        const response = await fetch(`/api/theme/${newTheme}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            // Reload the page to apply new theme
            window.location.reload();
        } else {
            console.error('Failed to update theme');
        }
    } catch (error) {
        console.error('Error toggling theme:', error);
    }
}

// Optional: Add theme-specific button icon
function updateThemeButton() {
    const themeButton = document.querySelector('.theme-button');
    if (document.styleSheets[0].href.includes('bright_style.css')) {
        themeButton.innerHTML = '🌙'; // Moon for dark mode
    } else {
        themeButton.innerHTML = '☀️'; // Sun for light mode
    }
}

document.addEventListener('DOMContentLoaded', updateThemeButton);

// Initialize
checkModels();