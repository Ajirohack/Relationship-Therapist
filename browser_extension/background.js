// Background service worker for Relationship Therapist Assistant

class BackgroundService {
  constructor() {
    this.apiBaseUrl = 'http://localhost:8000';
    this.authToken = null;
    this.userId = null;
    this.websocket = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  async initialize() {
    console.log('Relationship Therapist Assistant - Background service initialized');

    // Load stored authentication
    const stored = await chrome.storage.local.get(['authToken', 'userId']);
    this.authToken = stored.authToken;
    this.userId = stored.userId;

    // Set up message listeners
    this.setupMessageListeners();

    // Connect to WebSocket if authenticated
    if (this.authToken && this.userId) {
      this.connectWebSocket();
    }
  }

  setupMessageListeners() {
    // Listen for messages from content scripts and popup
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      this.handleMessage(message, sender, sendResponse);
      return true; // Keep message channel open for async response
    });
  }

  async handleMessage(message, sender, sendResponse) {
    try {
      switch (message.type) {
        case 'LOGIN':
          const loginResult = await this.login(message.credentials);
          sendResponse(loginResult);
          break;

        case 'LOGOUT':
          await this.logout();
          sendResponse({ success: true });
          break;

        case 'GET_RECOMMENDATION':
          const recommendation = await this.getRealtimeRecommendation(message.data);
          sendResponse(recommendation);
          break;

        case 'ANALYZE_CONVERSATION':
          const analysis = await this.analyzeConversation(message.data);
          sendResponse(analysis);
          break;

        case 'GET_AUTH_STATUS':
          sendResponse({
            authenticated: !!this.authToken,
            userId: this.userId
          });
          break;

        case 'UPLOAD_CONVERSATION':
          const uploadResult = await this.uploadConversation(message.data);
          sendResponse(uploadResult);
          break;

        default:
          sendResponse({ error: 'Unknown message type' });
      }
    } catch (error) {
      console.error('Background service error:', error);
      sendResponse({ error: error.message });
    }
  }

  async login(credentials) {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(credentials)
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const data = await response.json();
      this.authToken = data.access_token;
      this.userId = credentials.username; // Assuming username is used as userId

      // Store authentication
      await chrome.storage.local.set({
        authToken: this.authToken,
        userId: this.userId,
        refreshToken: data.refresh_token
      });

      // Connect to WebSocket
      this.connectWebSocket();

      return { success: true, userId: this.userId };
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: error.message };
    }
  }

  async logout() {
    try {
      if (this.authToken) {
        await fetch(`${this.apiBaseUrl}/api/v1/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.authToken}`,
            'Content-Type': 'application/json'
          }
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear stored data
      this.authToken = null;
      this.userId = null;
      await chrome.storage.local.clear();

      // Disconnect WebSocket
      if (this.websocket) {
        this.websocket.close();
        this.websocket = null;
      }
    }
  }

  async getRealtimeRecommendation(data) {
    if (!this.authToken) {
      throw new Error('Not authenticated');
    }

    try {
      const response = await fetch(`${this.apiBaseUrl}/api/v1/realtime/recommendation`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.authToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: this.userId,
          message: data.message,
          context: data.context || {},
          platform: data.platform || 'unknown'
        })
      });

      if (!response.ok) {
        throw new Error('Failed to get recommendation');
      }

      return await response.json();
    } catch (error) {
      console.error('Recommendation error:', error);
      throw error;
    }
  }

  async analyzeConversation(data) {
    if (!this.authToken) {
      throw new Error('Not authenticated');
    }

    try {
      const response = await fetch(`${this.apiBaseUrl}/api/v1/analyze/conversation`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.authToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: this.userId,
          conversation_data: data.conversation_data,
          platform: data.platform || 'unknown',
          metadata: data.metadata || {}
        })
      });

      if (!response.ok) {
        throw new Error('Failed to analyze conversation');
      }

      return await response.json();
    } catch (error) {
      console.error('Analysis error:', error);
      throw error;
    }
  }

  async uploadConversation(data) {
    if (!this.authToken) {
      throw new Error('Not authenticated');
    }

    try {
      const formData = new FormData();
      formData.append('file', data.file);

      const response = await fetch(`${this.apiBaseUrl}/api/v1/upload/conversation`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.authToken}`
        },
        body: formData
      });

      if (!response.ok) {
        throw new Error('Failed to upload conversation');
      }

      return await response.json();
    } catch (error) {
      console.error('Upload error:', error);
      throw error;
    }
  }

  connectWebSocket() {
    if (!this.authToken || !this.userId) return;

    try {
      const wsUrl = `ws://localhost:8000/ws/realtime/${this.userId}?token=${this.authToken}`;
      this.websocket = new WebSocket(wsUrl);

      this.websocket.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
      };

      this.websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        this.handleWebSocketMessage(data);
      };

      this.websocket.onclose = () => {
        console.log('WebSocket disconnected');
        this.scheduleReconnect();
      };

      this.websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    } catch (error) {
      console.error('WebSocket connection error:', error);
    }
  }

  handleWebSocketMessage(data) {
    // Broadcast WebSocket messages to content scripts
    chrome.tabs.query({ active: true }, (tabs) => {
      tabs.forEach(tab => {
        chrome.tabs.sendMessage(tab.id, {
          type: 'WEBSOCKET_MESSAGE',
          data: data
        }).catch(() => {
          // Ignore errors for tabs without content scripts
        });
      });
    });
  }

  scheduleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.pow(2, this.reconnectAttempts) * 1000; // Exponential backoff
      setTimeout(() => {
        this.connectWebSocket();
      }, delay);
    }
  }

  async refreshToken() {
    try {
      const stored = await chrome.storage.local.get(['refreshToken']);
      if (!stored.refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await fetch(`${this.apiBaseUrl}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          refresh_token: stored.refreshToken
        })
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const data = await response.json();
      this.authToken = data.access_token;

      await chrome.storage.local.set({
        authToken: this.authToken,
        refreshToken: data.refresh_token
      });

      return true;
    } catch (error) {
      console.error('Token refresh error:', error);
      await this.logout(); // Force logout on refresh failure
      return false;
    }
  }
}

// Initialize background service
const backgroundService = new BackgroundService();
backgroundService.initialize();

// Handle extension installation
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('Relationship Therapist Assistant installed');
    // Open welcome page or setup
    chrome.tabs.create({ url: 'popup.html' });
  }
});