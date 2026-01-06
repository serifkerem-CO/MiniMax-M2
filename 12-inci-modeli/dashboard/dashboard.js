/**
 * 12. İnci Modeli - Analytics Dashboard
 * Real-time analytics and monitoring
 */

const API_BASE = 'http://localhost:8000';
let emotionChart, trafficChart, performanceChart;
let activityFeed = [];

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    console.log('📊 Initializing Analytics Dashboard...');

    initializeCharts();
    loadInitialData();
    startRealTimeUpdates();

    console.log('✅ Dashboard ready');
});

// ============================================
// Chart Initialization
// ============================================

function initializeCharts() {
    // Emotion Distribution Pie Chart
    const emotionCtx = document.getElementById('emotionChart').getContext('2d');
    emotionChart = new Chart(emotionCtx, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: [
                    '#fbbf24', '#60a5fa', '#f87171', '#a78bfa',
                    '#86efac', '#fde047', '#fb7185', '#38bdf8',
                    '#5eead4', '#34d399', '#94a3b8', '#f472b6'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#f1f5f9',
                        padding: 15,
                        font: { size: 12 }
                    }
                }
            }
        }
    });

    // Hourly Traffic Line Chart
    const trafficCtx = document.getElementById('trafficChart').getContext('2d');
    trafficChart = new Chart(trafficCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Requests',
                data: [],
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#f1f5f9' }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: '#cbd5e1' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                },
                x: {
                    ticks: { color: '#cbd5e1' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                }
            }
        }
    });

    // Performance Line Chart
    const perfCtx = document.getElementById('performanceChart').getContext('2d');
    performanceChart = new Chart(perfCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Response Time (ms)',
                data: [],
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#f1f5f9' }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: '#cbd5e1' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                },
                x: {
                    ticks: { color: '#cbd5e1' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                }
            }
        }
    });
}

// ============================================
// Data Loading
// ============================================

async function loadInitialData() {
    try {
        // Load analytics summary
        const response = await fetch(`${API_BASE}/api/v1/analytics/summary`);
        const data = await response.json();

        updateKPIs(data);
        updateEmotionChart(data.emotion_distribution);
        updateEmotionsList(data.top_emotions);
        updateTrafficChart(data.hourly_stats);

    } catch (error) {
        console.error('Error loading data:', error);
        showError('Failed to load analytics data');
    }
}

function updateKPIs(data) {
    document.getElementById('total-requests').textContent =
        data.total_events?.toLocaleString() || '0';

    document.getElementById('active-users').textContent =
        data.system_metrics?.active_connections || '0';

    document.getElementById('avg-response-time').textContent =
        `${Math.round(data.system_metrics?.avg_response_time || 0)}ms`;

    const topEmotion = data.top_emotions?.[0];
    if (topEmotion) {
        const emotionLabels = {
            'joy': '😊 Mutluluk',
            'sadness': '😢 Üzüntü',
            'anger': '😠 Öfke',
            'fear': '😨 Korku',
            'disgust': '🤢 Tiksinme',
            'surprise': '😲 Şaşkınlık',
            'love': '❤️ Sevgi',
            'curiosity': '🤔 Merak',
            'peace': '😌 Huzur',
            'confidence': '💪 Güven',
            'regret': '😔 Pişmanlık',
            'excitement': '🎉 Heyecan'
        };
        document.getElementById('top-emotion').textContent =
            emotionLabels[topEmotion.emotion] || topEmotion.emotion;
    }
}

function updateEmotionChart(distribution) {
    const emotionLabels = {
        'joy': '😊 Mutluluk',
        'sadness': '😢 Üzüntü',
        'anger': '😠 Öfke',
        'fear': '😨 Korku',
        'disgust': '🤢 Tiksinme',
        'surprise': '😲 Şaşkınlık',
        'love': '❤️ Sevgi',
        'curiosity': '🤔 Merak',
        'peace': '😌 Huzur',
        'confidence': '💪 Güven',
        'regret': '😔 Pişmanlık',
        'excitement': '🎉 Heyecan'
    };

    const labels = [];
    const values = [];

    for (const [emotion, count] of Object.entries(distribution)) {
        labels.push(emotionLabels[emotion] || emotion);
        values.push(count);
    }

    emotionChart.data.labels = labels;
    emotionChart.data.datasets[0].data = values;
    emotionChart.update();
}

