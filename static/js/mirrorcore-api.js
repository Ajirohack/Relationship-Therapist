/**
 * MirrorCore API Client
 * Handles all API communication for the Relationship Therapist System
 */

class MirrorCoreAPI {
    constructor() {
        this.baseURL = window.location.origin;
        this.apiVersion = '/api/v1';
        this.endpoints = {
            // Analysis endpoints
            analyzeConversation: `${this.apiVersion}/analyze/conversation`,
            analyzeRealtime: `${this.apiVersion}/analyze/realtime`,
            analyzeUpload: `${this.apiVersion}/analyze/upload`,

            // Analytics
            analytics: '/api/analytics',
            userStats: `${this.apiVersion}/user/stats`,

            // Recommendations
            recommendations: '/api/recommendations',
            realtimeRecommendations: `${this.apiVersion}/recommendations/realtime`,

            // Reports
            reports: `${this.apiVersion}/reports`,
            generateReport: `${this.apiVersion}/reports/generate`,

            // User management
            userProfile: `${this.apiVersion}/user/profile`,
            userSessions: `${this.apiVersion}/user/sessions`,

            // Knowledge base
            knowledge: `${this.apiVersion}/knowledge`,
            knowledgeSearch: `${this.apiVersion}/knowledge-base/search`,

            // Feedback
            feedback: `${this.apiVersion}/feedback`,

            // Authentication
            login: `${this.apiVersion}/auth/login`,
            register: `${this.apiVersion}/auth/register`,
            refresh: `${this.apiVersion}/auth/refresh`,
            logout: `${this.apiVersion}/auth/logout`,

            // Health and status
            health: '/api/health',
            status: '/api/status'
        };

        this.token = localStorage.getItem('authToken');
        this.refreshToken = localStorage.getItem('refreshToken');

        // WebSocket connection for real-time features
        this.wsConnection = null;
        this.wsReconnectAttempts = 0;
        this.maxReconnectAttempts = 5;

        // Event listeners
        this.eventListeners = new Map();

        // Initialize
        this.init();
    }

    /**
     * Initialize the API client
     */
    async init() {
        // Check if user is authenticated
        if (this.token) {
            try {
                await this.verifyToken();
            } catch (error) {
                console.warn('Token verification failed:', error);
                this.clearAuth();
            }
        }

        // Setup automatic token refresh
        this.setupTokenRefresh();
    }

    /**
     * Make authenticated HTTP request
     */
    async request(endpoint, options = {}) {
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        // Add authorization header if token exists
        if (this.token) {
            config.headers.Authorization = `Bearer ${this.token}`;
        }

        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, config);

