/**
 * MirrorCore Relationship Therapist - Chat Interface
 * Handles the chat UI interactions, message rendering, and API communication
 */

// DOM Elements
const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');
const messagesContainer = document.getElementById('messages-container');
const sendButton = document.getElementById('send-button');
const analyzeButton = document.getElementById('analyze-button');
const uploadButton = document.getElementById('upload-button');
const settingsToggle = document.getElementById('settings-toggle');
const closeSettings = document.getElementById('close-settings');
const settingsPanel = document.getElementById('settings-panel');
const saveSettings = document.getElementById('save-settings');
const providerSelect = document.getElementById('provider-select');
const modelSelect = document.getElementById('model-select');
const apiKeyInput = document.getElementById('api-key');
const kbFormatSelect = document.getElementById('kb-format');
const customKbContainer = document.getElementById('custom-kb-container');
const testMcpConnection = document.getElementById('test-mcp-connection');
const installExtension = document.getElementById('install-extension');
const upgradeSubscription = document.getElementById('upgrade-subscription');
const connectionStatus = document.getElementById('connection-status');

// Analysis Modal Elements
const analysisModal = document.getElementById('analysis-modal');
const closeAnalysis = document.getElementById('close-analysis');
const closeAnalysisBtn = document.getElementById('close-analysis-btn');
const saveAnalysis = document.getElementById('save-analysis');
const analysisLoading = document.getElementById('analysis-loading');
const analysisResults = document.getElementById('analysis-results');
const insightsList = document.getElementById('insights-list');
const recommendationsList = document.getElementById('recommendations-list');

// Upload Modal Elements
const uploadModal = document.getElementById('upload-modal');
const closeUpload = document.getElementById('close-upload');
const cancelUpload = document.getElementById('cancel-upload');
const processUpload = document.getElementById('process-upload');
const dropArea = document.getElementById('drop-area');
const fileInput = document.getElementById('file-input');
const platformSelect = document.getElementById('platform-select');

// State variables
let conversationHistory = [];
let selectedFile = null;
let settings = {
    provider: 'openai',
    model: 'gpt-4',
    apiKey: '',
    mcpEndpoint: 'http://localhost:5001/mcp',
    knowledgeBaseFormat: 'relationship_counseling',
    customKnowledgeBase: '',
    extensionInstalled: false,
    subscriptionPlan: 'free'
};

// Initialize API Client
const api = new MirrorCoreAPI();

// Initialize Charts
let sentimentChart = null;
let communicationChart = null;

// ===============================================
// Initialization
// ===============================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize API client
    fetchSettings();

    // Attach event listeners
    attachEventListeners();

    // Add welcome message
    addMessage({
        role: 'assistant',
        content: 'Hello! I\'m your relationship therapist AI. How can I help you today?',
        timestamp: new Date().toISOString()
    });
});

// Attach event listeners to UI elements
function attachEventListeners() {
    // Chat form submission
    if (chatForm) {
        chatForm.addEventListener('submit', handleChatSubmit);
    }

    // Analysis button
    if (analyzeButton) {
        analyzeButton.addEventListener('click', handleAnalyzeClick);
    }

    // Upload button
    if (uploadButton) {
        uploadButton.addEventListener('click', handleUploadClick);
    }

    // Settings toggle
    if (settingsToggle) {
        settingsToggle.addEventListener('click', toggleSettingsPanel);
    }

    // Close settings
    if (closeSettings) {
        closeSettings.addEventListener('click', toggleSettingsPanel);
    }

    // Save settings
    if (saveSettings) {
        saveSettings.addEventListener('click', saveUserSettings);
    }

    // Test MCP connection
    if (testMcpConnection) {
        testMcpConnection.addEventListener('click', testConnection);
    }

    // Install extension
    if (installExtension) {
        installExtension.addEventListener('click', handleInstallExtension);
    }

    // Upgrade subscription
    if (upgradeSubscription) {
        upgradeSubscription.addEventListener('click', handleUpgradeSubscription);
    }

    // KB Format change
    if (kbFormatSelect) {
        kbFormatSelect.addEventListener('change', handleKbFormatChange);
    }

    // Analysis modal
    if (closeAnalysis) {
        closeAnalysis.addEventListener('click', () => {
            analysisModal.classList.add('hidden');
        });
    }

    if (closeAnalysisBtn) {
        closeAnalysisBtn.addEventListener('click', () => {
            analysisModal.classList.add('hidden');
        });
    }

    // Upload modal
    if (closeUpload) {
        closeUpload.addEventListener('click', () => {
            uploadModal.classList.add('hidden');
        });
    }

    if (cancelUpload) {
        cancelUpload.addEventListener('click', () => {
            uploadModal.classList.add('hidden');
        });
    }

    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }

    if (dropArea) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, unhighlight, false);
        });

        dropArea.addEventListener('drop', handleDrop, false);
    }

    if (processUpload) {
        processUpload.addEventListener('click', handleProcessUpload);
    }
}

