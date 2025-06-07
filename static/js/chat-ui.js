/**
 * Core Engine Chat UI
 * Handles all chat functionality for the Relationship Therapist System
 */

// Global variables for chat
let chatHistory = [];
let currentChatId = null;
let knowledgeBase = [];
let apiSettings = {
    provider: localStorage.getItem('api_provider') || 'openai',
    apiKey: localStorage.getItem('api_key') || '',
    model: localStorage.getItem('api_model') || 'gpt-4',
    endpoint: localStorage.getItem('api_endpoint') || ''
};

// Initialize chat UI
function initChatUI() {
    // Set up event listeners
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const newChatBtn = document.getElementById('new-chat-btn');
    const uploadBtn = document.getElementById('upload-btn');
    const chatAnalyzeBtn = document.getElementById('chat-analyze-btn');
    const chatSettingsBtn = document.getElementById('chat-settings-btn');

    // Chat form submission
    if (chatForm) {
        chatForm.addEventListener('submit', function (e) {
            e.preventDefault();
            sendMessage();
        });
    }

    // Auto-resize textarea as user types
    if (chatInput) {
        chatInput.addEventListener('input', function () {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    }

    // New chat button
    if (newChatBtn) {
        newChatBtn.addEventListener('click', createNewChat);
    }

    // Upload button
    if (uploadBtn) {
        uploadBtn.addEventListener('click', function () {
            openModal('upload-modal');
        });
    }

    // Analyze conversation button
    if (chatAnalyzeBtn) {
        chatAnalyzeBtn.addEventListener('click', analyzeCurrentConversation);
    }

    // Settings button
    if (chatSettingsBtn) {
        chatSettingsBtn.addEventListener('click', function () {
            openModal('settings-modal');
        });
    }

    // Initialize settings panel
    initSettingsPanel();

    // Load conversation history
    loadConversationHistory();

    // Initialize first chat if no history exists
    if (chatHistory.length === 0) {
        createNewChat();
    }
}

// Send a message
async function sendMessage() {
    const chatInput = document.getElementById('chat-input');
    const messageText = chatInput.value.trim();

    if (!messageText) return;

    // Add user message to UI
    addMessageToUI('user', messageText);

    // Clear input
    chatInput.value = '';
    chatInput.style.height = 'auto';

    // Save message to history
    saveMessageToHistory('user', messageText);

    // Show typing indicator
    showTypingIndicator();

    try {
        // Get response from AI
        const response = await getAIResponse(messageText);

        // Hide typing indicator
        hideTypingIndicator();

        // Add AI response to UI
        addMessageToUI('assistant', response);

        // Save AI response to history
        saveMessageToHistory('assistant', response);

        // Update conversation insights
        updateConversationInsights();

    } catch (error) {
        console.error('Error getting AI response:', error);

        // Hide typing indicator
        hideTypingIndicator();

        // Show error message
        addMessageToUI('system', 'Sorry, there was an error processing your request. Please try again.');
    }

    // Scroll to bottom
    scrollToBottom();
}

// Add message to UI
function addMessageToUI(role, content) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageWrapper = document.createElement('div');
    messageWrapper.className = `message-wrapper ${role}`;

    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    messageWrapper.innerHTML = `
    <div class="message">
      <div class="message-content">
        <p>${formatMessageContent(content)}</p>
      </div>
      <div class="message-time">${timestamp}</div>
    </div>
  `;

    messagesContainer.appendChild(messageWrapper);
    scrollToBottom();
}

// Format message content (convert URLs, line breaks, etc.)
function formatMessageContent(content) {
    // Convert URLs to links
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    content = content.replace(urlRegex, url => `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`);

    // Convert line breaks to <br>
    content = content.replace(/\n/g, '<br>');

    return content;
}

// Show typing indicator
function showTypingIndicator() {
    const messagesContainer = document.getElementById('chat-messages');
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    typingIndicator.id = 'typing-indicator';
    typingIndicator.innerHTML = `
    <div class="message-wrapper assistant">
      <div class="message">
        <div class="typing-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
  `;

    messagesContainer.appendChild(typingIndicator);
    scrollToBottom();
}

// Hide typing indicator
function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Scroll chat to bottom
function scrollToBottom() {
    const messagesContainer = document.getElementById('chat-messages');
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Save message to history
function saveMessageToHistory(role, content) {
    if (!currentChatId) {
        createNewChat();
    }

    // Find current chat in history
    const chatIndex = chatHistory.findIndex(chat => chat.id === currentChatId);

    if (chatIndex >= 0) {
        // Add message to existing chat
        chatHistory[chatIndex].messages.push({
            role,
            content,
            timestamp: new Date().toISOString()
        });

        // Update chat title if it's the first user message
        if (role === 'user' && chatHistory[chatIndex].messages.filter(m => m.role === 'user').length === 1) {
            chatHistory[chatIndex].title = generateChatTitle(content);
            updateChatHistoryUI();
        }

        // Save to localStorage
        saveChatsToLocalStorage();
    }
}

// Create a new chat
function createNewChat() {
    // Generate a unique ID
    const chatId = 'chat_' + Date.now();

    // Create chat object
    const newChat = {
        id: chatId,
        title: 'New Conversation',
        created: new Date().toISOString(),
        messages: [
            {
                role: 'system',
                content: 'Hello! I\'m your relationship therapist AI assistant. How can I help you today?',
                timestamp: new Date().toISOString()
            }
        ]
    };

    // Add to history
    chatHistory.unshift(newChat);

    // Set as current chat
    currentChatId = chatId;

    // Save to localStorage
    saveChatsToLocalStorage();

    // Update UI
    updateChatHistoryUI();

    // Clear and reset chat messages
    const messagesContainer = document.getElementById('chat-messages');
    messagesContainer.innerHTML = '';

    // Add initial system message
    addMessageToUI('system', newChat.messages[0].content);
}

// Generate a title for the chat based on first message
function generateChatTitle(message) {
    // Get first 30 characters of message
    let title = message.substring(0, 30).trim();

    // Add ellipsis if truncated
    if (message.length > 30) {
        title += '...';
    }

    return title;
}

// Load conversation history from localStorage
function loadConversationHistory() {
    const savedChats = localStorage.getItem('chat_history');

    if (savedChats) {
        try {
            chatHistory = JSON.parse(savedChats);

            // Set current chat to most recent
            if (chatHistory.length > 0) {
                currentChatId = chatHistory[0].id;
                loadChat(currentChatId);
            }

            // Update UI
            updateChatHistoryUI();

        } catch (error) {
            console.error('Error loading chat history:', error);
            chatHistory = [];
        }
    }
}

// Save chats to localStorage
function saveChatsToLocalStorage() {
    localStorage.setItem('chat_history', JSON.stringify(chatHistory));
}

// Update chat history UI
function updateChatHistoryUI() {
    const chatHistoryContainer = document.getElementById('chat-history');

    if (!chatHistoryContainer) return;

    // Clear existing items
    chatHistoryContainer.innerHTML = '';

    // Add each chat to sidebar
    chatHistory.forEach(chat => {
        const chatItem = document.createElement('div');
        chatItem.className = `chat-history-item ${chat.id === currentChatId ? 'active' : ''}`;
        chatItem.dataset.chatId = chat.id;

        // Format date
        const chatDate = new Date(chat.created);
        const formattedDate = formatRelativeTime(chatDate);

        chatItem.innerHTML = `
      <div class="chat-history-title">${chat.title}</div>
      <div class="chat-history-time">${formattedDate}</div>
    `;

        // Add click event to load chat
        chatItem.addEventListener('click', function () {
            loadChat(chat.id);
        });

        chatHistoryContainer.appendChild(chatItem);
    });
}

// Format relative time (e.g., "2 hours ago", "Yesterday", etc.)
function formatRelativeTime(date) {
    const now = new Date();
    const diffMs = now - date;
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHour = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHour / 24);

    if (diffDay > 6) {
        return date.toLocaleDateString();
    } else if (diffDay > 1) {
        return `${diffDay} days ago`;
    } else if (diffDay === 1) {
        return 'Yesterday';
    } else if (diffHour >= 1) {
        return `${diffHour} hour${diffHour > 1 ? 's' : ''} ago`;
    } else if (diffMin >= 1) {
        return `${diffMin} minute${diffMin > 1 ? 's' : ''} ago`;
    } else {
        return 'Just now';
    }
}

// Load a specific chat
function loadChat(chatId) {
    // Find chat in history
    const chat = chatHistory.find(c => c.id === chatId);

    if (!chat) return;

    // Set as current chat
    currentChatId = chatId;

    // Update UI to show this chat is active
    updateChatHistoryUI();

    // Clear current messages
    const messagesContainer = document.getElementById('chat-messages');
    messagesContainer.innerHTML = '';

    // Add all messages from this chat
    chat.messages.forEach(message => {
        addMessageToUI(message.role, message.content);
    });

    // Update conversation insights
    updateConversationInsights();
}

// Update conversation insights panel
function updateConversationInsights() {
    // Find current chat
    const chat = chatHistory.find(c => c.id === currentChatId);

    if (!chat || chat.messages.length < 2) return;

    // Get only user and assistant messages (skip system)
    const messages = chat.messages.filter(m => m.role === 'user' || m.role === 'assistant');

    // Skip if not enough messages
    if (messages.length < 2) return;

    // Simple sentiment analysis (just for demo)
    const userMessages = messages.filter(m => m.role === 'user');
    const positiveWords = ['happy', 'good', 'great', 'excellent', 'love', 'appreciate', 'thank', 'pleased'];
    const negativeWords = ['sad', 'bad', 'angry', 'upset', 'hate', 'dislike', 'disappointed', 'sorry'];

    let positiveCount = 0;
    let negativeCount = 0;
    let totalWords = 0;

    userMessages.forEach(message => {
        const words = message.content.toLowerCase().split(/\s+/);
        totalWords += words.length;

        words.forEach(word => {
            if (positiveWords.some(pw => word.includes(pw))) positiveCount++;
            if (negativeWords.some(nw => word.includes(nw))) negativeCount++;
        });
    });

    // Calculate sentiment score (between 0-100)
    const sentimentScore = totalWords > 0
        ? Math.min(100, Math.max(0, Math.round(100 * (positiveCount - negativeCount) / totalWords + 50)))
        : 50;

    // Update sentiment indicator
    const sentimentValue = document.querySelector('.sentiment-value');
    const sentimentLabel = document.querySelector('.sentiment-label');

    if (sentimentValue && sentimentLabel) {
        sentimentValue.style.width = `${sentimentScore}%`;

        let sentimentText = 'Neutral';
        if (sentimentScore > 70) sentimentText = 'Positive';
        if (sentimentScore < 30) sentimentText = 'Negative';

        sentimentLabel.textContent = `${sentimentText} (${sentimentScore}%)`;
    }

    // Extract key topics (simplified)
    const topicAnalysis = analyzeTopics(userMessages);
    const topicTags = document.querySelector('.topic-tags');

    if (topicTags) {
        topicTags.innerHTML = '';
        topicAnalysis.slice(0, 3).forEach(topic => {
            const tag = document.createElement('span');
            tag.className = 'tag';
            tag.textContent = topic;
            topicTags.appendChild(tag);
        });
    }
}

// Simple topic analysis (for demo)
function analyzeTopics(messages) {
    const topics = [
        'Communication', 'Trust', 'Intimacy', 'Conflict',
        'Emotional Support', 'Appreciation', 'Quality Time',
        'Boundaries', 'Future Planning', 'Values'
    ];

    // In a real implementation, this would use NLP to extract topics
    // For demo, just return random topics
    return topics.sort(() => 0.5 - Math.random()).slice(0, 3);
}

// Get AI response
async function getAIResponse(message) {
    // In a production system, this would call the actual AI API
    // For demo, we'll use the mock API
    try {
        // Call API
        const response = await window.coreEngineAPI.sendMessage(message);
        return response.message || "I'm not sure how to respond to that.";
    } catch (error) {
        console.error('Error getting AI response:', error);

        // For demo, return fallback response
        return "I apologize, but I'm having trouble connecting to the AI service. Please check your API settings or try again later.";
    }
}

// Analyze current conversation
async function analyzeCurrentConversation() {
    // Find current chat
    const chat = chatHistory.find(c => c.id === currentChatId);

    if (!chat || chat.messages.length < 3) {
        alert('Please have a longer conversation before analyzing.');
        return;
    }

    // Open analysis modal
    openModal('analysis-modal');

    // Show loading
    document.getElementById('analysis-loading').style.display = 'flex';
    document.getElementById('analysis-results').style.display = 'none';

    try {
        // Get messages in format for analysis
        const messages = chat.messages
            .filter(m => m.role !== 'system')
            .map(m => ({
                role: m.role,
                content: m.content,
                timestamp: m.timestamp
            }));

        // Call API for analysis
        const analysisResult = await window.coreEngineAPI.analyzeConversation({
            conversation: messages,
            analysis_type: 'comprehensive'
        });

        // Hide loading, show results
        document.getElementById('analysis-loading').style.display = 'none';
        document.getElementById('analysis-results').style.display = 'block';

        // Update charts and results
        updateAnalysisCharts(analysisResult);
        updateAnalysisResults(analysisResult);

    } catch (error) {
        console.error('Analysis error:', error);

        // Hide loading
        document.getElementById('analysis-loading').style.display = 'none';

        // Show error
        alert('Error analyzing conversation. Please try again.');
        closeModal('analysis-modal');
    }
}

// Update analysis charts
function updateAnalysisCharts(analysisData) {
    // Communication patterns chart
    const commCtx = document.getElementById('communicationChart');
    if (commCtx) {
        const patterns = analysisData.communication_patterns || {
            active_listening: 0.8,
            empathy_shown: 0.7,
            conflict_resolution: 0.6,
            emotional_support: 0.75,
            validation: 0.65
        };

        // Convert to percentage
        const patternValues = [
            patterns.active_listening * 100,
            patterns.empathy_shown * 100,
            patterns.conflict_resolution * 100,
            patterns.emotional_support * 100,
            patterns.validation * 100
        ];

        if (window.communicationChart) {
            window.communicationChart.destroy();
        }

        window.communicationChart = new Chart(commCtx, {
            type: 'radar',
            data: {
                labels: ['Active Listening', 'Empathy', 'Conflict Resolution', 'Emotional Support', 'Validation'],
                datasets: [{
                    label: 'Communication Quality',
                    data: patternValues,
                    backgroundColor: 'rgba(14, 165, 233, 0.2)',
                    borderColor: 'rgba(14, 165, 233, 1)',
                    pointBackgroundColor: 'rgba(14, 165, 233, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(14, 165, 233, 1)'
                }]
            },
            options: {
                scales: {
                    r: {
                        angleLines: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        pointLabels: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        },
                        ticks: {
                            backdropColor: 'transparent',
                            color: 'rgba(255, 255, 255, 0.7)'
                        },
                        min: 0,
                        max: 100
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        }
                    }
                }
            }
        });
    }

    // Sentiment chart
    const sentCtx = document.getElementById('sentimentChart');
    if (sentCtx) {
        // For demo, create mock sentiment data
        const sentimentLabels = [];
        const sentimentData = [];

        // Generate 10 data points from 0-100%
        for (let i = 0; i < 10; i++) {
            sentimentLabels.push(`Message ${i + 1}`);
            sentimentData.push(Math.round(30 + 40 * Math.sin(i / 2) + Math.random() * 20));
        }

        if (window.sentimentChart) {
            window.sentimentChart.destroy();
        }

        window.sentimentChart = new Chart(sentCtx, {
            type: 'line',
            data: {
                labels: sentimentLabels,
                datasets: [{
                    label: 'Sentiment Score',
                    data: sentimentData,
                    borderColor: 'rgba(139, 92, 246, 1)',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                scales: {
                    y: {
                        min: 0,
                        max: 100,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        }
                    }
                }
            }
        });
    }

    // Update overview statistics
    const statValues = document.querySelectorAll('.analysis-stat .stat-value');
    if (statValues.length >= 3) {
        // Set sentiment value
        statValues[0].textContent = `${Math.round(analysisData.sentiment_score * 100)}%`;

        // Set communication value (average of patterns)
        const patterns = analysisData.communication_patterns || {};
        const commAvg = Object.values(patterns).reduce((sum, val) => sum + val, 0) / Object.values(patterns).length;
        statValues[1].textContent = `${Math.round(commAvg * 100)}%`;

        // Set relationship health
        statValues[2].textContent = `${Math.round(analysisData.relationship_health * 100)}%`;
    }
}

