/**
 * Cloud Field Campaign Scorecard - Complete App
 * With dark mode, admin mode, versioning
 */

const API_BASE = 'http://localhost:8000/api/data';
const ADMIN_PASSWORD = 'admin123'; // TODO: Change in production

let data = {
    summary: null,
    clouds: null,
    horseman: null,
    traffic: null,
    regional: null
};

let state = {
    isAdmin: false,
    theme: 'light',
    currentView: 'overview'
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('App initialized');

    // Load saved state
    loadState();

    // Load data
    loadData();

    // Event listeners
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);
    document.getElementById('generateInsightsBtn').addEventListener('click', generateInsights);

    // Nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const view = item.dataset.view;
            if (view) {
                switchView(view);
            }
        });
    });

    // Admin modal - Enter key
    document.getElementById('adminPassword').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') loginAdmin();
    });
});

// Load state from localStorage
function loadState() {
    const saved = localStorage.getItem('scorecardState');
    if (saved) {
        const savedState = JSON.parse(saved);
        state.theme = savedState.theme || 'light';
        state.isAdmin = savedState.isAdmin || false;
    }

    // Apply theme
    if (state.theme === 'dark') {
        document.body.classList.add('dark');
        document.getElementById('themeToggle').textContent = '☀️ Light Mode';
    }

    // Apply admin status
    if (state.isAdmin) {
        document.body.classList.add('is-admin');
        document.getElementById('userName').textContent = 'Admin';
    }
}

// Save state to localStorage
function saveState() {
    localStorage.setItem('scorecardState', JSON.stringify(state));
}

// Toggle Dark/Light Mode
function toggleTheme() {
    state.theme = state.theme === 'light' ? 'dark' : 'light';

    if (state.theme === 'dark') {
        document.body.classList.add('dark');
        document.getElementById('themeToggle').textContent = '☀️ Light Mode';
    } else {
        document.body.classList.remove('dark');
        document.getElementById('themeToggle').textContent = '🌙 Dark Mode';
    }

    saveState();
}

// Admin Modal
function openAdminModal() {
    if (state.isAdmin) {
        // Already admin, show options
        alert('Admin features:\n- User management\n- Settings\n- Data export\n\nClick Logout to exit admin mode');
        if (confirm('Logout from admin?')) {
            logoutAdmin();
        }
    } else {
        document.getElementById('adminModal').classList.add('active');
    }
}

function closeAdminModal() {
    document.getElementById('adminModal').classList.remove('active');
    document.getElementById('adminPassword').value = '';
    document.getElementById('adminError').classList.remove('visible');
}

function loginAdmin() {
    const password = document.getElementById('adminPassword').value;

    if (password === ADMIN_PASSWORD) {
        state.isAdmin = true;
        document.body.classList.add('is-admin');
        document.getElementById('userName').textContent = 'Admin';
        saveState();
        closeAdminModal();
        alert('✅ Admin access granted!');
    } else {
        const errorEl = document.getElementById('adminError');
        errorEl.textContent = 'Incorrect password';
        errorEl.classList.add('visible');
    }
}

function logoutAdmin() {
    state.isAdmin = false;
    document.body.classList.remove('is-admin');
    document.getElementById('userName').textContent = 'Guest';
    saveState();
    alert('Logged out from admin mode');
}

// Switch View
function switchView(view) {
    state.currentView = view;

    // Update active nav
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.view === view) {
            item.classList.add('active');
        }
    });

    // Update breadcrumb
    const viewNames = {
        overview: 'Overview',
        clouds: 'Health of Cloud',
        regional: 'Regional View',
        horseman: 'Horseman',
        traffic: 'Traffic Source',
        settings: 'Settings',
        users: 'User Management'
    };
    document.getElementById('currentView').textContent = viewNames[view] || view;

    // TODO: Render appropriate view
    console.log('Switched to view:', view);
}

