// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', event => {
    if (event.reason?.message?.includes('message channel closed')) {
        event.preventDefault();
    }
});

const BACKEND_URL = 'https://your-backend-app.onrender.com';
const API_URL = `${BACKEND_URL}/chat`;
    ? 'https://chharomentalhealthchatbot.onrender.com'
    : '/chat';
const SESSION_ID = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);

let isProcessing = false;

// DOM elements
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendButton = document.getElementById('sendButton');
const typingIndicator = document.getElementById('typingIndicator');
const crisisBanner = document.getElementById('crisisBanner');

//Test backend connection on load
async function testConnection() {
    try {
        console.log('🔍 Testing backend connection...');
        const response = await fetch(`${BACKEND_URL}/health`);
        const data = await response.json();
        console.log('✅ Backend connected:', data);
    } catch (error) {
        console.error('❌ Backend connection failed:', error);
        addMessage('⚠️ Cannot connect to backend. Please check if the backend URL is correct.', 'bot');
    }
}
// Send message to backend
async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message || isProcessing) return;

    addMessage(message, 'user');
    chatInput.value = '';

    isProcessing = true;
    sendButton.disabled = true;
    typingIndicator.classList.add('active');

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: SESSION_ID, query: message })
        });

        if (!response.ok) throw new Error(`Network response was not ok: ${response.status}`);

        const data = await response.json();

        // Show crisis banner if necessary
        if (data.crisis) {
            crisisBanner.classList.add('active');
        } else {
            crisisBanner.classList.remove('active');
        }

        // Display AI + document response
        setTimeout(() => {
            typingIndicator.classList.remove('active');
            addMessage(data.response, 'bot', data.crisis);
        }, 500);

    } catch (error) {
        console.error('Error:', error);
        typingIndicator.classList.remove('active');
        addMessage('Sorry, I encountered an error. Please try again later.', 'bot');
    } finally {
        isProcessing = false;
        sendButton.disabled = false;
        chatInput.focus();
    }
}

// Add message to chat window
function addMessage(text, sender, isCrisis = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    if (isCrisis) messageDiv.classList.add('crisis');

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = sender === 'user' ? '👤' : '🫂';

    const content = document.createElement('div');
    content.className = 'message-content';
    content.textContent = text;

    if (sender === 'user') {
        messageDiv.appendChild(content);
        messageDiv.appendChild(avatar);
    } else {
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
    }

    // Remove welcome message on first message
    const welcomeMsg = chatMessages.querySelector('.welcome-message');
    if (welcomeMsg) welcomeMsg.remove();

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
// Reset chat (new session)
function startNewChat() {
    chatMessages.innerHTML = `
        <div class="welcome-message">
            <h2>Welcome to CHHARO Support Chat</h2>
            <p>I'm here to listen and support you. Feel free to share what's on your mind.</p>
            <div class="quick-actions">
                <div class="quick-action" onclick="sendQuickMessage('I need someone to talk to')">💬 Need to talk</div>
                <div class="quick-action" onclick="sendQuickMessage('I feel anxious')">😰 Feeling anxious</div>
                <div class="quick-action" onclick="sendQuickMessage('Tell me about mental health resources')">📚 Resources</div>
            </div>
        </div>
    `;
    crisisBanner.classList.remove('active');
    chatInput.value = '';
    window.SESSION_ID = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    console.log('🆕 New chat started:', SESSION_ID);
}


// Handle Enter key press
chatInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});

// Quick action messages
function sendQuickMessage(message) {
    chatInput.value = message;
    sendMessage();
}

// Focus input on load
document.addEventListener('DOMContentLoaded', () => {
    chatInput.focus();
});

document.getElementById('newChatButton').addEventListener('click', startNewChat);