// Update analysis results
function updateAnalysisResults(analysisData) {
    // Update insights list
    const insightsList = document.getElementById('insights-list');
    if (insightsList) {
        insightsList.innerHTML = '';

        // Add each insight
        analysisData.insights.forEach(insight => {
            const li = document.createElement('li');
            li.textContent = insight;
            insightsList.appendChild(li);
        });
    }

    // Update recommendations
    const recommendationsList = document.getElementById('recommendations-list');
    if (recommendationsList) {
        recommendationsList.innerHTML = '';

        // Add each recommendation
        analysisData.recommendations.forEach(recommendation => {
            const card = document.createElement('div');
            card.className = 'recommendation-card';

            // Split at first period or colon to create title and content
            const parts = recommendation.split(/[:\.]/);
            let title = 'Recommendation';
            let content = recommendation;

            if (parts.length > 1) {
                title = parts[0].trim();
                content = parts.slice(1).join('. ').trim();
            }

            card.innerHTML = `
        <h4>${title}</h4>
        <p>${content}</p>
      `;

            recommendationsList.appendChild(card);
        });
    }
}

// Initialize settings panel
function initSettingsPanel() {
    // Provider select
    const providerSelect = document.getElementById('provider-select');
    if (providerSelect) {
        providerSelect.value = apiSettings.provider;

        providerSelect.addEventListener('change', function () {
            apiSettings.provider = this.value;
            localStorage.setItem('api_provider', this.value);

            // Show/hide endpoint field based on provider
            const endpointGroup = document.querySelector('.api-endpoint-group');
            if (endpointGroup) {
                endpointGroup.classList.toggle('hidden', this.value !== 'custom');
            }

            // Update model options based on provider
            updateModelOptions(this.value);
        });
    }

    // API Key input
    const apiKeyInput = document.getElementById('api-key');
    if (apiKeyInput) {
        apiKeyInput.value = apiSettings.apiKey;

        apiKeyInput.addEventListener('change', function () {
            apiSettings.apiKey = this.value;
            localStorage.setItem('api_key', this.value);
        });
    }

    // Model select
    const modelSelect = document.getElementById('model-select');
    if (modelSelect) {
        // Initialize with appropriate options
        updateModelOptions(apiSettings.provider);

        modelSelect.value = apiSettings.model;

        modelSelect.addEventListener('change', function () {
            apiSettings.model = this.value;
            localStorage.setItem('api_model', this.value);
        });
    }

    // API Endpoint input
    const apiEndpointInput = document.getElementById('api-endpoint');
    if (apiEndpointInput) {
        apiEndpointInput.value = apiSettings.endpoint;

        apiEndpointInput.addEventListener('change', function () {
            apiSettings.endpoint = this.value;
            localStorage.setItem('api_endpoint', this.value);
        });
    }

    // API Settings form
    const apiSettingsForm = document.getElementById('api-settings-form');
    if (apiSettingsForm) {
        apiSettingsForm.addEventListener('submit', function (e) {
            e.preventDefault();
            saveAPISettings();
        });
    }

    // Test connection button
    const testConnectionBtn = document.getElementById('test-connection-btn');
    if (testConnectionBtn) {
        testConnectionBtn.addEventListener('click', testAPIConnection);
    }

    // Settings tabs
    const settingsTabs = document.querySelectorAll('.settings-tab');
    settingsTabs.forEach(tab => {
        tab.addEventListener('click', function () {
            // Remove active class from all tabs
            settingsTabs.forEach(t => t.classList.remove('active'));

            // Add active class to clicked tab
            this.classList.add('active');

            // Hide all panes
            document.querySelectorAll('.settings-pane').forEach(pane => {
                pane.classList.remove('active');
            });

            // Show selected pane
            const paneId = this.dataset.tab;
            document.getElementById(paneId).classList.add('active');
        });
    });

    // Knowledge upload
    setupKnowledgeUpload();

    // Install extension button
    const installExtensionBtn = document.getElementById('install-extension-btn');
    if (installExtensionBtn) {
        installExtensionBtn.addEventListener('click', function () {
            alert('Browser extension installation coming soon. This will be implemented in the production version.');
        });
    }
}