// Handle chat form submission
async function handleChatSubmit(e) {
    e.preventDefault();

    const message = messageInput.value.trim();
    if (!message) return;

    // Add user message to UI
    const userMessage = {
        role: 'user',
        content: message,
        timestamp: new Date().toISOString()
    };

    addMessage(userMessage);

    // Clear input
    messageInput.value = '';

    // Add to history
    conversationHistory.push(userMessage);

    // Show typing indicator
    showTypingIndicator();

    try {
        // Call API
        const response = await sendChatMessage(userMessage);

        // Hide typing indicator
        hideTypingIndicator();

        // Add response to UI
        const assistantMessage = {
            role: 'assistant',
            content: response.message.content,
            timestamp: response.message.timestamp
        };

        addMessage(assistantMessage);

        // Add to history
        conversationHistory.push(assistantMessage);

    } catch (error) {
        // Hide typing indicator
        hideTypingIndicator();

        console.error('Error sending message:', error);

        // Show error message
        addMessage({
            role: 'system',
            content: 'Sorry, there was an error processing your message. Please try again.',
            timestamp: new Date().toISOString()
        });
    }
}

// Send message to API
async function sendChatMessage(message) {
    const response = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            messages: conversationHistory,
            settings: settings
        })
    });

    if (!response.ok) {
        throw new Error('Failed to send message');
    }

    return await response.json();
}