// Load all data from API
async function loadData() {
    showLoading();

    try {
        const [summary, clouds, horseman, traffic, regional] = await Promise.all([
            fetch(`${API_BASE}/summary`).then(r => r.json()),
            fetch(`${API_BASE}/clouds`).then(r => r.json()),
            fetch(`${API_BASE}/horseman`).then(r => r.json()),
            fetch(`${API_BASE}/traffic`).then(r => r.json()),
            fetch(`${API_BASE}/regional`).then(r => r.json())
        ]);

        data = { summary, clouds, horseman, traffic, regional };

        renderSummaryStats();
        renderCloudCards();

        hideLoading();
    } catch (error) {
        console.error('Error loading data:', error);
        alert('Failed to load data. Make sure the API is running on localhost:8000');
        hideLoading();
    }
}

// Render Summary Stats
function renderSummaryStats() {
    const container = document.getElementById('summaryStats');

    const totalMDP = data.summary.total_mdp;
    const cloudCount = Object.keys(data.summary.cloud_breakdown).length;

    let topCloud = { name: '', mdp: 0 };
    for (const [cloud, info] of Object.entries(data.summary.cloud_breakdown)) {
        if (info.mdp > topCloud.mdp) {
            topCloud = { name: cloud, mdp: info.mdp };
        }
    }

    const stats = [
        {
            icon: '💰',
            label: 'Total MDP',
            value: formatCurrency(totalMDP),
            change: null
        },
        {
            icon: '☁️',
            label: 'Clouds Tracked',
            value: cloudCount,
            change: null
        },
        {
            icon: '🏆',
            label: 'Top Cloud',
            value: topCloud.name,
            subvalue: formatCurrency(topCloud.mdp)
        },
        {
            icon: '📊',
            label: 'Leaders',
            value: data.regional.count,
            change: null
        }
    ];

    container.innerHTML = stats.map(stat => `
        <div class="stat-card">
            <div class="stat-icon">${stat.icon}</div>
            <div class="stat-label">${stat.label}</div>
            <div class="stat-value">${stat.value}</div>
            ${stat.subvalue ? `<div class="stat-change">${stat.subvalue}</div>` : ''}
            ${stat.change !== null ? `
                <div class="stat-change ${stat.change >= 0 ? 'positive' : 'negative'}">
                    ${stat.change >= 0 ? '↑' : '↓'} ${Math.abs(stat.change * 100).toFixed(1)}% YoY
                </div>
            ` : ''}
        </div>
    `).join('');
}

