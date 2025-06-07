/**
 * Core Engine Analytics Engine
 * Advanced visualization and analytics for relationship data
 */

class CoreEngineAnalytics {
    constructor() {
        this.charts = new Map();
        this.apiClient = window.coreEngineAPI;
        this.realTimeData = {
            sentiment: [],
            patterns: [],
            metrics: {}
        };

        // Chart configurations
        this.chartConfigs = {
            sentiment: {
                type: 'line',
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Sentiment Analysis Over Time',
                            color: '#f1f5f9'
                        },
                        legend: {
                            labels: {
                                color: '#cbd5e1'
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            min: -1,
                            max: 1,
                            grid: {
                                color: 'rgba(148, 163, 184, 0.2)'
                            },
                            ticks: {
                                color: '#94a3b8'
                            }
                        },
                        x: {
                            grid: {
                                color: 'rgba(148, 163, 184, 0.2)'
                            },
                            ticks: {
                                color: '#94a3b8'
                            }
                        }
                    }
                }
            },

            communication: {
                type: 'radar',
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Communication Patterns',
                            color: '#f1f5f9'
                        },
                        legend: {
                            labels: {
                                color: '#cbd5e1'
                            }
                        }
                    },
                    scales: {
                        r: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(148, 163, 184, 0.2)'
                            },
                            pointLabels: {
                                color: '#94a3b8'
                            },
                            ticks: {
                                color: '#94a3b8'
                            }
                        }
                    }
                }
            },

            relationship: {
                type: 'doughnut',
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Relationship Health Score',
                            color: '#f1f5f9'
                        },
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: '#cbd5e1',
                                padding: 20
                            }
                        }
                    },
                    cutout: '70%'
                }
            }
        };
    }

    /**
     * Initialize all analytics components
     */
    async init() {
        this.setupCharts();
        this.setupRealTimeUpdates();
        await this.loadInitialData();
    }

    /**
     * Setup Chart.js visualizations
     */
    setupCharts() {
        // Sentiment Analysis Chart
        const sentimentCtx = document.getElementById('sentiment-chart');
        if (sentimentCtx) {
            this.charts.set('sentiment', new Chart(sentimentCtx, {
                ...this.chartConfigs.sentiment,
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Sentiment Score',
                        data: [],
                        borderColor: '#60a5fa',
                        backgroundColor: 'rgba(96, 165, 250, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                }
            }));
        }

        // Communication Patterns Chart
        const communicationCtx = document.getElementById('communication-chart');
        if (communicationCtx) {
            this.charts.set('communication', new Chart(communicationCtx, {
                ...this.chartConfigs.communication,
                data: {
                    labels: ['Empathy', 'Active Listening', 'Positivity', 'Clarity', 'Respect', 'Support'],
                    datasets: [{
                        label: 'Current Session',
                        data: [0, 0, 0, 0, 0, 0],
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.2)',
                        borderWidth: 2
                    }]
                }
            }));
        }

        // Relationship Health Chart
        const relationshipCtx = document.getElementById('relationship-chart');
        if (relationshipCtx) {
            this.charts.set('relationship', new Chart(relationshipCtx, {
                ...this.chartConfigs.relationship,
                data: {
                    labels: ['Healthy', 'Needs Attention', 'Critical'],
                    datasets: [{
                        data: [70, 25, 5],
                        backgroundColor: [
                            '#10b981',
                            '#f59e0b',
                            '#ef4444'
                        ],
                        borderWidth: 0
                    }]
                }
            }));
        }
    }

    /**
     * Update sentiment chart with new data
     */
    updateSentimentChart(data) {
        const chart = this.charts.get('sentiment');
        if (!chart) return;

        const now = new Date();
        const timeLabel = now.toLocaleTimeString();

        chart.data.labels.push(timeLabel);
        chart.data.datasets[0].data.push(data.sentiment);

        // Keep only last 20 data points
        if (chart.data.labels.length > 20) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
        }

        chart.update('none');
    }

    /**
     * Update communication patterns chart
     */
    updateCommunicationChart(patterns) {
        const chart = this.charts.get('communication');
        if (!chart) return;

        chart.data.datasets[0].data = [
            patterns.empathy || 0,
            patterns.activeListening || 0,
            patterns.positivity || 0,
            patterns.clarity || 0,
            patterns.respect || 0,
            patterns.support || 0
        ];

        chart.update('none');
    }

    /**
     * Update relationship health chart
     */
    updateRelationshipChart(healthData) {
        const chart = this.charts.get('relationship');
        if (!chart) return;

        chart.data.datasets[0].data = [
            healthData.healthy || 0,
            healthData.needsAttention || 0,
            healthData.critical || 0
        ];

        chart.update('none');
    }

    /**
     * Process analysis results and update visualizations
     */
    async processAnalysisResults(analysisData) {
        try {
            // Update sentiment tracking
            if (analysisData.sentiment) {
                this.updateSentimentChart({
                    sentiment: analysisData.sentiment.score,
                    timestamp: new Date()
                });

                // Update sentiment display
                this.updateSentimentDisplay(analysisData.sentiment);
            }

            // Update communication patterns
            if (analysisData.communication_style) {
                this.updateCommunicationChart({
                    empathy: analysisData.communication_style.empathy_score || 0,
                    activeListening: analysisData.communication_style.listening_score || 0,
                    positivity: analysisData.sentiment?.score > 0 ? analysisData.sentiment.score : 0,
                    clarity: analysisData.communication_style.clarity_score || 0,
                    respect: analysisData.communication_style.respect_score || 0,
                    support: analysisData.communication_style.support_score || 0
                });
            }

            // Update relationship metrics
            if (analysisData.relationship_health) {
                this.updateRelationshipChart(analysisData.relationship_health);
            }

            // Update recommendations
            if (analysisData.recommendations) {
                this.updateRecommendations(analysisData.recommendations);
            }

        } catch (error) {
            console.error('Error processing analysis results:', error);
        }
    }

    /**
     * Update sentiment display elements
     */
    updateSentimentDisplay(sentimentData) {
        const sentimentLabel = document.getElementById('sentiment-label');
        const sentimentScore = document.getElementById('sentiment-score');
        const sentimentBar = document.getElementById('sentiment-bar');

        if (sentimentLabel) {
            sentimentLabel.textContent = this.getSentimentLabel(sentimentData.score);
            sentimentLabel.className = `sentiment-label ${this.getSentimentClass(sentimentData.score)}`;
        }

        if (sentimentScore) {
            sentimentScore.textContent = sentimentData.score.toFixed(2);
        }

        if (sentimentBar) {
            const percentage = ((sentimentData.score + 1) / 2) * 100;
            sentimentBar.style.width = `${percentage}%`;
            sentimentBar.className = `sentiment-bar ${this.getSentimentClass(sentimentData.score)}`;
        }
    }

    /**
     * Get sentiment label from score
     */
    getSentimentLabel(score) {
        if (score > 0.3) return 'Positive';
        if (score < -0.3) return 'Negative';
        return 'Neutral';
    }

    /**
     * Get CSS class for sentiment
     */
    getSentimentClass(score) {
        if (score > 0.3) return 'positive';
        if (score < -0.3) return 'negative';
        return 'neutral';
    }

    /**
     * Update recommendations display
     */
    updateRecommendations(recommendations) {
        const container = document.getElementById('recommendations-list');
        if (!container) return;

        container.innerHTML = '';

        recommendations.forEach((rec, index) => {
            const item = document.createElement('div');
            item.className = 'recommendation-item animate-slideInUp';
            item.style.animationDelay = `${index * 0.1}s`;

            item.innerHTML = `
                <div class="flex items-start gap-md">
                    <div class="recommendation-icon">
                        ${this.getRecommendationIcon(rec.type)}
                    </div>
                    <div class="flex-1">
                        <h4 class="recommendation-title">${rec.title || 'Recommendation'}</h4>
                        <p class="recommendation-text">${rec.text}</p>
                        ${rec.priority ? `<span class="priority-badge priority-${rec.priority}">${rec.priority}</span>` : ''}
                    </div>
                </div>
            `;

            container.appendChild(item);
        });
    }

    /**
     * Get icon for recommendation type
     */
    getRecommendationIcon(type) {
        const icons = {
            communication: '💬',
            emotion: '💝',
            activity: '🎯',
            support: '🤝',
            growth: '🌱'
        };
        return icons[type] || '💡';
    }

    /**
     * Setup real-time updates
     */
    setupRealTimeUpdates() {
        if (this.apiClient && this.apiClient.setupWebSocket) {
            this.apiClient.setupWebSocket();
            this.apiClient.on('analysis_update', (data) => {
                this.processAnalysisResults(data);
            });
        }
    }

    /**
     * Load initial dashboard data
     */
    async loadInitialData() {
        try {
            if (this.apiClient) {
                const healthData = await this.apiClient.getHealthMetrics();
                if (healthData) {
                    this.updateDashboardMetrics(healthData);
                }
            }
        } catch (error) {
            console.warn('Could not load initial data:', error);
        }
    }

    /**
     * Update dashboard metrics
     */
    updateDashboardMetrics(data) {
        // Update metric displays
        const analysisCount = document.getElementById('analysis-count');
        const avgSentiment = document.getElementById('avg-sentiment');
        const successRate = document.getElementById('success-rate');

        if (analysisCount) analysisCount.textContent = data.totalAnalyses || '-';
        if (avgSentiment) avgSentiment.textContent = data.averageSentiment ? data.averageSentiment.toFixed(2) : '-';
        if (successRate) successRate.textContent = data.successRate ? `${data.successRate}%` : '-';
    }

    /**
     * Analyze conversation text
     */
    async analyzeConversation(conversationText) {
        try {
            const result = await this.apiClient.analyzeConversation(conversationText);
            await this.processAnalysisResults(result);
            return result;
        } catch (error) {
            console.error('Analysis failed:', error);
            throw error;
        }
    }

    /**
     * Export analytics data
     */
    exportData() {
        const data = {
            timestamp: new Date().toISOString(),
            sentiment: this.realTimeData.sentiment,
            patterns: this.realTimeData.patterns,
            metrics: this.realTimeData.metrics
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `core_engine-analytics-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }
}

// Initialize analytics when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.coreEngineAnalytics = new CoreEngineAnalytics();
    window.coreEngineAnalytics.init();
});
