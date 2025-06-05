// Admin Dashboard JavaScript
class AdminDashboard {
    constructor() {
        this.currentSection = 'overview';
        this.charts = {};
        this.users = [];
        this.sessions = [];
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadInitialData();
        this.initializeCharts();
    }

    bindEvents() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = e.target.dataset.section;
                this.navigateToSection(section);
            });
        });

        // User management
        document.getElementById('add-user-btn')?.addEventListener('click', () => {
            this.showUserModal();
        });

        document.getElementById('user-search')?.addEventListener('input', (e) => {
            this.filterUsers(e.target.value);
        });

        // Session filtering
        document.getElementById('session-filter')?.addEventListener('change', (e) => {
            this.filterSessions(e.target.value);
        });

        // Modal events
        document.getElementById('cancel-user')?.addEventListener('click', () => {
            this.hideUserModal();
        });

        document.getElementById('save-user')?.addEventListener('click', () => {
            this.saveUser();
        });

        document.querySelector('.modal-close')?.addEventListener('click', () => {
            this.hideUserModal();
        });

        // System actions
        document.querySelectorAll('.config-actions .btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.handleSystemAction(e.target.textContent.trim());
            });
        });

        // Chart period change
        document.getElementById('activity-period')?.addEventListener('change', (e) => {
            this.updateActivityChart(e.target.value);
        });
    }

    navigateToSection(section) {
        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`)?.classList.add('active');

        // Update sections
        document.querySelectorAll('.admin-section').forEach(sec => {
            sec.classList.remove('active');
        });
        document.getElementById(`${section}-section`)?.classList.add('active');

        this.currentSection = section;

        // Load section-specific data
        this.loadSectionData(section);
    }

    async loadInitialData() {
        try {
            await Promise.all([
                this.loadMetrics(),
                this.loadUsers(),
                this.loadSessions(),
                this.loadSystemHealth()
            ]);
        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.showNotification('Failed to load dashboard data', 'error');
        }
    }

    async loadMetrics() {
        try {
            const response = await fetch('/api/v1/admin/stats', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const metrics = await response.json();

            document.getElementById('total-users').textContent = metrics.total_users?.toLocaleString() || '0';
            document.getElementById('active-sessions').textContent = metrics.active_sessions || '0';
            document.getElementById('total-analyses').textContent = metrics.total_analyses?.toLocaleString() || '0';
            document.getElementById('avg-rating').textContent = metrics.avg_rating || '0.0';
        } catch (error) {
            console.error('Failed to load metrics:', error);
            this.showNotification('Failed to load system metrics', 'error');
        }
    }

    async loadUsers() {
        try {
            const response = await fetch('/api/v1/admin/users', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.users = data.users || [];

            this.renderUsers();
        } catch (error) {
            console.error('Failed to load users:', error);
            this.showNotification('Failed to load users', 'error');
        }
    }

    async loadSessions() {
        try {
            const response = await fetch('/api/v1/admin/sessions', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.sessions = data.sessions || [];

            this.renderSessions();
        } catch (error) {
            console.error('Failed to load sessions:', error);
            this.showNotification('Failed to load sessions', 'error');
        }
    }

    async loadSystemHealth() {
        try {
            // For now, we'll use the stats endpoint to get system health info
            const response = await fetch('/api/v1/admin/stats', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const stats = await response.json();

            // Determine health status based on stats
            const health = {
                api: 'online', // If we got a response, API is online
                database: stats.total_users !== undefined ? 'online' : 'offline',
                aiService: 'online', // Assume online if stats are available
                cache: 'online'
            };

            // Update health indicators
            // This would be implemented based on actual health check endpoints
        } catch (error) {
            console.error('Failed to load system health:', error);
        }
    }

    renderUsers() {
        const tbody = document.getElementById('users-tbody');
        if (!tbody) return;

        tbody.innerHTML = this.users.map(user => `
            <tr>
                <td>
                    <div class="user-info">
                        <div class="user-avatar">${user.username.charAt(0).toUpperCase()}</div>
                        <div>
                            <div class="user-name">${user.username}</div>
                            <div class="user-id">#${user.id}</div>
                        </div>
                    </div>
                </td>
                <td>${user.email}</td>
                <td><span class="role-badge ${user.role}">${user.role}</span></td>
                <td><span class="status-badge ${user.status}">${user.status}</span></td>
                <td>${this.formatDate(user.lastLogin)}</td>
                <td>${user.sessions}</td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="adminDashboard.editUser('${user.id}')">Edit</button>
                    <button class="btn btn-sm btn-danger" onclick="adminDashboard.deleteUser('${user.id}')">Delete</button>
                </td>
            </tr>
        `).join('');
    }

    renderSessions() {
        const grid = document.getElementById('sessions-grid');
        if (!grid) return;

        grid.innerHTML = this.sessions.map(session => `
            <div class="session-card">
                <div class="session-header">
                    <h4 class="session-title">${session.title}</h4>
                    <span class="session-status ${session.status}">${session.status}</span>
                </div>
                <div class="session-meta">
                    <div>User: ${session.user}</div>
                    <div>Created: ${this.formatDate(session.createdAt)}</div>
                    <div>Messages: ${session.messages}</div>
                </div>
                <div class="session-actions">
                    <button class="btn btn-sm btn-primary" onclick="adminDashboard.viewSession('${session.id}')">View</button>
                    <button class="btn btn-sm btn-secondary" onclick="adminDashboard.exportSession('${session.id}')">Export</button>
                </div>
            </div>
        `).join('');
    }

    initializeCharts() {
        this.initActivityChart();
        this.initSessionChart();
        this.initAnalyticsCharts();
    }

    initActivityChart() {
        const ctx = document.getElementById('activity-chart');
        if (!ctx) return;

        this.charts.activity = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Active Users',
                    data: [65, 78, 90, 81, 95, 72, 68],
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#f8fafc'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: '#94a3b8'
                        },
                        grid: {
                            color: '#334155'
                        }
                    },
                    y: {
                        ticks: {
                            color: '#94a3b8'
                        },
                        grid: {
                            color: '#334155'
                        }
                    }
                }
            }
        });
    }

    initSessionChart() {
        const ctx = document.getElementById('session-chart');
        if (!ctx) return;

        this.charts.session = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Active', 'Completed', 'Pending'],
                datasets: [{
                    data: [45, 35, 20],
                    backgroundColor: ['#10b981', '#2563eb', '#f59e0b'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#f8fafc',
                            padding: 20
                        }
                    }
                }
            }
        });
    }

    initAnalyticsCharts() {
        // Trust Scores Chart
        const trustCtx = document.getElementById('trust-scores-chart');
        if (trustCtx) {
            this.charts.trust = new Chart(trustCtx, {
                type: 'bar',
                data: {
                    labels: ['Very Low', 'Low', 'Medium', 'High', 'Very High'],
                    datasets: [{
                        label: 'Trust Scores',
                        data: [5, 15, 35, 30, 15],
                        backgroundColor: '#10b981'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: {
                                color: '#f8fafc'
                            }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { color: '#94a3b8' },
                            grid: { color: '#334155' }
                        },
                        y: {
                            ticks: { color: '#94a3b8' },
                            grid: { color: '#334155' }
                        }
                    }
                }
            });
        }

        // Communication Chart
        const commCtx = document.getElementById('communication-chart');
        if (commCtx) {
            this.charts.communication = new Chart(commCtx, {
                type: 'radar',
                data: {
                    labels: ['Clarity', 'Empathy', 'Responsiveness', 'Conflict Resolution', 'Active Listening'],
                    datasets: [{
                        label: 'Average Scores',
                        data: [8.2, 7.8, 8.5, 7.2, 8.9],
                        borderColor: '#2563eb',
                        backgroundColor: 'rgba(37, 99, 235, 0.1)'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: {
                                color: '#f8fafc'
                            }
                        }
                    },
                    scales: {
                        r: {
                            ticks: {
                                color: '#94a3b8'
                            },
                            grid: {
                                color: '#334155'
                            },
                            pointLabels: {
                                color: '#f8fafc'
                            }
                        }
                    }
                }
            });
        }
    }

    filterUsers(query) {
        const filteredUsers = this.users.filter(user =>
            user.username.toLowerCase().includes(query.toLowerCase()) ||
            user.email.toLowerCase().includes(query.toLowerCase())
        );

        // Re-render with filtered users
        const tbody = document.getElementById('users-tbody');
        if (!tbody) return;

        tbody.innerHTML = filteredUsers.map(user => `
            <tr>
                <td>
                    <div class="user-info">
                        <div class="user-avatar">${user.username.charAt(0).toUpperCase()}</div>
                        <div>
                            <div class="user-name">${user.username}</div>
                            <div class="user-id">#${user.id}</div>
                        </div>
                    </div>
                </td>
                <td>${user.email}</td>
                <td><span class="role-badge ${user.role}">${user.role}</span></td>
                <td><span class="status-badge ${user.status}">${user.status}</span></td>
                <td>${this.formatDate(user.lastLogin)}</td>
                <td>${user.sessions}</td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="adminDashboard.editUser('${user.id}')">Edit</button>
                    <button class="btn btn-sm btn-danger" onclick="adminDashboard.deleteUser('${user.id}')">Delete</button>
                </td>
            </tr>
        `).join('');
    }

    filterSessions(status) {
        const filteredSessions = status === 'all' ?
            this.sessions :
            this.sessions.filter(session => session.status === status);

        const grid = document.getElementById('sessions-grid');
        if (!grid) return;

        grid.innerHTML = filteredSessions.map(session => `
            <div class="session-card">
                <div class="session-header">
                    <h4 class="session-title">${session.title}</h4>
                    <span class="session-status ${session.status}">${session.status}</span>
                </div>
                <div class="session-meta">
                    <div>User: ${session.user}</div>
                    <div>Created: ${this.formatDate(session.createdAt)}</div>
                    <div>Messages: ${session.messages}</div>
                </div>
                <div class="session-actions">
                    <button class="btn btn-sm btn-primary" onclick="adminDashboard.viewSession('${session.id}')">View</button>
                    <button class="btn btn-sm btn-secondary" onclick="adminDashboard.exportSession('${session.id}')">Export</button>
                </div>
            </div>
        `).join('');
    }

    showUserModal(userId = null) {
        const modal = document.getElementById('user-modal');
        const title = document.getElementById('user-modal-title');
        const passwordField = document.getElementById('user-password');

        if (userId) {
            title.textContent = 'Edit User';
            modal.dataset.userId = userId;
            // Load user data for editing
            const user = this.users.find(u => u.id === userId);
            if (user) {
                document.getElementById('user-email').value = user.email;
                document.getElementById('user-username').value = user.username;
                document.getElementById('user-role').value = user.role;
                // Make password optional for editing
                passwordField.placeholder = 'Leave blank to keep current password';
                passwordField.required = false;
            }
        } else {
            title.textContent = 'Add User';
            delete modal.dataset.userId;
            // Clear form
            document.getElementById('user-form').reset();
            passwordField.placeholder = 'Password';
            passwordField.required = true;
        }

        modal.classList.add('active');
    }

    hideUserModal() {
        const modal = document.getElementById('user-modal');
        modal.classList.remove('active');
    }

    async saveUser() {
        const email = document.getElementById('user-email').value;
        const username = document.getElementById('user-username').value;
        const role = document.getElementById('user-role').value;
        const password = document.getElementById('user-password').value;
        const userId = document.getElementById('user-modal').dataset.userId;

        if (!email || !username || (!password && !userId)) {
            this.showNotification('Please fill in all required fields', 'error');
            return;
        }

        try {
            const userData = {
                email,
                username,
                role
            };

            if (password) {
                userData.password = password;
            }

            let response;
            if (userId) {
                // Update existing user
                response = await fetch(`/api/v1/admin/users/${userId}`, {
                    method: 'PUT',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(userData)
                });
            } else {
                // Create new user - this would need a separate endpoint
                this.showNotification('User creation endpoint not implemented', 'error');
                return;
            }

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            await this.loadUsers(); // Reload users list
            this.hideUserModal();
            this.showNotification(result.message || 'User saved successfully', 'success');
        } catch (error) {
            console.error('Failed to save user:', error);
            this.showNotification('Failed to save user', 'error');
        }
    }

    editUser(userId) {
        this.showUserModal(userId);
    }

    async deleteUser(userId) {
        if (!confirm('Are you sure you want to delete this user?')) {
            return;
        }

        try {
            const response = await fetch(`/api/v1/admin/users/${userId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            await this.loadUsers(); // Reload users list
            this.showNotification(result.message || 'User deleted successfully', 'success');
        } catch (error) {
            console.error('Failed to delete user:', error);
            this.showNotification('Failed to delete user', 'error');
        }
    }

    async viewSession(sessionId) {
        try {
            const response = await fetch(`/api/v1/admin/sessions/${sessionId}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const sessionData = await response.json();

            // Open session details in a modal or new window
            this.showSessionModal(sessionData);

        } catch (error) {
            console.error('Failed to view session:', error);
            this.showNotification('Failed to load session details', 'error');
        }
    }

    async exportSession(sessionId) {
        try {
            const response = await fetch(`/api/v1/admin/sessions/${sessionId}/export`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `session_${sessionId}_export.json`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            this.showNotification('Session exported successfully', 'success');

        } catch (error) {
            console.error('Failed to export session:', error);
            this.showNotification('Failed to export session', 'error');
        }
    }

    handleSystemAction(action) {
        switch (action) {
            case 'Backup Database':
                this.backupDatabase();
                break;
            case 'Clear Cache':
                this.clearCache();
                break;
            case 'Export Logs':
                this.exportLogs();
                break;
            case 'Restart Services':
                this.restartServices();
                break;
            default:
                this.showNotification(`Unknown system action: ${action}`, 'warning');
        }
    }

    async backupDatabase() {
        try {
            this.showNotification('Database backup started', 'info');

            const response = await fetch('/api/v1/admin/system/backup', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            this.showNotification(result.message || 'Database backup completed', 'success');
        } catch (error) {
            console.error('Database backup failed:', error);
            this.showNotification('Database backup failed', 'error');
        }
    }

    async clearCache() {
        try {
            const response = await fetch('/api/v1/admin/system/cache/clear', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            this.showNotification(result.message || 'Cache cleared successfully', 'success');
        } catch (error) {
            console.error('Failed to clear cache:', error);
            this.showNotification('Failed to clear cache', 'error');
        }
    }

    async exportLogs() {
        try {
            const response = await fetch('/api/v1/admin/logs', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const logs = await response.json();

            // Create and download the logs file
            const blob = new Blob([JSON.stringify(logs, null, 2)], { type: 'application/json' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `system-logs-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            this.showNotification('Logs exported successfully', 'success');
        } catch (error) {
            console.error('Failed to export logs:', error);
            this.showNotification('Failed to export logs', 'error');
        }
    }

    async restartServices() {
        if (!confirm('Are you sure you want to restart all services? This may cause temporary downtime.')) {
            return;
        }

        try {
            this.showNotification('Services restarting...', 'info');

            const response = await fetch('/api/v1/admin/system/restart', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            this.showNotification('Services restarted successfully', 'success');

        } catch (error) {
            console.error('Failed to restart services:', error);
            this.showNotification('Failed to restart services', 'error');
        }
    }

    async updateActivityChart(period) {
        try {
            // Try to fetch real activity data
            const response = await fetch(`/api/v1/admin/analytics/activity?period=${period}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });

            if (response.ok) {
                const activityData = await response.json();
                this.charts.activity.data.labels = activityData.labels;
                this.charts.activity.data.datasets[0].data = activityData.data;
                this.charts.activity.update();
                return;
            }
        } catch (error) {
            console.warn('Failed to load real activity data, using fallback:', error);
        }

        // Fallback to mock data if API is not available
        const data = {
            '7d': [65, 78, 90, 81, 95, 72, 68],
            '30d': [45, 52, 68, 73, 81, 76, 89, 92, 85, 78, 82, 88, 91, 87, 83, 79, 85, 90, 94, 88, 82, 86, 89, 93, 87, 84, 88, 91, 85, 82],
            '90d': Array.from({ length: 90 }, () => Math.floor(Math.random() * 50) + 50)
        };

        const labels = {
            '7d': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            '30d': Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`),
            '90d': Array.from({ length: 90 }, (_, i) => `Day ${i + 1}`)
        };

        this.charts.activity.data.labels = labels[period];
        this.charts.activity.data.datasets[0].data = data[period];
        this.charts.activity.update();
    }

    loadSectionData(section) {
        switch (section) {
            case 'users':
                this.loadUsers();
                break;
            case 'sessions':
                this.loadSessions();
                break;
            case 'analytics':
                this.loadAnalyticsData();
                break;
            case 'reviews':
                this.loadReviewData();
                break;
            case 'system':
                this.loadSystemHealth();
                break;
        }
    }

    async loadAnalyticsData() {
        try {
            const response = await fetch('/api/v1/admin/analytics', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const analytics = await response.json();

            // Update analytics charts with real data
            this.updateAnalyticsCharts(analytics);

        } catch (error) {
            console.error('Failed to load analytics data:', error);
            this.showNotification('Failed to load analytics data', 'error');
        }
    }

    updateAnalyticsCharts(analytics) {
        // Update charts with real analytics data
        if (analytics.activity_data && this.charts.activity) {
            this.charts.activity.data.datasets[0].data = analytics.activity_data;
            this.charts.activity.update();
        }

        if (analytics.user_growth && this.charts.userGrowth) {
            this.charts.userGrowth.data.datasets[0].data = analytics.user_growth;
            this.charts.userGrowth.update();
        }

        if (analytics.session_metrics && this.charts.sessions) {
            this.charts.sessions.data.datasets[0].data = analytics.session_metrics;
            this.charts.sessions.update();
        }
    }

    showSessionModal(sessionData) {
        // Create and show session details modal
        const modal = document.createElement('div');
        modal.className = 'modal session-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Session Details - ${sessionData.id}</h3>
                    <button class="close-btn" onclick="this.closest('.modal').remove()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="session-info">
                        <p><strong>User:</strong> ${sessionData.user_id}</p>
                        <p><strong>Started:</strong> ${this.formatDate(sessionData.created_at)}</p>
                        <p><strong>Duration:</strong> ${sessionData.duration || 'Ongoing'}</p>
                        <p><strong>Messages:</strong> ${sessionData.message_count || 0}</p>
                    </div>
                    <div class="session-messages">
                        <h4>Messages</h4>
                        <div class="messages-list">
                            ${sessionData.messages ? sessionData.messages.map(msg => `
                                <div class="message-item">
                                    <div class="message-meta">${msg.role} - ${this.formatDate(msg.timestamp)}</div>
                                    <div class="message-content">${msg.content}</div>
                                </div>
                            `).join('') : '<p>No messages available</p>'}
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        modal.style.display = 'block';
    }

    async loadReviewData() {
        try {
            const response = await fetch('/api/v1/admin/reviews', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const reviews = await response.json();

            const pendingReviews = document.getElementById('pending-reviews');
            if (pendingReviews && reviews.length > 0) {
                pendingReviews.innerHTML = reviews.map(review => `
                    <div class="review-item">
                        <div class="review-title">${review.title || `Review #${review.id}`}</div>
                        <div class="review-meta">User: ${review.user_id} • Submitted: ${this.formatDate(review.created_at)}</div>
                        <div class="review-actions">
                            <button class="btn btn-sm btn-primary" onclick="adminDashboard.viewReview('${review.id}')">View</button>
                            <button class="btn btn-sm btn-success" onclick="adminDashboard.approveReview('${review.id}')">Approve</button>
                        </div>
                    </div>
                `).join('');
            } else if (pendingReviews) {
                pendingReviews.innerHTML = '<p>No pending reviews</p>';
            }

        } catch (error) {
            console.error('Failed to load review data:', error);

            // Fallback to mock data if API is not available
            const pendingReviews = document.getElementById('pending-reviews');
            if (pendingReviews) {
                pendingReviews.innerHTML = `
                    <div class="review-item">
                        <div class="review-title">Session Analysis #1247</div>
                        <div class="review-meta">User: john_doe • Submitted: 2 hours ago</div>
                    </div>
                    <div class="review-item">
                        <div class="review-title">Communication Review #1248</div>
                        <div class="review-meta">User: jane_smith • Submitted: 4 hours ago</div>
                    </div>
                    <div class="review-item">
                        <div class="review-title">Trust Building Analysis #1249</div>
                        <div class="review-meta">User: mike_wilson • Submitted: 6 hours ago</div>
                    </div>
                `;
            }

            this.showNotification('Using sample review data - API not available', 'warning');
        }
    }

    async viewReview(reviewId) {
        try {
            const response = await fetch(`/api/v1/admin/reviews/${reviewId}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const review = await response.json();
            this.showReviewModal(review);

        } catch (error) {
            console.error('Failed to view review:', error);
            this.showNotification('Failed to load review details', 'error');
        }
    }

    async approveReview(reviewId) {
        try {
            const response = await fetch(`/api/v1/admin/reviews/${reviewId}/approve`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            this.showNotification('Review approved successfully', 'success');
            this.loadReviewData(); // Refresh the review list

        } catch (error) {
            console.error('Failed to approve review:', error);
            this.showNotification('Failed to approve review', 'error');
        }
    }

    async rejectReview(reviewId) {
        try {
            const response = await fetch(`/api/v1/admin/reviews/${reviewId}/reject`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            this.showNotification('Review rejected successfully', 'success');
            this.loadReviewData(); // Refresh the review list

        } catch (error) {
            console.error('Failed to reject review:', error);
            this.showNotification('Failed to reject review', 'error');
        }
    }

    showReviewModal(review) {
        const modal = document.createElement('div');
        modal.className = 'modal review-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Review Details - ${review.title || `#${review.id}`}</h3>
                    <button class="close-btn" onclick="this.closest('.modal').remove()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="review-info">
                        <p><strong>User:</strong> ${review.user_id}</p>
                        <p><strong>Submitted:</strong> ${this.formatDate(review.created_at)}</p>
                        <p><strong>Status:</strong> ${review.status}</p>
                        <p><strong>Type:</strong> ${review.type || 'General Review'}</p>
                    </div>
                    <div class="review-content">
                        <h4>Content</h4>
                        <div class="review-text">${review.content || 'No content available'}</div>
                    </div>
                    <div class="review-actions">
                        <button class="btn btn-success" onclick="adminDashboard.approveReview('${review.id}'); this.closest('.modal').remove();">Approve</button>
                        <button class="btn btn-danger" onclick="adminDashboard.rejectReview('${review.id}'); this.closest('.modal').remove();">Reject</button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        modal.style.display = 'block';
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;

        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;

        // Set background color based on type
        const colors = {
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#2563eb'
        };
        notification.style.backgroundColor = colors[type] || colors.info;

        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
}

// Add CSS for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Initialize admin dashboard when DOM is loaded
let adminDashboard;
document.addEventListener('DOMContentLoaded', () => {
    adminDashboard = new AdminDashboard();
});