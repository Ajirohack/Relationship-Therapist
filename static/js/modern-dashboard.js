// Modern Dashboard JavaScript
class ModernDashboard {
    constructor() {
        this.currentSection = 'dashboard';
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadDashboardData();
        this.initializeCharts();
    }

    bindEvents() {
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const section = e.target.dataset.section;
                this.navigateToSection(section);
            });
        });

        // Hero actions
        document.getElementById('start-analysis')?.addEventListener('click', () => {
            this.navigateToSection('analysis');
        });

        document.getElementById('open-chat')?.addEventListener('click', () => {
            this.navigateToSection('chat');
        });

        // Quick analysis form
        document.getElementById('quick-analysis-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleQuickAnalysis();
        });

        // Chat form
        document.getElementById('chat-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleChatMessage();
        });

        // Analysis form
        document.getElementById('analyze-btn')?.addEventListener('click', () => {
            this.handleFullAnalysis();
        });

        // File upload
        document.getElementById('upload-area')?.addEventListener('click', () => {
            document.getElementById('file-input')?.click();
        });

        document.getElementById('file-input')?.addEventListener('change', (e) => {
            this.handleFileUpload(e.target.files[0]);
        });

        // Drag and drop
        const uploadArea = document.getElementById('upload-area');
        if (uploadArea) {
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.style.borderColor = 'var(--primary)';
            });

            uploadArea.addEventListener('dragleave', () => {
                uploadArea.style.borderColor = 'var(--border)';
            });

            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.style.borderColor = 'var(--border)';
                const file = e.dataTransfer.files[0];
                this.handleFileUpload(file);
            });
        }
    }

    navigateToSection(section) {
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`)?.classList.add('active');

        // Update sections
        document.querySelectorAll('.section').forEach(sec => {
            sec.classList.remove('active');
        });
        document.getElementById(`${section}-section`)?.classList.add('active');

        this.currentSection = section;
    }

    async loadDashboardData() {
        try {
            const response = await fetch('/api/v1/user/stats');
            if (response.ok) {
                const data = await response.json();
                this.updateStats(data);
            }
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }

        // Load recent activity
        this.loadRecentActivity();
    }

    updateStats(data) {
        document.getElementById('total-analyses').textContent = data.total_analyses || 0;
        document.getElementById('avg-sentiment').textContent = data.avg_sentiment || '-';
        document.getElementById('total-reports').textContent = data.total_reports || 0;
        document.getElementById('success-rate').textContent = data.success_rate || '-';
    }

    async loadRecentActivity() {
        try {
            const response = await fetch('/api/v1/user/sessions');
            if (response.ok) {
                const data = await response.json();
                this.updateRecentActivity(data.sessions || []);
            }
        } catch (error) {
            console.error('Error loading recent activity:', error);
        }
    }

    updateRecentActivity(sessions) {
        const container = document.getElementById('recent-activity');
        if (!container) return;

        if (sessions.length === 0) {
            container.innerHTML = `
                <div class="activity-item">
                    <div class="activity-icon">📊</div>
                    <div class="activity-content">
                        <div class="activity-title">Welcome to Core Engine</div>
                        <div class="activity-time">Start your first analysis</div>
                    </div>
                </div>
            `;
            return;
        }

        container.innerHTML = sessions.map(session => `
            <div class="activity-item">
                <div class="activity-icon">📊</div>
                <div class="activity-content">
                    <div class="activity-title">${session.title || 'Analysis Session'}</div>
                    <div class="activity-time">${this.formatDate(session.created_at)}</div>
                </div>
            </div>
        `).join('');
    }

    async handleQuickAnalysis() {
        const input = document.getElementById('conversation-input');
        const text = input.value.trim();

        if (!text) {
            this.showError('Please enter a conversation to analyze');
            return;
        }

        this.showLoading('Analyzing conversation...');

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ conversation: text })
            });

            if (response.ok) {
                const data = await response.json();
                this.displayQuickResults(data);
                input.value = '';
            } else {
                throw new Error('Analysis failed');
            }
        } catch (error) {
            console.error('Error analyzing conversation:', error);
            this.showError('Failed to analyze conversation. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    displayQuickResults(data) {
        // Add to recent activity
        const activityContainer = document.getElementById('recent-activity');
        const newActivity = document.createElement('div');
        newActivity.className = 'activity-item';
        newActivity.innerHTML = `
            <div class="activity-icon">📊</div>
            <div class="activity-content">
                <div class="activity-title">Quick Analysis Completed</div>
                <div class="activity-time">Just now</div>
            </div>
        `;
        activityContainer.insertBefore(newActivity, activityContainer.firstChild);

        // Update stats
        const totalAnalyses = document.getElementById('total-analyses');
        const current = parseInt(totalAnalyses.textContent) || 0;
        totalAnalyses.textContent = current + 1;

        // Show success message
        this.showSuccess('Analysis completed successfully!');
    }

    async handleChatMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();

        if (!message) return;

        // Add user message
        this.addChatMessage(message, 'user');
        input.value = '';

        // Show typing indicator
        this.addTypingIndicator();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });

            if (response.ok) {
                const data = await response.json();
                this.removeTypingIndicator();
                this.addChatMessage(data.response, 'ai');
            } else {
                throw new Error('Chat request failed');
            }
        } catch (error) {
            console.error('Error sending chat message:', error);
            this.removeTypingIndicator();
            this.addChatMessage('Sorry, I encountered an error. Please try again.', 'ai');
        }
    }

    addChatMessage(message, sender) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const avatar = sender === 'ai' ? '🤖' : '👤';
        
        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                <div class="message-text">${message}</div>
            </div>
        `;

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    addTypingIndicator() {
        const messagesContainer = document.getElementById('chat-messages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message ai-message typing-indicator';
        typingDiv.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <div class="message-text">Typing...</div>
            </div>
        `;
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    removeTypingIndicator() {
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    async handleFullAnalysis() {
        const input = document.getElementById('analysis-input');
        const text = input.value.trim();

        if (!text) {
            this.showError('Please enter a conversation to analyze');
            return;
        }

        this.showLoading('Performing detailed analysis...');

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ conversation: text })
            });

            if (response.ok) {
                const data = await response.json();
                this.displayFullResults(data);
            } else {
                throw new Error('Analysis failed');
            }
        } catch (error) {
            console.error('Error analyzing conversation:', error);
            this.showError('Failed to analyze conversation. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    displayFullResults(data) {
        const resultsContainer = document.getElementById('analysis-results');
        resultsContainer.classList.remove('hidden');

        // Update sentiment chart
        this.updateSentimentChart(data.sentiment);

        // Update communication insights
        const communicationDiv = document.getElementById('communication-insights');
        communicationDiv.innerHTML = `
            <div class="insight-item">
                <strong>Communication Style:</strong> ${data.communication?.style || 'Balanced'}
            </div>
            <div class="insight-item">
                <strong>Tone:</strong> ${data.communication?.tone || 'Neutral'}
            </div>
            <div class="insight-item">
                <strong>Engagement Level:</strong> ${data.communication?.engagement || 'Moderate'}
            </div>
        `;

        // Update health score
        const healthDiv = document.getElementById('health-score');
        const score = data.relationship_health?.overall_score || 75;
        healthDiv.innerHTML = `
            <div class="health-score-display">
                <div class="score-circle">
                    <span class="score-value">${score}%</span>
                </div>
                <div class="score-label">Overall Health</div>
            </div>
        `;

        // Update recommendations
        const recommendationsDiv = document.getElementById('recommendations');
        const recommendations = data.recommendations || ['Continue positive communication patterns'];
        recommendationsDiv.innerHTML = recommendations.map(rec => `
            <div class="recommendation-item">• ${rec}</div>
        `).join('');

        this.showSuccess('Detailed analysis completed!');
    }

    handleFileUpload(file) {
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            const content = e.target.result;
            document.getElementById('analysis-input').value = content;
            this.showSuccess('File uploaded successfully!');
        };
        reader.readAsText(file);
    }

    initializeCharts() {
        // Initialize empty sentiment chart
        const ctx = document.getElementById('sentiment-chart');
        if (ctx) {
            this.sentimentChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Positive', 'Neutral', 'Negative'],
                    datasets: [{
                        data: [0, 0, 0],
                        backgroundColor: ['#10b981', '#64748b', '#ef4444']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
    }

    updateSentimentChart(sentimentData) {
        if (this.sentimentChart && sentimentData) {
            const positive = sentimentData.positive || 0;
            const neutral = sentimentData.neutral || 0;
            const negative = sentimentData.negative || 0;
            
            this.sentimentChart.data.datasets[0].data = [positive, neutral, negative];
            this.sentimentChart.update();
        }
    }

    showLoading(message = 'Loading...') {
        const overlay = document.getElementById('loading-overlay');
        const text = document.querySelector('.loading-text');
        if (overlay && text) {
            text.textContent = message;
            overlay.classList.remove('hidden');
        }
    }

    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.add('hidden');
        }
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 16px 24px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 1001;
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;
        
        if (type === 'success') {
            notification.style.background = 'var(--success)';
        } else if (type === 'error') {
            notification.style.background = 'var(--error)';
        } else {
            notification.style.background = 'var(--primary)';
        }
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
        return date.toLocaleDateString();
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ModernDashboard();
});