/**
 * Core Engine Relationship Therapist - Knowledge Base
 * Handles knowledge base article listing, filtering, and rendering
 */

// DOM Elements
const kbSearchInput = document.getElementById('kb-search');
const kbSearchBtn = document.getElementById('kb-search-btn');
const kbCategoryItems = document.querySelectorAll('.kb-category-item');
const kbArticlesContainer = document.getElementById('kb-articles');
const kbLoading = document.getElementById('kb-loading');
const kbArticleList = document.getElementById('kb-article-list');
const kbArticleDetail = document.getElementById('kb-article-detail');
const kbArticleContent = document.getElementById('kb-article-content');
const kbArticleTags = document.getElementById('kb-article-tags');
const kbBackBtn = document.getElementById('kb-back-btn');
const kbPrintBtn = document.getElementById('kb-print-btn');
const kbShareBtn = document.getElementById('kb-share-btn');
const kbSaveBtn = document.getElementById('kb-save-btn');
const kbHelpfulYes = document.getElementById('kb-helpful-yes');
const kbHelpfulNo = document.getElementById('kb-helpful-no');
const kbRecentList = document.getElementById('kb-recent-list');

// Settings Panel Elements
const settingsToggle = document.getElementById('settings-toggle');
const closeSettings = document.getElementById('close-settings');
const settingsPanel = document.getElementById('settings-panel');
const saveSettings = document.getElementById('save-settings');
const cancelSettings = document.getElementById('cancel-settings');
const providerSelect = document.getElementById('provider-select');
const modelSelect = document.getElementById('model-select');
const apiKeyInput = document.getElementById('api-key');
const toggleKey = document.getElementById('toggle-key');
const kbFormatSelect = document.getElementById('kb-format');
const customKbContainer = document.getElementById('custom-kb-container');
const testMcpConnection = document.getElementById('test-mcp-connection');
const installExtension = document.getElementById('install-extension');
const extensionStatus = document.getElementById('extension-status');
const upgradeSubscription = document.getElementById('upgrade-subscription');

// State variables
let currentCategory = 'all';
let articles = [];
let recentArticles = [];
let settings = {
    ai_provider: {
        provider: 'openai',
        model: 'gpt-4',
        api_key: ''
    },
    knowledge_base_format: 'default',
    subscription_tier: 'free',
    extension_installed: false
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Load articles
    fetchArticles();

    // Load settings
    fetchSettings();

    // Initialize event listeners
    initEventListeners();
});

// Fetch articles from API
async function fetchArticles(category = null) {
    showLoading();

    try {
        let url = '/api/v1/knowledge-base/articles';
        if (category && category !== 'all') {
            url += `?category=${category}`;
        }

        const response = await fetch(url);
        const data = await response.json();

        articles = data.articles;
        renderArticles(articles);

    } catch (error) {
        console.error('Error fetching articles:', error);
        showError('Failed to load knowledge base articles. Please try again.');
    } finally {
        hideLoading();
    }
}

// Fetch article by ID
async function fetchArticle(articleId) {
    showLoading();

    try {
        const response = await fetch(`/api/v1/knowledge-base/article/${articleId}`);

        if (!response.ok) {
            throw new Error('Article not found');
        }

        const article = await response.json();
        renderArticleDetail(article);

        // Add to recent articles
        addToRecentArticles(article);

    } catch (error) {
        console.error('Error fetching article:', error);
        showError('Failed to load article. Please try again.');
        showArticleList();
    } finally {
        hideLoading();
    }
}

