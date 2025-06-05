// Relationship Therapist Assistant - Popup Script

class PopupManager {
    constructor() {
        this.isAuthenticated = false;
        this.user = null;
        this.stats = {
            conversations: 0,
            suggestions: 0,
            insights: 0
        };
        this.settings = {
            autoSuggestions: true,
            realTimeAnalysis: true,
            notifications: true
        };

        this.init();
    }

    async init() {
        await this.loadUserData();
        this.setupEventListeners();
        this.updateUI();
        this.loadStats();
        this.loadSettings();
        this.loadRecentActivity();
        this.checkConnectionStatus();
    }

    async loadUserData() {
        try {
            const result = await chrome.storage.local.get(['authToken', 'user']);
            if (result.authToken && result.user) {
                this.isAuthenticated = true;
                this.user = result.user;
            }
        } catch (error) {
            console.error('Error loading user data:', error);
        }
    }

    setupEventListeners() {
        // Auth form listeners
        const loginForm = document.getElementById('loginFormElement');
        const registerForm = document.getElementById('registerFormElement');
        const showRegisterForm = document.getElementById('showRegisterForm');
        const showLoginForm = document.getElementById('showLoginForm');
        const logoutBtn = document.getElementById('logoutBtn');

        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        if (registerForm) {
            registerForm.addEventListener('submit', (e) => this.handleRegister(e));
        }

        if (showRegisterForm) {
            showRegisterForm.addEventListener('click', (e) => {
                e.preventDefault();
                this.showRegisterForm();
            });
        }

        if (showLoginForm) {
            showLoginForm.addEventListener('click', (e) => {
                e.preventDefault();
                this.showLoginForm();
            });
        }

        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.handleLogout());
        }

        // Action button listeners
        const toggleAssistantBtn = document.getElementById('toggleAssistantBtn');
        const getSuggestionBtn = document.getElementById('getSuggestionBtn');
        const analyzeConversationBtn = document.getElementById('analyzeConversationBtn');
        const openDashboardBtn = document.getElementById('openDashboardBtn');

        if (toggleAssistantBtn) {
            toggleAssistantBtn.addEventListener('click', () => this.toggleAssistant());
        }

        if (getSuggestionBtn) {
            getSuggestionBtn.addEventListener('click', () => this.getSuggestion());
        }

        if (analyzeConversationBtn) {
            analyzeConversationBtn.addEventListener('click', () => this.analyzeConversation());
        }

        if (openDashboardBtn) {
            openDashboardBtn.addEventListener('click', () => this.openDashboard());
        }

        // Settings listeners
        const autoSuggestionsToggle = document.getElementById('autoSuggestionsToggle');
        const realTimeAnalysisToggle = document.getElementById('realTimeAnalysisToggle');
        const notificationsToggle = document.getElementById('notificationsToggle');

        if (autoSuggestionsToggle) {
            autoSuggestionsToggle.addEventListener('change', (e) => {
                this.updateSetting('autoSuggestions', e.target.checked);
            });
        }

        if (realTimeAnalysisToggle) {
            realTimeAnalysisToggle.addEventListener('change', (e) => {
                this.updateSetting('realTimeAnalysis', e.target.checked);
            });
        }

        if (notificationsToggle) {
            notificationsToggle.addEventListener('change', (e) => {
                this.updateSetting('notifications', e.target.checked);
            });
        }

        // Footer links
        const helpLink = document.getElementById('helpLink');
        const feedbackLink = document.getElementById('feedbackLink');

        if (helpLink) {
            helpLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.openHelp();
            });
        }

        if (feedbackLink) {
            feedbackLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.openFeedback();
            });
        }
    }

    updateUI() {
        const authSection = document.getElementById('authSection');
        const mainContent = document.getElementById('mainContent');

        if (this.isAuthenticated && this.user) {
            authSection.style.display = 'none';
            mainContent.style.display = 'block';
            this.updateUserInfo();
        } else {
            authSection.style.display = 'block';
            mainContent.style.display = 'none';
        }
    }

    updateUserInfo() {
        if (!this.user) return;

        const userInitials = document.getElementById('userInitials');
        const userName = document.getElementById('userName');
        const userRole = document.getElementById('userRole');

        if (userInitials) {
            const initials = this.user.email.substring(0, 2).toUpperCase();
            userInitials.textContent = initials;
        }

        if (userName) {
            userName.textContent = this.user.email.split('@')[0];
        }

        if (userRole) {
            userRole.textContent = this.user.role || 'user';
        }
    }

    showRegisterForm() {
        document.getElementById('loginForm').style.display = 'none';
        document.getElementById('registerForm').style.display = 'block';
    }

    showLoginForm() {
        document.getElementById('registerForm').style.display = 'none';
        document.getElementById('loginForm').style.display = 'block';
    }

    async handleLogin(event) {
        event.preventDefault();

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const loginBtn = document.getElementById('loginBtn');

        this.setButtonLoading(loginBtn, true);

        try {
            const response = await this.sendMessageToBackground({
                type: 'LOGIN',
                data: { email, password }
            });

            if (response.success) {
                this.isAuthenticated = true;
                this.user = response.user;
                this.updateUI();
                this.showMessage('Login successful!', 'success');
                this.loadStats();
            } else {
                this.showMessage(response.error || 'Login failed', 'error');
            }
        } catch (error) {
            console.error('Login error:', error);
            this.showMessage('Login failed. Please try again.', 'error');
        } finally {
            this.setButtonLoading(loginBtn, false);
        }
    }

    async handleRegister(event) {
        event.preventDefault();

        const email = document.getElementById('regEmail').value;
        const password = document.getElementById('regPassword').value;
        const confirmPassword = document.getElementById('regConfirmPassword').value;
        const role = document.getElementById('regRole').value;
        const registerBtn = document.getElementById('registerBtn');

        if (password !== confirmPassword) {
            this.showMessage('Passwords do not match', 'error');
            return;
        }

        this.setButtonLoading(registerBtn, true);

        try {
            const response = await this.sendMessageToBackground({
                type: 'REGISTER',
                data: { email, password, role }
            });

            if (response.success) {
                this.showMessage('Registration successful! Please login.', 'success');
                this.showLoginForm();
            } else {
                this.showMessage(response.error || 'Registration failed', 'error');
            }
        } catch (error) {
            console.error('Registration error:', error);
            this.showMessage('Registration failed. Please try again.', 'error');
        } finally {
            this.setButtonLoading(registerBtn, false);
        }
    }

    async handleLogout() {
        try {
            await this.sendMessageToBackground({ type: 'LOGOUT' });
            this.isAuthenticated = false;
            this.user = null;
            this.updateUI();
            this.showMessage('Logged out successfully', 'success');
        } catch (error) {
            console.error('Logout error:', error);
            this.showMessage('Logout failed', 'error');
        }
    }

    async toggleAssistant() {
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            await chrome.tabs.sendMessage(tab.id, { type: 'TOGGLE_ASSISTANT' });
            this.showMessage('Assistant toggled', 'info');
        } catch (error) {
            console.error('Toggle assistant error:', error);
            this.showMessage('Failed to toggle assistant', 'error');
        }
    }

    async getSuggestion() {
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            await chrome.tabs.sendMessage(tab.id, { type: 'GET_SUGGESTION' });
            this.showMessage('Getting suggestion...', 'info');
        } catch (error) {
            console.error('Get suggestion error:', error);
            this.showMessage('Failed to get suggestion', 'error');
        }
    }

    async analyzeConversation() {
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            await chrome.tabs.sendMessage(tab.id, { type: 'ANALYZE_CONVERSATION' });
            this.showMessage('Analyzing conversation...', 'info');
        } catch (error) {
            console.error('Analyze conversation error:', error);
            this.showMessage('Failed to analyze conversation', 'error');
        }
    }

    async openDashboard() {
        try {
            await chrome.tabs.create({ url: 'http://localhost:8000/dashboard' });
        } catch (error) {
            console.error('Open dashboard error:', error);
            this.showMessage('Failed to open dashboard', 'error');
        }
    }

    async openHelp() {
        try {
            await chrome.tabs.create({ url: 'http://localhost:8000/help' });
        } catch (error) {
            console.error('Open help error:', error);
        }
    }

    async openFeedback() {
        try {
            await chrome.tabs.create({ url: 'http://localhost:8000/feedback' });
        } catch (error) {
            console.error('Open feedback error:', error);
        }
    }

    async loadStats() {
        try {
            const response = await this.sendMessageToBackground({
                type: 'GET_STATS'
            });

            if (response.success) {
                this.stats = response.stats;
                this.updateStatsUI();
            }
        } catch (error) {
            console.error('Load stats error:', error);
        }
    }

    updateStatsUI() {
        const conversationsCount = document.getElementById('conversationsCount');
        const suggestionsCount = document.getElementById('suggestionsCount');
        const insightsCount = document.getElementById('insightsCount');

        if (conversationsCount) {
            conversationsCount.textContent = this.stats.conversations || 0;
        }

        if (suggestionsCount) {
            suggestionsCount.textContent = this.stats.suggestions || 0;
        }

        if (insightsCount) {
            insightsCount.textContent = this.stats.insights || 0;
        }
    }

    async loadSettings() {
        try {
            const result = await chrome.storage.local.get(['settings']);
            if (result.settings) {
                this.settings = { ...this.settings, ...result.settings };
            }
            this.updateSettingsUI();
        } catch (error) {
            console.error('Load settings error:', error);
        }
    }

    updateSettingsUI() {
        const autoSuggestionsToggle = document.getElementById('autoSuggestionsToggle');
        const realTimeAnalysisToggle = document.getElementById('realTimeAnalysisToggle');
        const notificationsToggle = document.getElementById('notificationsToggle');

        if (autoSuggestionsToggle) {
            autoSuggestionsToggle.checked = this.settings.autoSuggestions;
        }

        if (realTimeAnalysisToggle) {
            realTimeAnalysisToggle.checked = this.settings.realTimeAnalysis;
        }

        if (notificationsToggle) {
            notificationsToggle.checked = this.settings.notifications;
        }
    }

    async updateSetting(key, value) {
        this.settings[key] = value;
        try {
            await chrome.storage.local.set({ settings: this.settings });
            await this.sendMessageToBackground({
                type: 'UPDATE_SETTINGS',
                data: this.settings
            });
        } catch (error) {
            console.error('Update setting error:', error);
        }
    }

    async loadRecentActivity() {
        try {
            const response = await this.sendMessageToBackground({
                type: 'GET_RECENT_ACTIVITY'
            });

            if (response.success && response.activities) {
                this.updateActivityUI(response.activities);
            }
        } catch (error) {
            console.error('Load recent activity error:', error);
        }
    }

    updateActivityUI(activities) {
        const activityList = document.getElementById('activityList');
        if (!activityList) return;

        if (!activities || activities.length === 0) {
            activityList.innerHTML = `
                <div class="activity-item placeholder">
                    <span class="activity-icon">📝</span>
                    <span class="activity-text">No recent activity</span>
                    <span class="activity-time">-</span>
                </div>
            `;
            return;
        }

        activityList.innerHTML = activities.map(activity => `
            <div class="activity-item">
                <span class="activity-icon">${this.getActivityIcon(activity.type)}</span>
                <span class="activity-text">${activity.description}</span>
                <span class="activity-time">${this.formatTime(activity.timestamp)}</span>
            </div>
        `).join('');
    }

    getActivityIcon(type) {
        const icons = {
            suggestion: '💡',
            analysis: '📊',
            conversation: '💬',
            login: '🔐',
            upload: '📁'
        };
        return icons[type] || '📝';
    }

    formatTime(timestamp) {
        const now = new Date();
        const time = new Date(timestamp);
        const diff = now - time;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);

        if (minutes < 1) return 'now';
        if (minutes < 60) return `${minutes}m`;
        if (hours < 24) return `${hours}h`;
        return `${days}d`;
    }

    async checkConnectionStatus() {
        const statusIndicator = document.getElementById('statusIndicator');
        const statusDot = statusIndicator.querySelector('.status-dot');
        const statusText = statusIndicator.querySelector('.status-text');

        try {
            const response = await this.sendMessageToBackground({
                type: 'CHECK_CONNECTION'
            });

            if (response.connected) {
                statusDot.className = 'status-dot connected';
                statusText.textContent = 'Connected';
            } else {
                statusDot.className = 'status-dot disconnected';
                statusText.textContent = 'Disconnected';
            }
        } catch (error) {
            statusDot.className = 'status-dot disconnected';
            statusText.textContent = 'Disconnected';
        }
    }

    setButtonLoading(button, loading) {
        if (loading) {
            button.classList.add('loading');
            button.disabled = true;
        } else {
            button.classList.remove('loading');
            button.disabled = false;
        }
    }

    showMessage(text, type = 'info') {
        const messageContainer = document.getElementById('messageContainer');
        const messageText = document.getElementById('messageText');

        if (messageContainer && messageText) {
            messageText.textContent = text;
            messageContainer.className = `message ${type}`;
            messageContainer.style.display = 'block';

            setTimeout(() => {
                messageContainer.style.display = 'none';
            }, 3000);
        }
    }

    async sendMessageToBackground(message) {
        return new Promise((resolve, reject) => {
            chrome.runtime.sendMessage(message, (response) => {
                if (chrome.runtime.lastError) {
                    reject(chrome.runtime.lastError);
                } else {
                    resolve(response);
                }
            });
        });
    }
}

// Initialize popup when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PopupManager();
});