// Render Cloud Cards
function renderCloudCards() {
    const container = document.getElementById('cloudCards');

    const clouds = data.clouds.clouds.slice(0, 6);

    container.innerHTML = clouds.map(cloud => {
        const yoyChange = cloud.avg_yoy_change;
        const isPositive = yoyChange >= 0;
        const insights = getCloudInsights(cloud.cloud, cloud.mdp, yoyChange);

        return `
            <div class="cloud-card">
                <div class="cloud-card-header">
                    <div class="cloud-name">${cloud.cloud}</div>
                    ${yoyChange !== null ? `
                        <div class="cloud-badge ${isPositive ? 'badge-positive' : 'badge-negative'}">
                            ${isPositive ? '↑' : '↓'} ${Math.abs(yoyChange * 100).toFixed(1)}% YoY
                        </div>
                    ` : ''}
                </div>

                <div class="cloud-metrics">
                    <div class="metric">
                        <div class="metric-label">MDP</div>
                        <div class="metric-value">${formatCurrency(cloud.mdp)}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Leaders</div>
                        <div class="metric-value">${cloud.leaders_count}</div>
                    </div>
                </div>

                <div class="insights-section">
                    <div class="insight-group">
                        <div class="insight-title highlights">
                            🟢 Highlights
                        </div>
                        <ul class="insight-list highlights">
                            ${insights.highlights.map(h => `<li class="insight-item">${h}</li>`).join('')}
                        </ul>
                    </div>

                    <div class="insight-group">
                        <div class="insight-title lowlights">
                            🔴 Areas to Watch
                        </div>
                        <ul class="insight-list lowlights">
                            ${insights.lowlights.map(l => `<li class="insight-item">${l}</li>`).join('')}
                        </ul>
                    </div>

                    <div class="insight-group">
                        <div class="insight-title actions">
                            📋 Next Steps
                        </div>
                        <ul class="insight-list actions">
                            ${insights.actions.map(a => `<li class="insight-item">${a}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// Get cloud insights (from your deck data)
function getCloudInsights(cloud, mdp, yoyChange) {
    const insights = {
        Service: {
            highlights: [
                "Strong overall performance +13% YoY, all regions showing growth, UKI standout +34%",
                "Webinar L2 increase +62% YoY, totalling 8% of MDP share",
                "Email continues to grow for Service +8% YoY"
            ],
            lowlights: [
                "Central performance decreased -32% YoY",
                "MDP percentage 32%, -2.5 ppts vs Q1 FY26",
                "AE contribution down -14% YoY, only horseman in decline"
            ],
            actions: [
                "Q2 planning underway. BoM active across Organic channels",
                "9 Service focused webinars planned in Q2",
                "Assist Paid team to ensure budget spent efficiently (-62% Cloud budget)"
            ]
        },
        Sales: {
            highlights: [
                "Webinars continue strong growth +44%, share gradually increasing",
                "North experiencing +45% YoY growth, contributing 34%",
                "BrightTalk on-demand program active"
            ],
            lowlights: [
                "Central decline -3% (excl CH), driven by paid -18% and organic -34%",
                "Paid and organic search declining -31% and -33% YoY",
                "Localised demos overwritten by English versions"
            ],
            actions: [
                "Continue webinar momentum, on-demand promotion via DSE",
                "Focus week Apr 20-24 to activate localised emails",
                "Demo localisation project underway for organic growth"
            ]
        },
        Marketing: {
            highlights: [
                "Strong BDR w/ double-digit growth Central +32%, South +28%, France +11%",
                "Digital Specialist ramping $16.4M generated across OUs",
                "Paid growth strong +57% YoY driven by content synd $4.9M"
            ],
            lowlights: [
                "Double-digit AE decline across 5 OUs, notably Central -77%, South -60%",
                "Email 'other' offers down -23% YoY (demos, guides, newsletters)",
                "Organic -48% and paid -31% search decline"
            ],
            actions: [
                "Continue webinar momentum w/ Q2 execution (4 webinars)",
                "Activate Q2 GIC BOM: 7 UK, 3 FR, 3 DE, 3 IT, 3 NL, 3 ES offers",
                "Post-CNX'26 webinar + nurture targeting attendees"
            ]
        }
    };

    return insights[cloud] || {
        highlights: [`MDP: ${formatCurrency(mdp)}`, 'Performance tracking enabled'],
        lowlights: ['Monitor trends for optimization'],
        actions: ['Review performance metrics', 'Optimize channel mix']
    };
}

// Generate Insights with Claude
async function generateInsights() {
    try {
        const response = await fetch('http://localhost:8000/api/insights/example');
        const result = await response.json();

        alert(`🤖 AI Insights Generated!\n\nCloud: ${result.cloud}\n\n🟢 Highlights:\n${result.insights.highlights.join('\n')}\n\n🔴 Areas to Watch:\n${result.insights.areas_to_watch.join('\n')}`);
    } catch (error) {
        alert('Failed to generate insights. Make sure API is running.');
    }
}

// Utility Functions
function formatCurrency(value) {
    if (!value) return '$0';
    if (value >= 1000000) {
        return `$${(value / 1000000).toFixed(1)}M`;
    }
    return `$${(value / 1000).toFixed(0)}K`;
}

function showLoading() {
    document.body.classList.add('loading');
}

function hideLoading() {
    document.body.classList.remove('loading');
}