// Render article list
function renderArticles(articles) {
    if (!kbArticlesContainer) return;

    if (articles.length === 0) {
        kbArticlesContainer.innerHTML = `
            <div class="empty-state">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
                </svg>
                <p>No articles found. Try a different search or category.</p>
            </div>
        `;
        return;
    }

    const html = articles.map(article => `
        <div class="kb-article-card" data-id="${article.id}">
            <h3 class="kb-article-title">${article.title}</h3>
            <p class="kb-article-summary">${article.summary}</p>
            <div class="kb-article-meta">
                <span class="kb-article-category">${formatCategory(article.category)}</span>
                <span class="kb-article-reading">${article.read_time}</span>
            </div>
        </div>
    `).join('');

    kbArticlesContainer.innerHTML = html;

    // Add click event listeners
    document.querySelectorAll('.kb-article-card').forEach(card => {
        card.addEventListener('click', () => {
            const articleId = card.dataset.id;
            fetchArticle(articleId);
        });
    });
}

// Render article detail
function renderArticleDetail(article) {
    if (!kbArticleContent || !kbArticleTags) return;

    // Hide article list, show article detail
    kbArticleList.style.display = 'none';
    kbArticleDetail.style.display = 'block';

    // Render content using marked.js for markdown
    kbArticleContent.innerHTML = marked.parse(article.content || '');

    // Render tags
    if (article.tags && article.tags.length > 0) {
        const tagsHtml = article.tags.map(tag => `
            <span class="kb-tag">${tag}</span>
        `).join('');

        kbArticleTags.innerHTML = tagsHtml;
    } else {
        kbArticleTags.innerHTML = '<span class="kb-tag">No tags</span>';
    }
}

// Show article list, hide article detail
function showArticleList() {
    if (!kbArticleList || !kbArticleDetail) return;

    kbArticleList.style.display = 'block';
    kbArticleDetail.style.display = 'none';
}

// Format category for display
function formatCategory(category) {
    if (!category) return 'Uncategorized';

    return category
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

// Add to recent articles
function addToRecentArticles(article) {
    if (!kbRecentList) return;

    // Check if already in recent
    const existingIndex = recentArticles.findIndex(a => a.id === article.id);
    if (existingIndex > -1) {
        // Remove from current position
        recentArticles.splice(existingIndex, 1);
    }

    // Add to beginning
    recentArticles.unshift({
        id: article.id,
        title: article.title,
        category: article.category
    });

    // Keep only the last 5
    recentArticles = recentArticles.slice(0, 5);

    // Save to localStorage
    localStorage.setItem('kb_recent_articles', JSON.stringify(recentArticles));

    // Render recent articles
    renderRecentArticles();
}

// Render recent articles
function renderRecentArticles() {
    if (!kbRecentList) return;

    if (recentArticles.length === 0) {
        kbRecentList.innerHTML = '<li class="text-muted">No recent articles</li>';
        return;
    }

    const html = recentArticles.map(article => `
        <li class="kb-recent-item" data-id="${article.id}">
            <div class="kb-recent-title">${article.title}</div>
            <div class="kb-recent-category">${formatCategory(article.category)}</div>
        </li>
    `).join('');

    kbRecentList.innerHTML = html;

    // Add click event listeners
    document.querySelectorAll('.kb-recent-item').forEach(item => {
        item.addEventListener('click', () => {
            const articleId = item.dataset.id;
            fetchArticle(articleId);
        });
    });
}

// Show loading state
function showLoading() {
    if (kbLoading) {
        kbLoading.style.display = 'flex';
    }
}

// Hide loading state
function hideLoading() {
    if (kbLoading) {
        kbLoading.style.display = 'none';
    }
}

// Show error message
function showError(message) {
    // Implementation depends on your UI design
    console.error(message);
    alert(message);
}

// Fetch user settings
async function fetchSettings() {
    try {
        const response = await fetch('/api/v1/settings');
        const data = await response.json();

        settings = data;

        // Update UI
        updateSettingsUI();

    } catch (error) {
        console.error('Error fetching settings:', error);
    }
}

// Update settings UI
function updateSettingsUI() {
    if (!providerSelect || !modelSelect || !apiKeyInput || !kbFormatSelect) return;

    // Set provider and model
    providerSelect.value = settings.ai_provider.provider;
    modelSelect.value = settings.ai_provider.model;

    // Set API key (masked)
    apiKeyInput.value = settings.ai_provider.api_key || '';

    // Set KB format
    kbFormatSelect.value = settings.knowledge_base_format;

    // Show/hide custom KB container
    if (settings.knowledge_base_format === 'custom') {
        customKbContainer.classList.remove('hidden');
    } else {
        customKbContainer.classList.add('hidden');
    }

    // Update extension status
    if (settings.extension_installed) {
        extensionStatus.className = 'status-indicator status-success';
        extensionStatus.innerHTML = '<span class="status-dot"></span>Extension installed';
    } else {
        extensionStatus.className = 'status-indicator status-warning';
        extensionStatus.innerHTML = '<span class="status-dot"></span>Extension not installed';
    }

    // Update subscription tier
    const tierBadge = document.querySelector('.subscription-tier .tier-badge');
    if (tierBadge) {
        tierBadge.className = `tier-badge ${settings.subscription_tier}`;
        tierBadge.textContent = capitalizeFirstLetter(settings.subscription_tier);
    }
}

// Capitalize first letter
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

// Save settings
async function saveUserSettings() {
    // Gather settings from UI
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

        const data = await response.json();

        if (data.status === 'success') {
            settings = data.settings;
            updateSettingsUI();
            toggleSettingsPanel();
            alert('Settings saved successfully');
        } else {
            throw new Error(data.message || 'Failed to save settings');
        }

    } catch (error) {
        console.error('Error saving settings:', error);
        showError('Failed to save settings. Please try again.');
    }
}

