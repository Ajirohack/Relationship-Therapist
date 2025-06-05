// Content script for Relationship Therapist Assistant

class RelationshipAssistant {
  constructor() {
    this.platform = this.detectPlatform();
    this.isActive = false;
    this.currentConversation = [];
    this.assistantPanel = null;
    this.messageObserver = null;
    this.typingIndicator = null;
    this.lastAnalyzedMessage = null;

    this.init();
  }

  detectPlatform() {
    const hostname = window.location.hostname;

    if (hostname.includes('whatsapp.com')) return 'whatsapp';
    if (hostname.includes('messenger.com')) return 'messenger';
    if (hostname.includes('discord.com')) return 'discord';
    if (hostname.includes('telegram.org')) return 'telegram';
    if (hostname.includes('instagram.com')) return 'instagram';
    if (hostname.includes('twitter.com') || hostname.includes('x.com')) return 'twitter';

    return 'unknown';
  }

  async init() {
    console.log(`Relationship Therapist Assistant - Initializing for ${this.platform}`);

    // Check authentication status
    const authStatus = await this.sendMessage({ type: 'GET_AUTH_STATUS' });
    if (!authStatus.authenticated) {
      console.log('User not authenticated');
      return;
    }

    this.isActive = true;

    // Wait for page to load completely
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.setup());
    } else {
      this.setup();
    }
  }

  setup() {
    this.createAssistantPanel();
    this.setupMessageObserver();
    this.setupKeyboardShortcuts();
    this.setupWebSocketListener();

    console.log('Relationship Therapist Assistant - Setup complete');
  }

  createAssistantPanel() {
    // Create floating assistant panel
    this.assistantPanel = document.createElement('div');
    this.assistantPanel.id = 'relationship-assistant-panel';
    this.assistantPanel.className = 'rta-panel rta-hidden';

    this.assistantPanel.innerHTML = `
      <div class="rta-header">
        <h3>💝 Relationship Assistant</h3>
        <div class="rta-controls">
          <button id="rta-minimize" class="rta-btn rta-btn-sm">−</button>
          <button id="rta-close" class="rta-btn rta-btn-sm">×</button>
        </div>
      </div>
      <div class="rta-content">
        <div class="rta-tabs">
          <button class="rta-tab rta-tab-active" data-tab="suggestions">Suggestions</button>
          <button class="rta-tab" data-tab="analysis">Analysis</button>
          <button class="rta-tab" data-tab="insights">Insights</button>
        </div>
        
        <div class="rta-tab-content rta-tab-active" id="rta-suggestions">
          <div class="rta-suggestion-box">
            <p class="rta-placeholder">Type a message to get real-time suggestions...</p>
          </div>
          <div class="rta-actions">
            <button id="rta-get-suggestion" class="rta-btn rta-btn-primary">Get Suggestion</button>
            <button id="rta-analyze-conversation" class="rta-btn rta-btn-secondary">Analyze Chat</button>
          </div>
        </div>
        
        <div class="rta-tab-content" id="rta-analysis">
          <div class="rta-analysis-box">
            <p class="rta-placeholder">No analysis available yet.</p>
          </div>
        </div>
        
        <div class="rta-tab-content" id="rta-insights">
          <div class="rta-insights-box">
            <p class="rta-placeholder">Conversation insights will appear here.</p>
          </div>
        </div>
      </div>
      <div class="rta-footer">
        <div class="rta-status">Ready</div>
        <button id="rta-toggle-auto" class="rta-btn rta-btn-sm">Auto: OFF</button>
      </div>
    `;

    document.body.appendChild(this.assistantPanel);

    // Setup panel event listeners
    this.setupPanelEvents();

    // Create toggle button
    this.createToggleButton();
  }

  createToggleButton() {
    const toggleBtn = document.createElement('button');
    toggleBtn.id = 'rta-toggle-btn';
    toggleBtn.className = 'rta-toggle-btn';
    toggleBtn.innerHTML = '💝';
    toggleBtn.title = 'Toggle Relationship Assistant';

    toggleBtn.addEventListener('click', () => {
      this.togglePanel();
    });

    document.body.appendChild(toggleBtn);
  }

  setupPanelEvents() {
    // Tab switching
    this.assistantPanel.querySelectorAll('.rta-tab').forEach(tab => {
      tab.addEventListener('click', (e) => {
        const tabName = e.target.dataset.tab;
        this.switchTab(tabName);
      });
    });

    // Panel controls
    document.getElementById('rta-close').addEventListener('click', () => {
      this.hidePanel();
    });

    document.getElementById('rta-minimize').addEventListener('click', () => {
      this.minimizePanel();
    });

    // Action buttons
    document.getElementById('rta-get-suggestion').addEventListener('click', () => {
      this.getSuggestion();
    });

    document.getElementById('rta-analyze-conversation').addEventListener('click', () => {
      this.analyzeConversation();
    });

    document.getElementById('rta-toggle-auto').addEventListener('click', () => {
      this.toggleAutoMode();
    });

    // Make panel draggable
    this.makeDraggable();
  }

  setupMessageObserver() {
    const selectors = this.getMessageSelectors();
    if (!selectors.container) return;

    const container = document.querySelector(selectors.container);
    if (!container) return;

    this.messageObserver = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === 'childList') {
          mutation.addedNodes.forEach((node) => {
            if (node.nodeType === Node.ELEMENT_NODE) {
              this.handleNewMessage(node);
            }
          });
        }
      });
    });

    this.messageObserver.observe(container, {
      childList: true,
      subtree: true
    });
  }

  getMessageSelectors() {
    const selectors = {
      whatsapp: {
        container: '[data-testid="conversation-panel-messages"]',
        message: '[data-testid="msg-container"]',
        text: '.selectable-text',
        input: '[data-testid="msg-input"]'
      },
      messenger: {
        container: '[role="main"]',
        message: '[data-testid="message_bubble"]',
        text: '[data-testid="message_bubble"] span',
        input: '[contenteditable="true"][role="textbox"]'
      },
      discord: {
        container: '[data-list-id="chat-messages"]',
        message: '[id^="chat-messages-"]',
        text: '[id^="message-content-"]',
        input: '[role="textbox"][data-slate-editor="true"]'
      },
      telegram: {
        container: '.messages-container',
        message: '.message',
        text: '.message-content',
        input: '.input-message-input'
      },
      instagram: {
        container: '[role="main"]',
        message: '[role="row"]',
        text: '[role="row"] span',
        input: '[contenteditable="true"][role="textbox"]'
      },
      twitter: {
        container: '[data-testid="primaryColumn"]',
        message: '[data-testid="tweet"]',
        text: '[data-testid="tweetText"]',
        input: '[data-testid="tweetTextarea_0"]'
      }
    };

    return selectors[this.platform] || {};
  }

  handleNewMessage(messageElement) {
    const selectors = this.getMessageSelectors();
    const textElement = messageElement.querySelector(selectors.text);

    if (textElement) {
      const messageText = textElement.textContent.trim();
      if (messageText && messageText !== this.lastAnalyzedMessage) {
        this.lastAnalyzedMessage = messageText;
        this.currentConversation.push({
          text: messageText,
          timestamp: Date.now(),
          sender: this.detectMessageSender(messageElement)
        });

        // Auto-suggest if enabled
        if (this.isAutoModeEnabled()) {
          this.getSuggestion(messageText);
        }
      }
    }
  }

  detectMessageSender(messageElement) {
    // Platform-specific logic to detect if message is from user or other party
    // This is a simplified version - real implementation would be more robust
    const userIndicators = {
      whatsapp: '.message-out',
      messenger: '[data-testid="outgoing_message"]',
      discord: '.message-author-you',
      telegram: '.message.own',
      instagram: '.outgoing',
      twitter: '[data-testid="tweet"][data-testid*="user"]'
    };

    const indicator = userIndicators[this.platform];
    if (indicator && messageElement.closest(indicator)) {
      return 'user';
    }
    return 'other';
  }

  async getSuggestion(messageText = null) {
    this.updateStatus('Getting suggestion...');

    try {
      const inputText = messageText || this.getCurrentInputText();
      if (!inputText) {
        this.showError('No message to analyze');
        return;
      }

      const response = await this.sendMessage({
        type: 'GET_RECOMMENDATION',
        data: {
          message: inputText,
          context: {
            conversation: this.currentConversation.slice(-10), // Last 10 messages
            platform: this.platform
          },
          platform: this.platform
        }
      });

      if (response.error) {
        this.showError(response.error);
        return;
      }

      this.displaySuggestion(response.recommendation);
      this.updateStatus('Ready');

    } catch (error) {
      console.error('Error getting suggestion:', error);
      this.showError('Failed to get suggestion');
    }
  }

  async analyzeConversation() {
    this.updateStatus('Analyzing conversation...');

    try {
      const response = await this.sendMessage({
        type: 'ANALYZE_CONVERSATION',
        data: {
          conversation_data: this.currentConversation,
          platform: this.platform,
          metadata: {
            url: window.location.href,
            timestamp: Date.now()
          }
        }
      });

      if (response.error) {
        this.showError(response.error);
        return;
      }

      this.displayAnalysis(response.analysis);
      this.updateStatus('Ready');

    } catch (error) {
      console.error('Error analyzing conversation:', error);
      this.showError('Failed to analyze conversation');
    }
  }

  getCurrentInputText() {
    const selectors = this.getMessageSelectors();
    const inputElement = document.querySelector(selectors.input);

    if (inputElement) {
      return inputElement.textContent || inputElement.value || '';
    }

    return '';
  }

  displaySuggestion(suggestion) {
    const suggestionBox = document.querySelector('.rta-suggestion-box');

    suggestionBox.innerHTML = `
      <div class="rta-suggestion">
        <h4>💡 Suggestion</h4>
        <p>${suggestion.text || suggestion.message || 'No specific suggestion available'}</p>
        ${suggestion.confidence ? `<div class="rta-confidence">Confidence: ${Math.round(suggestion.confidence * 100)}%</div>` : ''}
        ${suggestion.reasoning ? `<div class="rta-reasoning"><strong>Why:</strong> ${suggestion.reasoning}</div>` : ''}
        <div class="rta-suggestion-actions">
          <button class="rta-btn rta-btn-sm" onclick="navigator.clipboard.writeText('${suggestion.text || suggestion.message}')">Copy</button>
          <button class="rta-btn rta-btn-sm" onclick="this.closest('.rta-suggestion').remove()">Dismiss</button>
        </div>
      </div>
    `;

    this.switchTab('suggestions');
    this.showPanel();
  }

  displayAnalysis(analysis) {
    const analysisBox = document.querySelector('.rta-analysis-box');

    analysisBox.innerHTML = `
      <div class="rta-analysis">
        <h4>📊 Conversation Analysis</h4>
        ${analysis.sentiment ? `<div class="rta-metric"><strong>Sentiment:</strong> ${analysis.sentiment.overall || 'Neutral'}</div>` : ''}
        ${analysis.tone ? `<div class="rta-metric"><strong>Tone:</strong> ${analysis.tone}</div>` : ''}
        ${analysis.patterns ? `<div class="rta-metric"><strong>Patterns:</strong> ${analysis.patterns.join(', ')}</div>` : ''}
        ${analysis.recommendations ? `
          <div class="rta-recommendations">
            <strong>Recommendations:</strong>
            <ul>
              ${analysis.recommendations.map(rec => `<li>${rec}</li>`).join('')}
            </ul>
          </div>
        ` : ''}
      </div>
    `;

    this.switchTab('analysis');
  }

  setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      // Ctrl/Cmd + Shift + R: Toggle panel
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'R') {
        e.preventDefault();
        this.togglePanel();
      }

      // Ctrl/Cmd + Shift + S: Get suggestion
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'S') {
        e.preventDefault();
        this.getSuggestion();
      }
    });
  }

  setupWebSocketListener() {
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      if (message.type === 'WEBSOCKET_MESSAGE') {
        this.handleWebSocketMessage(message.data);
      }
    });
  }

  handleWebSocketMessage(data) {
    // Handle real-time updates from the server
    if (data.type === 'suggestion') {
      this.displaySuggestion(data.suggestion);
    } else if (data.type === 'analysis') {
      this.displayAnalysis(data.analysis);
    }
  }

  // Panel management methods
  togglePanel() {
    if (this.assistantPanel.classList.contains('rta-hidden')) {
      this.showPanel();
    } else {
      this.hidePanel();
    }
  }

  showPanel() {
    this.assistantPanel.classList.remove('rta-hidden');
  }

  hidePanel() {
    this.assistantPanel.classList.add('rta-hidden');
  }

  minimizePanel() {
    this.assistantPanel.classList.toggle('rta-minimized');
  }

  switchTab(tabName) {
    // Remove active class from all tabs and content
    this.assistantPanel.querySelectorAll('.rta-tab').forEach(tab => {
      tab.classList.remove('rta-tab-active');
    });
    this.assistantPanel.querySelectorAll('.rta-tab-content').forEach(content => {
      content.classList.remove('rta-tab-active');
    });

    // Add active class to selected tab and content
    this.assistantPanel.querySelector(`[data-tab="${tabName}"]`).classList.add('rta-tab-active');
    this.assistantPanel.querySelector(`#rta-${tabName}`).classList.add('rta-tab-active');
  }

  toggleAutoMode() {
    const autoBtn = document.getElementById('rta-toggle-auto');
    const isEnabled = autoBtn.textContent.includes('ON');

    autoBtn.textContent = isEnabled ? 'Auto: OFF' : 'Auto: ON';
    autoBtn.classList.toggle('rta-auto-enabled');
  }

  isAutoModeEnabled() {
    const autoBtn = document.getElementById('rta-toggle-auto');
    return autoBtn && autoBtn.textContent.includes('ON');
  }

  makeDraggable() {
    const header = this.assistantPanel.querySelector('.rta-header');
    let isDragging = false;
    let currentX;
    let currentY;
    let initialX;
    let initialY;
    let xOffset = 0;
    let yOffset = 0;

    header.addEventListener('mousedown', (e) => {
      initialX = e.clientX - xOffset;
      initialY = e.clientY - yOffset;

      if (e.target === header || header.contains(e.target)) {
        isDragging = true;
      }
    });

    document.addEventListener('mousemove', (e) => {
      if (isDragging) {
        e.preventDefault();
        currentX = e.clientX - initialX;
        currentY = e.clientY - initialY;

        xOffset = currentX;
        yOffset = currentY;

        this.assistantPanel.style.transform = `translate(${currentX}px, ${currentY}px)`;
      }
    });

    document.addEventListener('mouseup', () => {
      isDragging = false;
    });
  }

  updateStatus(status) {
    const statusElement = this.assistantPanel.querySelector('.rta-status');
    if (statusElement) {
      statusElement.textContent = status;
    }
  }

  showError(error) {
    this.updateStatus(`Error: ${error}`);
    setTimeout(() => {
      this.updateStatus('Ready');
    }, 3000);
  }

  async sendMessage(message) {
    return new Promise((resolve) => {
      chrome.runtime.sendMessage(message, resolve);
    });
  }
}

// Initialize the assistant when the script loads
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new RelationshipAssistant();
  });
} else {
  new RelationshipAssistant();
}