// Update model options based on provider
function updateModelOptions(provider) {
    const modelSelect = document.getElementById('model-select');
    if (!modelSelect) return;

    // Clear existing options
    modelSelect.innerHTML = '';

    // Add options based on provider
    switch (provider) {
        case 'openai':
            addOption(modelSelect, 'gpt-4', 'GPT-4');
            addOption(modelSelect, 'gpt-4-turbo', 'GPT-4 Turbo');
            addOption(modelSelect, 'gpt-3.5-turbo', 'GPT-3.5 Turbo');
            break;

        case 'anthropic':
            addOption(modelSelect, 'claude-3-opus', 'Claude 3 Opus');
            addOption(modelSelect, 'claude-3-sonnet', 'Claude 3 Sonnet');
            addOption(modelSelect, 'claude-3-haiku', 'Claude 3 Haiku');
            break;

        case 'mcp':
            addOption(modelSelect, 'gpt-4', 'GPT-4');
            addOption(modelSelect, 'claude-3', 'Claude 3');
            addOption(modelSelect, 'llama-3', 'Llama 3');
            addOption(modelSelect, 'gemini-pro', 'Gemini Pro');
            break;

        case 'custom':
            addOption(modelSelect, 'custom', 'Custom Model');
            break;
    }

    // Select first option
    if (modelSelect.options.length > 0) {
        modelSelect.selectedIndex = 0;
        apiSettings.model = modelSelect.value;
        localStorage.setItem('api_model', modelSelect.value);
    }
}