// Test MCP connection
async function testMcpConnectionHandler() {
    const provider = providerSelect.value;
    const apiKey = apiKeyInput.value;

    if (!apiKey) {
        showError('Please enter an API key');
        return;
    }

    try {
        const button = testMcpConnection;
        const originalText = button.textContent;

        button.textContent = 'Testing...';
        button.disabled = true;

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

        const data = await response.json();

        if (data.status === 'success') {
            alert(`Connection successful! Available models: ${data.models_available.join(', ')}`);

            // Update model options if needed
            if (data.models_available && data.models_available.length > 0) {
                modelSelect.innerHTML = data.models_available.map(model =>
                    `<option value="${model}">${model}</option>`
                ).join('');

                // Select first model
                modelSelect.value = data.models_available[0];
            }
        } else {
            showError(data.message || 'Connection test failed');
        }

        button.textContent = originalText;
        button.disabled = false;

    } catch (error) {
        console.error('Error testing connection:', error);
        showError('Connection test failed. Please check your settings and try again.');

        testMcpConnection.textContent = 'Test Connection';
        testMcpConnection.disabled = false;
    }
}

// Toggle settings panel
function toggleSettingsPanel() {
    if (!settingsPanel) return;

    settingsPanel.classList.toggle('hidden');
}

// Update knowledge base format
async function updateKnowledgeBaseFormat(format) {
    try {
        const response = await fetch('/api/v1/knowledge-base/format', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ format })
        });

        const data = await response.json();

        if (data.status === 'success') {
            alert(`Knowledge base format updated to ${format}`);

            // Refresh articles
            fetchArticles(currentCategory);
        } else {
            throw new Error(data.message || 'Failed to update knowledge base format');
        }

    } catch (error) {
        console.error('Error updating KB format:', error);
        showError('Failed to update knowledge base format. Please try again.');
    }
}

