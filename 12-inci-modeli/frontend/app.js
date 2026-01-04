/**
 * 12. İnci Modeli - Frontend Application
 * modulLLM.com - Real-time Emotion AI
 */

class EmotionChatApp {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 2000;

        // DOM elements
        this.chatMessages = document.getElementById('chat-messages');
        this.userInput = document.getElementById('user-input');
        this.sendButton = document.getElementById('send-button');
        this.emotionDisplay = document.getElementById('emotion-display');
        this.statusText = document.getElementById('status-text');
        this.connectionStatus = document.getElementById('connection-status');

        this.init();
    }

    init() {
        // Event listeners
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Connect to WebSocket
        this.connect();
    }

    connect() {
        const wsUrl = this.getWebSocketUrl();
        this.updateStatus('Bağlanıyor...', 'disconnected');

        try {
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => this.onOpen();
            this.ws.onmessage = (event) => this.onMessage(event);
            this.ws.onerror = (error) => this.onError(error);
            this.ws.onclose = () => this.onClose();

        } catch (error) {
            console.error('WebSocket connection error:', error);
            this.updateStatus('Bağlantı hatası', 'disconnected');
            this.scheduleReconnect();
        }
    }

    getWebSocketUrl() {
        // Determine WebSocket URL based on current location
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.hostname;
        const port = '8000'; // API server port

        // For development
        if (host === 'localhost' || host === '127.0.0.1') {
            return `${protocol}//${host}:${port}/ws/emotion/realtime`;
        }

        // For production
        return `${protocol}//${host}/ws/emotion/realtime`;
    }

    onOpen() {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        this.updateStatus('Bağlı ✓', 'connected');
        this.sendButton.disabled = false;
    }

    onMessage(event) {
        try {
            const data = JSON.parse(event.data);
            console.log('Received:', data);

            switch (data.type) {
                case 'connected':
                    this.addSystemMessage(data.message);
                    break;

                case 'emotion_response':
                    this.handleEmotionResponse(data);
                    break;

                case 'error':
                    this.addSystemMessage(`Hata: ${data.message}`, 'error');
                    break;

                default:
                    console.warn('Unknown message type:', data.type);
            }
        } catch (error) {
            console.error('Error parsing message:', error);
        }
    }

    onError(error) {
        console.error('WebSocket error:', error);
        this.updateStatus('Bağlantı hatası', 'disconnected');
    }

    onClose() {
        console.log('WebSocket disconnected');
        this.updateStatus('Bağlantı kesildi', 'disconnected');
        this.sendButton.disabled = true;
        this.scheduleReconnect();
    }

    scheduleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = this.reconnectDelay * this.reconnectAttempts;

            console.log(`Reconnecting in ${delay}ms... (Attempt ${this.reconnectAttempts})`);
            this.updateStatus(`Yeniden bağlanılıyor (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`, 'disconnected');

            setTimeout(() => this.connect(), delay);
        } else {
            this.updateStatus('Bağlantı başarısız. Sayfayı yenileyin.', 'disconnected');
            this.addSystemMessage('❌ Bağlantı kurulamadı. Lütfen sayfayı yenileyin veya API sunucusunu kontrol edin.', 'error');
        }
    }

    updateStatus(text, status) {
        this.statusText.textContent = text;
        const statusDot = this.connectionStatus.querySelector('.status-dot');
        statusDot.className = `status-dot ${status}`;
    }

    sendMessage() {
        const text = this.userInput.value.trim();

        if (!text || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
            return;
        }

        // Add user message to chat
        this.addUserMessage(text);

        // Send to server
        const message = {
            type: 'message',
            text: text,
            timestamp: new Date().toISOString()
        };

        this.ws.send(JSON.stringify(message));

        // Clear input
        this.userInput.value = '';

        // Show typing indicator
        this.showTypingIndicator();
    }

    handleEmotionResponse(data) {
        // Remove typing indicator
        this.removeTypingIndicator();

        // Update emotion display
        this.updateEmotionDisplay(data.emotions);

        // Add AI response
        this.addAIMessage(data.ai_response, data.emotions);
    }

    addUserMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        messageDiv.textContent = text;
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    addAIMessage(text, emotions) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message ai-message';

        const textP = document.createElement('p');
        textP.textContent = text;
        messageDiv.appendChild(textP);

        // Add emotion indicator
        if (emotions && emotions.length > 0) {
            const emotionSpan = document.createElement('div');
            emotionSpan.className = 'message-emotion';
            emotionSpan.innerHTML = `${emotions[0].emoji} ${emotions[0].label}`;
            messageDiv.appendChild(emotionSpan);
        }

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    addSystemMessage(text, type = 'info') {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'system-message';
        messageDiv.textContent = text;

        if (type === 'error') {
            messageDiv.style.borderColor = 'var(--error-color)';
            messageDiv.style.background = 'rgba(239, 68, 68, 0.1)';
        }

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'message ai-message typing-indicator';
        indicator.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        indicator.id = 'typing-indicator';
        this.chatMessages.appendChild(indicator);
        this.scrollToBottom();
    }

    removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    updateEmotionDisplay(emotions) {
        if (!emotions || emotions.length === 0) {
            this.emotionDisplay.innerHTML = '<div class="emotion-placeholder">Duygu tespit edilemedi</div>';
            return;
        }

        this.emotionDisplay.innerHTML = '';

        emotions.forEach((emotion, index) => {
            const emotionDiv = document.createElement('div');
            emotionDiv.className = 'emotion-item';
            emotionDiv.style.animationDelay = `${index * 0.1}s`;

            emotionDiv.innerHTML = `
                <div class="emotion-header">
                    <div class="emotion-name">
                        <span>${emotion.emoji}</span>
                        <span>${emotion.label}</span>
                    </div>
                    <div class="emotion-confidence">${Math.round(emotion.confidence * 100)}%</div>
                </div>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: ${emotion.confidence * 100}%"></div>
                </div>
            `;

            this.emotionDisplay.appendChild(emotionDiv);
        });
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('12. İnci Modeli - modulLLM.com');
    console.log('Initializing Emotion Chat App...');

    const app = new EmotionChatApp();
    window.emotionChatApp = app; // For debugging

    console.log('App initialized successfully');
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        console.log('Page hidden');
    } else {
        console.log('Page visible');
        // Reconnect if needed
        if (window.emotionChatApp && (!window.emotionChatApp.ws || window.emotionChatApp.ws.readyState !== WebSocket.OPEN)) {
            console.log('Reconnecting...');
            window.emotionChatApp.connect();
        }
    }
});