            // Handle different response types
            if (response.status === 401) {
                await this.handleUnauthorized();
                throw new Error('Unauthorized');
            }

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || error.message || 'Request failed');
            }

            // Handle different content types
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }

            return await response.text();
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }

    /**
     * Authentication Methods
     */
    async login(email, password) {
        try {
            const response = await this.request(this.endpoints.login, {
                method: 'POST',
                body: JSON.stringify({ email, password })
            });

            this.setTokens(response.access_token, response.refresh_token);
            this.emit('authChanged', { authenticated: true, user: response.user });

            return response;
        } catch (error) {
            this.emit('authError', error);
            throw error;
        }
    }

    async register(userData) {
        try {
            const response = await this.request(this.endpoints.register, {
                method: 'POST',
                body: JSON.stringify(userData)
            });

            this.setTokens(response.access_token, response.refresh_token);
            this.emit('authChanged', { authenticated: true, user: response.user });

            return response;
        } catch (error) {
            this.emit('authError', error);
            throw error;
        }
    }

    async logout() {
        try {
            if (this.token) {
                await this.request(this.endpoints.logout, { method: 'POST' });
            }
        } catch (error) {
            console.warn('Logout request failed:', error);
        } finally {
            this.clearAuth();
            this.emit('authChanged', { authenticated: false });
        }
    }

    /**
     * Conversation Analysis Methods
     */
    async analyzeConversation(conversationText, options = {}) {
        try {
            this.emit('analysisStarted', { text: conversationText });

            const response = await this.request(this.endpoints.analyzeConversation, {
                method: 'POST',
                body: JSON.stringify({
                    conversation_text: conversationText,
                    analysis_type: options.analysisType || 'comprehensive',
                    include_recommendations: options.includeRecommendations !== false,
                    real_time: options.realTime || false
                })
            });

            this.emit('analysisCompleted', response);
            return response;
        } catch (error) {
            this.emit('analysisError', error);
            throw error;
        }
    }

    async uploadAndAnalyze(file, options = {}) {
        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('analysis_type', options.analysisType || 'comprehensive');

            this.emit('uploadStarted', { filename: file.name });

            const response = await this.request(this.endpoints.analyzeUpload, {
                method: 'POST',
                body: formData,
                headers: {} // Remove Content-Type to let browser set it with boundary
            });

            this.emit('uploadCompleted', response);
            return response;
        } catch (error) {
            this.emit('uploadError', error);
            throw error;
        }
    }

    /**
     * Real-time Analysis with WebSocket
     */
    async startRealtimeAnalysis() {
        if (this.wsConnection) {
            return this.wsConnection;
        }

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsURL = `${protocol}//${window.location.host}/ws/realtime-analysis`;

        try {
            this.wsConnection = new WebSocket(wsURL);

            this.wsConnection.onopen = () => {
                console.log('WebSocket connected for real-time analysis');
                this.wsReconnectAttempts = 0;
                this.emit('realtimeConnected');
            };

            this.wsConnection.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.emit('realtimeUpdate', data);
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error);
                }
            };

            this.wsConnection.onclose = () => {
                console.log('WebSocket disconnected');
                this.wsConnection = null;
                this.emit('realtimeDisconnected');
                this.attemptReconnect();
            };

            this.wsConnection.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.emit('realtimeError', error);
            };

            return this.wsConnection;
        } catch (error) {
            console.error('Failed to establish WebSocket connection:', error);
            throw error;
        }
    }

    sendRealtimeMessage(message) {
        if (this.wsConnection && this.wsConnection.readyState === WebSocket.OPEN) {
            this.wsConnection.send(JSON.stringify(message));
        } else {
            console.warn('WebSocket not connected');
        }
    }

    /**
     * Reports and Recommendations
     */
    async getRecommendations(analysisId) {
        return await this.request(`${this.endpoints.recommendations}?analysis_id=${analysisId}`);
    }

    async generateReport(analysisId, reportType = 'comprehensive') {
        return await this.request(this.endpoints.generateReport, {
            method: 'POST',
            body: JSON.stringify({
                analysis_id: analysisId,
                report_type: reportType
            })
        });
    }

    async getUserReports(limit = 10, offset = 0) {
        return await this.request(`${this.endpoints.reports}?limit=${limit}&offset=${offset}`);
    }

    /**
     * Knowledge Base Methods
     */
    async searchKnowledge(query, category = null) {
        const params = new URLSearchParams({ query });
        if (category) params.append('category', category);

        return await this.request(`${this.endpoints.knowledgeSearch}?${params}`);
    }

    async getKnowledgeCategories() {
        return await this.request(`${this.endpoints.knowledge}/categories`);
    }

    /**
     * User Profile Methods
     */
    async getUserProfile() {
        return await this.request(this.endpoints.userProfile);
    }

    async updateUserProfile(profileData) {
        return await this.request(this.endpoints.userProfile, {
            method: 'PUT',
            body: JSON.stringify(profileData)
        });
    }

    async getUserSessions(limit = 20) {
        return await this.request(`${this.endpoints.userSessions}?limit=${limit}`);
    }

    /**
     * Health and Status
     */
    async checkHealth() {
        return await this.request(this.endpoints.health);
    }

    async getStatus() {
        return await this.request(this.endpoints.status);
    }

    /**
     * Utility Methods
     */
    setTokens(accessToken, refreshToken) {
        this.token = accessToken;
        this.refreshToken = refreshToken;
        localStorage.setItem('authToken', accessToken);
        localStorage.setItem('refreshToken', refreshToken);
    }

    clearAuth() {
        this.token = null;
        this.refreshToken = null;
        localStorage.removeItem('authToken');
        localStorage.removeItem('refreshToken');
    }

    async verifyToken() {
        if (!this.token) return false;

        try {
            await this.getUserProfile();
            return true;
        } catch (error) {
            return false;
        }
    }

    async handleUnauthorized() {
        if (this.refreshToken) {
            try {
                const response = await fetch(`${this.baseURL}${this.endpoints.refresh}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ refresh_token: this.refreshToken })
                });

                if (response.ok) {
                    const data = await response.json();
                    this.setTokens(data.access_token, data.refresh_token);
                    return;
                }
            } catch (error) {
                console.error('Token refresh failed:', error);
            }
        }

        this.clearAuth();
        this.emit('authChanged', { authenticated: false });
    }

    setupTokenRefresh() {
        // Refresh token 5 minutes before expiry
        setInterval(async () => {
            if (this.token && this.refreshToken) {
                try {
                    await this.handleUnauthorized();
                } catch (error) {
                    console.error('Automatic token refresh failed:', error);
                }
            }
        }, 25 * 60 * 1000); // 25 minutes
    }

    attemptReconnect() {
        if (this.wsReconnectAttempts < this.maxReconnectAttempts) {
            this.wsReconnectAttempts++;
            const delay = Math.pow(2, this.wsReconnectAttempts) * 1000; // Exponential backoff

            setTimeout(() => {
                console.log(`Attempting WebSocket reconnect (${this.wsReconnectAttempts}/${this.maxReconnectAttempts})`);
                this.startRealtimeAnalysis();
            }, delay);
        }
    }

    /**
     * Event System
     */
    on(event, callback) {
        if (!this.eventListeners.has(event)) {
            this.eventListeners.set(event, []);
        }
        this.eventListeners.get(event).push(callback);
    }

    off(event, callback) {
        if (this.eventListeners.has(event)) {
            const listeners = this.eventListeners.get(event);
            const index = listeners.indexOf(callback);
            if (index > -1) {
                listeners.splice(index, 1);
            }
        }
    }

    emit(event, data) {
        if (this.eventListeners.has(event)) {
            this.eventListeners.get(event).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Error in event listener for ${event}:`, error);
                }
            });
        }
    }

    isAuthenticated() {
        return !!this.token;
    }

    disconnect() {
        if (this.wsConnection) {
            this.wsConnection.close();
            this.wsConnection = null;
        }
    }
}

// Global API instance
window.mirrorCoreAPI = new MirrorCoreAPI();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MirrorCoreAPI;
}