// Helper to add option to select
function addOption(select, value, text) {
    const option = document.createElement('option');
    option.value = value;
    option.textContent = text;
    select.appendChild(option);
}

// Save API settings
function saveAPISettings() {
    const provider = document.getElementById('provider-select').value;
    const apiKey = document.getElementById('api-key').value;
    const model = document.getElementById('model-select').value;
    const endpoint = document.getElementById('api-endpoint').value;

    // Save to local settings
    apiSettings.provider = provider;
    apiSettings.apiKey = apiKey;
    apiSettings.model = model;
    apiSettings.endpoint = endpoint;

    // Save to localStorage
    localStorage.setItem('api_provider', provider);
    localStorage.setItem('api_key', apiKey);
    localStorage.setItem('api_model', model);
    localStorage.setItem('api_endpoint', endpoint);

    // Notify user
    alert('API settings saved successfully');

    // Close modal
    closeModal('settings-modal');
}

// Test API connection
async function testAPIConnection() {
    const testBtn = document.getElementById('test-connection-btn');

    // Save current settings
    const provider = document.getElementById('provider-select').value;
    const apiKey = document.getElementById('api-key').value;
    const model = document.getElementById('model-select').value;
    const endpoint = document.getElementById('api-endpoint').value;

    // Set button to loading state
    testBtn.textContent = 'Testing...';
    testBtn.disabled = true;

    try {
        // Call API test endpoint
        const result = await window.coreEngineAPI.testConnection({
            provider,
            apiKey,
            model,
            endpoint
        });

        // Show success message
        alert('Connection successful! The API is working correctly.');

    } catch (error) {
        console.error('API test error:', error);

        // Show error message
        alert(`Connection failed: ${error.message || 'Unknown error'}`);

    } finally {
        // Reset button
        testBtn.textContent = 'Test Connection';
        testBtn.disabled = false;
    }
}