function updateEmotionsList(topEmotions) {
    const container = document.getElementById('emotionsList');
    container.innerHTML = '';

    const emotionData = {
        'joy': { emoji: '😊', label: 'Mutluluk' },
        'sadness': { emoji: '😢', label: 'Üzüntü' },
        'anger': { emoji: '😠', label: 'Öfke' },
        'fear': { emoji: '😨', label: 'Korku' },
        'disgust': { emoji: '🤢', label: 'Tiksinme' },
        'surprise': { emoji: '😲', label: 'Şaşkınlık' },
        'love': { emoji: '❤️', label: 'Sevgi' },
        'curiosity': { emoji: '🤔', label: 'Merak' },
        'peace': { emoji: '😌', label: 'Huzur' },
        'confidence': { emoji: '💪', label: 'Güven' },
        'regret': { emoji: '😔', label: 'Pişmanlık' },
        'excitement': { emoji: '🎉', label: 'Heyecan' }
    };

    const maxCount = Math.max(...topEmotions.map(e => e.count));

    topEmotions.forEach(item => {
        const emotion = emotionData[item.emotion];
        if (!emotion) return;

        const percentage = (item.count / maxCount) * 100;

        const div = document.createElement('div');
        div.className = 'emotion-item';
        div.innerHTML = `
            <div>
                <div class="emotion-name">
                    <span>${emotion.emoji}</span>
                    <span>${emotion.label}</span>
                </div>
                <div class="emotion-bar">
                    <div class="emotion-bar-fill" style="width: ${percentage}%"></div>
                </div>
            </div>
            <span class="emotion-count">${item.count}</span>
        `;

        container.appendChild(div);
    });
}

function updateTrafficChart(hourlyStats) {
    const labels = [];
    const data = [];

    hourlyStats.forEach(stat => {
        const hour = new Date(stat.hour).getHours();
        labels.push(`${hour}:00`);
        data.push(stat.requests);
    });

    trafficChart.data.labels = labels;
    trafficChart.data.datasets[0].data = data;
    trafficChart.update();

    // Also update performance chart
    const perfData = hourlyStats.map(s => s.avg_response_time);
    performanceChart.data.labels = labels;
    performanceChart.data.datasets[0].data = perfData;
    performanceChart.update();
}

// ============================================
// Real-time Updates
// ============================================

function startRealTimeUpdates() {
    // Update every 5 seconds
    setInterval(() => {
        loadInitialData();
        updateLastUpdateTime();
    }, 5000);

    // Simulate activity feed
    setInterval(() => {
        addActivityItem();
    }, 3000);
}

function updateLastUpdateTime() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('tr-TR', {
        hour: '2-digit',
        minute: '2-digit'
    });
    document.getElementById('last-update').textContent = `Last update: ${timeStr}`;
}

function addActivityItem() {
    const activities = [
        { icon: '😊', text: 'New joy emotion detected', emotion: 'joy' },
        { icon: '😢', text: 'Sadness analysis completed', emotion: 'sadness' },
        { icon: '👤', text: 'New user registered', type: 'user' },
        { icon: '📊', text: 'Analytics data exported', type: 'system' },
        { icon: '🔄', text: 'Cache refreshed', type: 'system' },
        { icon: '⚡', text: 'Fast response (85ms)', type: 'performance' }
    ];

    const activity = activities[Math.floor(Math.random() * activities.length)];

    const feed = document.getElementById('activityFeed');
    const item = document.createElement('div');
    item.className = 'activity-item';

    const now = new Date();
    const timeStr = now.toLocaleTimeString('tr-TR', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });

    item.innerHTML = `
        <div class="activity-icon">${activity.icon}</div>
        <div class="activity-content">
            <div class="activity-text">${activity.text}</div>
            <div class="activity-time">${timeStr}</div>
        </div>
    `;

    feed.insertBefore(item, feed.firstChild);

    // Keep only last 20 items
    while (feed.children.length > 20) {
        feed.removeChild(feed.lastChild);
    }

    // Update count
    document.getElementById('activity-count').textContent =
        `${feed.children.length} events`;
}

// ============================================
// User Actions
// ============================================

function refreshCharts() {
    console.log('🔄 Refreshing charts...');
    loadInitialData();
}

function updateTimeRange() {
    const range = document.getElementById('timeRange').value;
    console.log(`📅 Time range changed to: ${range}`);
    // Would fetch data for selected range
    loadInitialData();
}

function showError(message) {
    console.error('❌', message);
    // Could show toast notification
}

// Export for global access
window.refreshCharts = refreshCharts;
window.updateTimeRange = updateTimeRange;