// Add message to UI
function addMessage(message) {
    const messageEl = document.createElement('div');
    messageEl.className = `message message-${message.role}`;

    const timestamp = new Date(message.timestamp).toLocaleTimeString();

    messageEl.innerHTML = `
        <div class="message-content">
            <div class="message-text">${formatMessageContent(message.content)}</div>
            <div class="message-time">${timestamp}</div>
        </div>
    `;

    messagesContainer.appendChild(messageEl);

    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Format message content (convert links, etc.)
function formatMessageContent(content) {
    // Convert URLs to links
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    return content.replace(urlRegex, url => `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`);
}

// Show typing indicator
function showTypingIndicator() {
    const typingEl = document.createElement('div');
    typingEl.className = 'message message-typing';
    typingEl.id = 'typing-indicator';

    typingEl.innerHTML = `
        <div class="message-content">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;

    messagesContainer.appendChild(typingEl);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Hide typing indicator
function hideTypingIndicator() {
    const typingEl = document.getElementById('typing-indicator');
    if (typingEl) {
        typingEl.remove();
    }
}

// Handle analyze button click
async function handleAnalyzeClick() {
    if (conversationHistory.length < 2) {
        alert('Please have a conversation first before analyzing.');
        return;
    }

    // Show analysis modal
    analysisModal.classList.remove('hidden');

    // Show loading state
    analysisLoading.classList.remove('hidden');
    analysisResults.classList.add('hidden');

    try {
        // Call API
        const response = await fetch('/api/v1/chat/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                messages: conversationHistory
            })
        });

        if (!response.ok) {
            throw new Error('Failed to analyze conversation');
        }

        const data = await response.json();

        // Hide loading, show results
        analysisLoading.classList.add('hidden');
        analysisResults.classList.remove('hidden');

        // Render insights
        renderInsights(data.insights);

        // Render recommendations
        renderRecommendations(data.recommendations);

    } catch (error) {
        console.error('Error analyzing conversation:', error);

        // Hide loading
        analysisLoading.classList.add('hidden');

        // Show error
        analysisResults.innerHTML = `
            <div class="error-message">
                <p>Sorry, there was an error analyzing the conversation. Please try again.</p>
            </div>
        `;
        analysisResults.classList.remove('hidden');
    }
}

// Render insights list
function renderInsights(insights) {
    if (!insightsList) return;

    if (!insights || insights.length === 0) {
        insightsList.innerHTML = '<li>No insights available</li>';
        return;
    }

    insightsList.innerHTML = insights.map(insight => `
        <li>${insight}</li>
    `).join('');
}

// Render recommendations list
function renderRecommendations(recommendations) {
    if (!recommendationsList) return;

    if (!recommendations || recommendations.length === 0) {
        recommendationsList.innerHTML = '<li>No recommendations available</li>';
        return;
    }

    recommendationsList.innerHTML = recommendations.map(rec => `
        <li>${rec}</li>
    `).join('');
}

// Handle upload button click
function handleUploadClick() {
    uploadModal.classList.remove('hidden');
}

// Handle file select
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        selectedFile = file;
        updateFilePreview(file);
    }
}

// Handle file drop
function handleDrop(e) {
    const file = e.dataTransfer.files[0];
    if (file) {
        selectedFile = file;
        updateFilePreview(file);

        // Update file input
        if (fileInput) {
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            fileInput.files = dataTransfer.files;
        }
    }
}

// Update file preview
function updateFilePreview(file) {
    const previewEl = document.createElement('div');
    previewEl.className = 'file-preview';

    previewEl.innerHTML = `
        <div class="file-info">
            <span class="file-name">${file.name}</span>
            <span class="file-size">${formatFileSize(file.size)}</span>
        </div>
    `;

    const existingPreview = dropArea.querySelector('.file-preview');
    if (existingPreview) {
        dropArea.removeChild(existingPreview);
    }

    dropArea.appendChild(previewEl);
}

// Format file size
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' bytes';
    else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    else return (bytes / 1048576).toFixed(1) + ' MB';
}

// Handle process upload
async function handleProcessUpload() {
    if (!selectedFile) {
        alert('Please select a file first');
        return;
    }

    const platform = platformSelect.value;

    // Show loading state
    processUpload.disabled = true;
    processUpload.textContent = 'Processing...';

    try {
        // Read file
        const content = await readFileAsText(selectedFile);

        // Call API
        const response = await fetch('/api/v1/upload/conversation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                platform,
                content: JSON.parse(content)
            })
        });

        if (!response.ok) {
            throw new Error('Failed to process file');
        }

        const data = await response.json();

        // Hide modal
        uploadModal.classList.add('hidden');

        // Show success message
        addMessage({
            role: 'system',
            content: `Successfully processed ${platform} conversation: ${data.message}`,
            timestamp: new Date().toISOString()
        });

        // Reset state
        selectedFile = null;
        if (fileInput) fileInput.value = '';
        const existingPreview = dropArea.querySelector('.file-preview');
        if (existingPreview) {
            dropArea.removeChild(existingPreview);
        }

    } catch (error) {
        console.error('Error processing file:', error);
        alert('Error processing file. Please make sure it\'s a valid conversation export.');
    } finally {
        // Reset button
        processUpload.disabled = false;
        processUpload.textContent = 'Process';
    }
}

// Read file as text
function readFileAsText(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = event => resolve(event.target.result);
        reader.onerror = error => reject(error);
        reader.readAsText(file);
    });
}

// Toggle settings panel
function toggleSettingsPanel() {
    settingsPanel.classList.toggle('hidden');
}

// Fetch user settings
async function fetchSettings() {
    try {
        const response = await fetch('/api/v1/settings');
        if (!response.ok) {
            throw new Error('Failed to fetch settings');
        }

        const data = await response.json();

        // Update settings
        settings = {
            provider: data.ai_provider.provider,
            model: data.ai_provider.model,
            api_key: data.ai_provider.api_key,
            knowledge_base_format: data.knowledge_base_format,
            subscription_tier: data.subscription_tier,
            extension_installed: data.extension_installed
        };

        // Update UI
        updateSettingsUI();

    } catch (error) {
        console.error('Error fetching settings:', error);
    }
}

// Update settings UI
function updateSettingsUI() {
    // Provider
    if (providerSelect) {
        providerSelect.value = settings.provider;
    }

    // Model
    if (modelSelect) {
        modelSelect.value = settings.model;
    }

    // API key (masked)
    if (apiKeyInput) {
        apiKeyInput.value = settings.api_key || '';
    }

    // KB format
    if (kbFormatSelect) {
        kbFormatSelect.value = settings.knowledge_base_format;
    }

    // Custom KB container
    if (customKbContainer) {
        if (settings.knowledge_base_format === 'custom') {
            customKbContainer.classList.remove('hidden');
        } else {
            customKbContainer.classList.add('hidden');
        }
    }

    // Extension status
    const extensionStatus = document.getElementById('extension-status');
    if (extensionStatus) {
        if (settings.extension_installed) {
            extensionStatus.className = 'status-indicator status-success';
            extensionStatus.innerHTML = '<span class="status-dot"></span>Extension installed';
        } else {
            extensionStatus.className = 'status-indicator status-warning';
            extensionStatus.innerHTML = '<span class="status-dot"></span>Extension not installed';
        }
    }

    // Subscription tier
    const tierBadge = document.querySelector('.subscription-tier .tier-badge');
    if (tierBadge) {
        tierBadge.className = `tier-badge ${settings.subscription_tier}`;
        tierBadge.textContent = capitalizeFirstLetter(settings.subscription_tier);
    }
}

// Save user settings
async function saveUserSettings() {
    const newSettings = {
        ai_provider: {
            provider: providerSelect.value,
            model: modelSelect.value,
            api_key: apiKeyInput.value
        },
        knowledge_base_format: kbFormatSelect.value,
        subscription_tier: settings.subscription_tier,
        extension_installed: settings.extension_installed
    };

    try {
        const response = await fetch('/api/v1/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(newSettings)
        });

        if (!response.ok) {
            throw new Error('Failed to save settings');
        }

        const data = await response.json();

        // Update settings
        settings = {
            provider: data.settings.ai_provider.provider,
            model: data.settings.ai_provider.model,
            api_key: data.settings.ai_provider.api_key,
            knowledge_base_format: data.settings.knowledge_base_format,
            subscription_tier: data.settings.subscription_tier,
            extension_installed: data.settings.extension_installed
        };

        // Update UI
        updateSettingsUI();

        // Hide settings panel
        toggleSettingsPanel();

        // Show success message
        addMessage({
            role: 'system',
            content: 'Settings saved successfully',
            timestamp: new Date().toISOString()
        });

    } catch (error) {
        console.error('Error saving settings:', error);
        alert('Failed to save settings. Please try again.');
    }
}

// Handle KB format change
function handleKbFormatChange() {
    const format = kbFormatSelect.value;

    // Show/hide custom KB container
    if (format === 'custom') {
        customKbContainer.classList.remove('hidden');
    } else {
        customKbContainer.classList.add('hidden');
    }
}

// Test MCP connection
async function testConnection() {
    const provider = providerSelect.value;
    const apiKey = apiKeyInput.value;

    if (!apiKey) {
        alert('Please enter an API key');
        return;
    }

    // Show loading state
    testMcpConnection.disabled = true;
    testMcpConnection.textContent = 'Testing...';

    try {
        const response = await fetch('/api/v1/test-connection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                provider,
                api_key: apiKey
            })
        });

        if (!response.ok) {
            throw new Error('Connection test failed');
        }

        const data = await response.json();

        if (data.status === 'success') {
            alert(`Connection successful! Available models: ${data.models_available.join(', ')}`);

            // Update model options
            if (modelSelect && data.models_available && data.models_available.length > 0) {
                modelSelect.innerHTML = data.models_available.map(model =>
                    `<option value="${model}">${model}</option>`
                ).join('');

                // Select first model
                modelSelect.value = data.models_available[0];
            }
        } else {
            alert(data.message || 'Connection test failed');
        }

    } catch (error) {
        console.error('Error testing connection:', error);
        alert('Connection test failed. Please check your settings and try again.');
    } finally {
        // Reset button
        testMcpConnection.disabled = false;
        testMcpConnection.textContent = 'Test Connection';
    }
}

// Handle install extension
function handleInstallExtension() {
    const confirmed = confirm('This will open the browser extension store in a new tab. Continue?');

    if (confirmed) {
        alert('In a real implementation, this would redirect to the extension store');

        // Simulate successful installation
        setTimeout(() => {
            settings.extension_installed = true;
            updateSettingsUI();

            // Show success message
            addMessage({
                role: 'system',
                content: 'Browser extension installed successfully',
                timestamp: new Date().toISOString()
            });
        }, 1000);
    }
}

// Handle upgrade subscription
function handleUpgradeSubscription() {
    const confirmed = confirm('This will take you to the subscription upgrade page. Continue?');

    if (confirmed) {
        alert('In a real implementation, this would redirect to the subscription page');

        // Simulate successful upgrade
        setTimeout(() => {
            settings.subscription_tier = 'professional';
            updateSettingsUI();

            // Show success message
            addMessage({
                role: 'system',
                content: 'Subscription upgraded to Professional',
                timestamp: new Date().toISOString()
            });
        }, 1000);
    }
}

// Helper functions
function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight() {
    dropArea.classList.add('highlight');
}

function unhighlight() {
    dropArea.classList.remove('highlight');
}

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}