// Setup knowledge base upload
function setupKnowledgeUpload() {
    const fileUploadArea = document.querySelector('.file-upload-placeholder');
    const fileInput = document.getElementById('knowledge-files');
    const fileList = document.getElementById('knowledge-file-list');

    if (!fileUploadArea || !fileInput || !fileList) return;

    // Click to browse
    fileUploadArea.addEventListener('click', function () {
        fileInput.click();
    });

    // File selection changed
    fileInput.addEventListener('change', function () {
        handleKnowledgeFiles(this.files);
    });

    // Drag and drop
    fileUploadArea.addEventListener('dragover', function (e) {
        e.preventDefault();
        fileUploadArea.classList.add('drag-over');
    });

    fileUploadArea.addEventListener('dragleave', function () {
        fileUploadArea.classList.remove('drag-over');
    });

    fileUploadArea.addEventListener('drop', function (e) {
        e.preventDefault();
        fileUploadArea.classList.remove('drag-over');

        if (e.dataTransfer.files.length > 0) {
            handleKnowledgeFiles(e.dataTransfer.files);
        }
    });

    // Knowledge form submission
    const knowledgeForm = document.getElementById('knowledge-settings-form');
    if (knowledgeForm) {
        knowledgeForm.addEventListener('submit', function (e) {
            e.preventDefault();
            saveKnowledgeSettings();
        });
    }
}

