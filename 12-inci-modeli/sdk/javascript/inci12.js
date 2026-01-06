/**
 * 12. İnci Modeli - JavaScript/TypeScript SDK
 * Official JavaScript client for 12. İnci Emotion AI API
 *
 * Installation:
 *   npm install inci12-sdk
 *
 * Usage (Node.js):
 *   const { InciClient } = require('inci12-sdk');
 *   const client = new InciClient({ apiKey: 'your_key' });
 *   const result = await client.analyzeEmotion('Bugün çok mutluyum!');
 *
 * Usage (Browser):
 *   <script src="inci12.js"></script>
 *   const client = new InciClient();
 *   const result = await client.analyzeEmotion('Merhaba!');
 */

(function (global, factory) {
    typeof exports === 'object' && typeof module !== 'undefined'
        ? factory(exports)
        : typeof define === 'function' && define.amd
            ? define(['exports'], factory)
            : factory((global.Inci12 = {}));
})(this, function (exports) {
    'use strict';

    const VERSION = '1.0.0';
    const DEFAULT_BASE_URL = 'http://localhost:8000';

    // ============================================
    // Data Models
    // ============================================

    class Emotion {
        constructor(data) {
            this.type = data.type;
            this.confidence = data.confidence;
            this.label = data.label;
            this.emoji = data.emoji;
        }
    }

    class EmotionAnalysisResult {
        constructor(data) {
            this.emotions = (data.emotions || []).map(e => new Emotion(e));
            this.primaryEmotion = data.primary_emotion;
            this.responseSuggestion = data.response_suggestion;
            this.timestamp = data.timestamp;
        }

        get topEmotion() {
            return this.emotions.length > 0 ? this.emotions[0] : null;
        }
    }

    // ============================================
    // HTTP Client
    // ============================================

    class InciClient {
        /**
         * Create a new InciClient
         * @param {Object} options - Configuration options
         * @param {string} options.apiKey - Optional API key for authentication
         * @param {string} options.baseUrl - Base API URL
         */
        constructor(options = {}) {
            this.apiKey = options.apiKey;
            this.baseUrl = (options.baseUrl || DEFAULT_BASE_URL).replace(/\/$/, '');
            this.headers = {
                'Content-Type': 'application/json'
            };

            if (this.apiKey) {
                this.headers['Authorization'] = `Bearer ${this.apiKey}`;
            }
        }

        /**
         * Make HTTP request
         * @private
         */
        async _request(method, endpoint, body = null) {
            const url = `${this.baseUrl}${endpoint}`;
            const options = {
                method,
                headers: this.headers
            };

            if (body) {
                options.body = JSON.stringify(body);
            }

            try {
                const response = await fetch(url, options);

                if (!response.ok) {
                    const error = await response.json().catch(() => ({}));
                    throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
                }

                return await response.json();
            } catch (error) {
                throw new Error(`API request failed: ${error.message}`);
            }
        }

        /**
         * Analyze emotion in text
         * @param {string} text - Text to analyze
         * @param {Object} options - Analysis options
         * @param {string} options.language - Language code (tr or en)
         * @param {string} options.context - Optional context
         * @returns {Promise<EmotionAnalysisResult>}
         */
        async analyzeEmotion(text, options = {}) {
            const payload = {
                text,
                language: options.language || 'tr'
            };

            if (options.context) {
                payload.context = options.context;
            }

            const data = await this._request('POST', '/api/v1/emotion/analyze', payload);
            return new EmotionAnalysisResult(data);
        }

        /**
         * Get list of 12 emotion categories
         * @returns {Promise<Array>}
         */
        async getEmotionsList() {
            const data = await this._request('GET', '/api/v1/emotions/list');
            return data.emotions || [];
        }

        /**
         * Send chat message
         * @param {string} message - Chat message
         * @param {Object} emotionContext - Optional emotion context
         * @returns {Promise<Object>}
         */
        async chat(message, emotionContext = null) {
            const payload = { text: message };
            if (emotionContext) {
                payload.emotion_context = emotionContext;
            }

            return await this._request('POST', '/api/v1/chat', payload);
        }

        /**
         * Check API health
         * @returns {Promise<boolean>}
         */
        async healthCheck() {
            try {
                const data = await this._request('GET', '/health');
                return data.status === 'healthy';
            } catch {
                return false;
            }
        }
    }

    // ============================================
    // WebSocket Client
    // ============================================

    class InciWebSocketClient {
        /**
         * Create WebSocket client
         * @param {string} wsUrl - WebSocket URL
         */
        constructor(wsUrl = 'ws://localhost:8000/ws/emotion/realtime') {
            this.wsUrl = wsUrl;
            this.ws = null;
            this.messageHandlers = [];
            this.errorHandlers = [];
        }

        /**
         * Connect to WebSocket
         * @returns {Promise<void>}
         */
        connect() {
            return new Promise((resolve, reject) => {
                this.ws = new WebSocket(this.wsUrl);

                this.ws.onopen = () => {
                    console.log('✅ WebSocket connected');
                    resolve();
                };

                this.ws.onerror = (error) => {
                    console.error('❌ WebSocket error:', error);
                    this.errorHandlers.forEach(handler => handler(error));
                    reject(error);
                };

                this.ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        this.messageHandlers.forEach(handler => handler(data));
                    } catch (error) {
                        console.error('Error parsing message:', error);
                    }
                };

                this.ws.onclose = () => {
                    console.log('WebSocket closed');
                };
            });
        }

        /**
         * Send message
         * @param {string} text - Message text
         */
        send(text) {
            if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
                throw new Error('WebSocket not connected');
            }

            const message = {
                type: 'message',
                text
            };

            this.ws.send(JSON.stringify(message));
        }

        /**
         * Register message handler
         * @param {Function} handler - Message handler function
         */
        onMessage(handler) {
            this.messageHandlers.push(handler);
        }

        /**
         * Register error handler
         * @param {Function} handler - Error handler function
         */
        onError(handler) {
            this.errorHandlers.push(handler);
        }

        /**
         * Close connection
         */
        close() {
            if (this.ws) {
                this.ws.close();
            }
        }
    }

    // ============================================
    // Convenience Functions
    // ============================================

    /**
     * Quick emotion analysis
     * @param {string} text - Text to analyze
     * @param {string} apiKey - Optional API key
     * @returns {Promise<EmotionAnalysisResult>}
     */
    async function quickAnalyze(text, apiKey = null) {
        const client = new InciClient({ apiKey });
        return await client.analyzeEmotion(text);
    }

    // ============================================
    // Exports
    // ============================================

    exports.VERSION = VERSION;
    exports.InciClient = InciClient;
    exports.InciWebSocketClient = InciWebSocketClient;
    exports.Emotion = Emotion;
    exports.EmotionAnalysisResult = EmotionAnalysisResult;
    exports.quickAnalyze = quickAnalyze;

    // For browser global
    if (typeof window !== 'undefined') {
        window.InciClient = InciClient;
        window.InciWebSocketClient = InciWebSocketClient;
        window.quickAnalyze = quickAnalyze;
    }
});