// Initialize event listeners
function initEventListeners() {
    // Search
    if (kbSearchBtn) {
        kbSearchBtn.addEventListener('click', () => {
            const query = kbSearchInput.value.trim();
            if (query) {
                // In a real app, you would call an API endpoint with the search query
                // For now, we'll just filter the existing articles
                const filtered = articles.filter(article =>
                    article.title.toLowerCase().includes(query.toLowerCase()) ||
                    article.summary.toLowerCase().includes(query.toLowerCase())
                );
                renderArticles(filtered);
            }
        });
    }

    if (kbSearchInput) {
        kbSearchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                kbSearchBtn.click();
            }
        });
    }

    // Category filters
    kbCategoryItems.forEach(item => {
        item.addEventListener('click', () => {
            // Update active class
            kbCategoryItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');

            // Get category
            const category = item.dataset.category;
            currentCategory = category;

            // Fetch articles
            fetchArticles(category);
        });
    });

    // Back button
    if (kbBackBtn) {
        kbBackBtn.addEventListener('click', showArticleList);
    }

    // Print button
    if (kbPrintBtn) {
        kbPrintBtn.addEventListener('click', () => {
            window.print();
        });
    }

    // Share button
    if (kbShareBtn) {
        kbShareBtn.addEventListener('click', () => {
            // In a real app, implement sharing functionality
            alert('Sharing functionality would be implemented here');
        });
    }

    // Save button
    if (kbSaveBtn) {
        kbSaveBtn.addEventListener('click', () => {
            // In a real app, implement saving/bookmarking
            alert('Article saved to your bookmarks');
        });
    }

    // Helpful feedback
    if (kbHelpfulYes) {
        kbHelpfulYes.addEventListener('click', () => {
            alert('Thank you for your feedback!');
            kbHelpfulYes.disabled = true;
            kbHelpfulNo.disabled = true;
        });
    }

    if (kbHelpfulNo) {
        kbHelpfulNo.addEventListener('click', () => {
            alert('Thank you for your feedback. We\'ll work on improving this article.');
            kbHelpfulYes.disabled = true;
            kbHelpfulNo.disabled = true;
        });
    }

    // Settings panel
    if (settingsToggle) {
        settingsToggle.addEventListener('click', toggleSettingsPanel);
    }

    if (closeSettings) {
        closeSettings.addEventListener('click', toggleSettingsPanel);
    }

    if (cancelSettings) {
        cancelSettings.addEventListener('click', toggleSettingsPanel);
    }

    if (saveSettings) {
        saveSettings.addEventListener('click', saveUserSettings);
    }

    // Toggle API key visibility
    if (toggleKey) {
        toggleKey.addEventListener('click', () => {
            const type = apiKeyInput.type;
            apiKeyInput.type = type === 'password' ? 'text' : 'password';
        });
    }

    // Knowledge base format change
    if (kbFormatSelect) {
        kbFormatSelect.addEventListener('change', () => {
            const format = kbFormatSelect.value;

            // Show/hide custom KB container
            if (format === 'custom') {
                customKbContainer.classList.remove('hidden');
            } else {
                customKbContainer.classList.add('hidden');
            }
        });
    }

    // Test connection
    if (testMcpConnection) {
        testMcpConnection.addEventListener('click', testMcpConnectionHandler);
    }

    // Install extension
    if (installExtension) {
        installExtension.addEventListener('click', () => {
            // In a real app, this would redirect to the extension store or download page
            const confirmed = confirm('This will open the browser extension store in a new tab. Continue?');

            if (confirmed) {
                alert('In a real implementation, this would redirect to the extension store');

                // Simulate successful installation
                setTimeout(() => {
                    settings.extension_installed = true;
                    updateSettingsUI();
                }, 1000);
            }
        });
    }

    // Upgrade subscription
    if (upgradeSubscription) {
        upgradeSubscription.addEventListener('click', () => {
            // In a real app, this would open a payment/upgrade page
            const confirmed = confirm('This will take you to the subscription upgrade page. Continue?');

            if (confirmed) {
                alert('In a real implementation, this would redirect to the subscription page');

                // Simulate successful upgrade
                setTimeout(() => {
                    settings.subscription_tier = 'professional';
                    updateSettingsUI();
                }, 1000);
            }
        });
    }
}

// Load recent articles from localStorage
function loadRecentArticles() {
    const saved = localStorage.getItem('kb_recent_articles');

    if (saved) {
        try {
            recentArticles = JSON.parse(saved) || [];
            renderRecentArticles();
        } catch (error) {
            console.error('Error parsing recent articles:', error);
            recentArticles = [];
        }
    }
}

// Call loadRecentArticles on init
loadRecentArticles();