// Handle knowledge base files
function handleKnowledgeFiles(files) {
    const fileList = document.getElementById('knowledge-file-list');

    if (!fileList) return;

    // Clear list
    fileList.innerHTML = '';

    // Add each file
    Array.from(files).forEach(file => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';

        fileItem.innerHTML = `
      <div class="file-info">
        <span class="file-name">${file.name}</span>
        <span class="file-size">(${formatFileSize(file.size)})</span>
      </div>
      <button type="button" class="btn btn-icon remove-file">×</button>
    `;

        // Remove button
        fileItem.querySelector('.remove-file').addEventListener('click', function () {
            fileItem.remove();
        });

        fileList.appendChild(fileItem);
    });
}

// Format file size
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
}

// Save knowledge settings
function saveKnowledgeSettings() {
    const format = document.getElementById('knowledge-format').value;
    const fileItems = document.querySelectorAll('.file-item .file-name');

    // Get filenames
    const fileNames = Array.from(fileItems).map(item => item.textContent);

    // Save format preference
    localStorage.setItem('knowledge_format', format);

    // In a real implementation, this would upload files to the server
    // For demo, just show message
    alert(`Knowledge base settings saved. Format: ${format}, Files: ${fileNames.join(', ')}`);

    // Close modal
    closeModal('settings-modal');
}

// Open a modal
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';

        // Add event listener to close button
        const closeButtons = modal.querySelectorAll('.close-modal-btn');
        closeButtons.forEach(btn => {
            btn.addEventListener('click', function () {
                closeModal(modalId);
            });
        });

        // Close when clicking outside content
        modal.addEventListener('click', function (e) {
            if (e.target === modal) {
                closeModal(modalId);
            }
        });
    }
}

// Close a modal
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// Set up all modals
function setupModals() {
    // Close buttons
    document.querySelectorAll('.close-modal-btn').forEach(btn => {
        const modal = btn.closest('.modal');
        if (modal) {
            btn.addEventListener('click', function () {
                modal.style.display = 'none';
            });
        }
    });

    // Close when clicking outside content
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function (e) {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    });
}

// Initialize when document loads
document.addEventListener('DOMContentLoaded', function () {
    // Initialize chat
    initChatUI();
});
