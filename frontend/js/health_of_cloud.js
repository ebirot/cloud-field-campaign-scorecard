/**
 * Health of the Cloud Scorecard
 * Displays MDP data in 3-column slide layout
 */

// Auto-detect API URL based on environment
const getApiUrl = () => {
    const hostname = window.location.hostname;
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return 'http://localhost:8000';
    }
    return window.location.origin; // Use same origin (Heroku URL)
};

const API_BASE_URL = getApiUrl();
const API_BASE = `${API_BASE_URL}/api/data`;
const ANALYTICS_API = `${API_BASE_URL}/api/analytics`;
const CAMPAIGN_API = `${API_BASE_URL}/api/campaign`;

// Tableau Configuration
const TABLEAU_SERVER = 'https://prod-uswest-c.online.tableau.com';
const TABLEAU_SITE = 'salesforce';
const TABLEAU_WORKBOOK_PATH = 'FY27AMEREMEACFMMDPScorecardBuilderDataCSVBackEnd';

// Tableau View Links (using real workbook name from browser URL)
// Format: /#/site/{site}/views/{workbook}/{view}?:iid=1
const TABLEAU_LINKS = {
    regional: `${TABLEAU_SERVER}/#/site/${TABLEAU_SITE}/views/${TABLEAU_WORKBOOK_PATH}/1_REGIONALVIEWSalesL2Cloud?:iid=1`,
    horseman: `${TABLEAU_SERVER}/#/site/${TABLEAU_SITE}/views/${TABLEAU_WORKBOOK_PATH}/3_HORSEMAN?:iid=1`,
    traffic: `${TABLEAU_SERVER}/#/site/${TABLEAU_SITE}/views/${TABLEAU_WORKBOOK_PATH}/4_TRAFFICSOURCE?:iid=1`,
    offer: `${TABLEAU_SERVER}/#/site/${TABLEAU_SITE}/views/${TABLEAU_WORKBOOK_PATH}/5_OFFERL1L2?:iid=1`,
    webinar: `${TABLEAU_SERVER}/#/site/${TABLEAU_SITE}/views/${TABLEAU_WORKBOOK_PATH}/6_WEBINAR?:iid=1`
};

// Analytics tracking
async function trackEvent(eventType, metadata = {}) {
    try {
        await fetch(`${ANALYTICS_API}/track`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                event_type: eventType,
                user_id: localStorage.getItem('scorecard_user_id') || 'anonymous',
                metadata: metadata
            })
        });
    } catch (e) {
        console.log('Analytics tracking failed:', e);
    }
}

let currentCloud = 'Service';
let currentTab = 'health';
let currentRegionFilter = 'BOTH'; // BOTH, EMEA, AMER
let currentOUFilter = null; // null = all OUs, or specific OU name
let currentQuarter = 'Q2'; // Q1, Q2, Q1,Q2 (YTD), etc.
let currentFiscalYear = 'FY2027'; // FY2026, FY2027, or 'ALL'
let data = {
    regional: null,
    horseman: null,
    traffic: null,
    clouds: null
};

// All available clouds
const ALL_CLOUDS = [
    'Service',
    'Sales',
    'Marketing',
    'Commerce',
    'AI and Data',
    'Analytics',
    'Integration',
    'Salesforce Platform',
    'Slack',
    'Other',
    'Core Success Plans',
    'Agentforce'
];

// Load cloud visibility config from localStorage or use defaults
let cloudModeVisibleClouds = JSON.parse(localStorage.getItem('cloudModeVisibleClouds')) || ['Service', 'Sales', 'Marketing', 'Commerce', 'AI and Data', 'Agentforce'];
let ouModeVisibleClouds = JSON.parse(localStorage.getItem('ouModeVisibleClouds')) || ['Service', 'Sales', 'Marketing', 'Commerce', 'AI and Data', 'Agentforce'];

// Operating Unit to Leader mapping
const OU_TO_LEADER = {
    // EMEA
    'CENTRAL': 'Alexander Wallner',
    'NORTH': 'Bob Vanstraelen',
    'FRANCE': 'Emilie Sidiqian',
    'SOUTH': 'Marco Hernansanz',
    'UKI': 'Zahra Bahrololoumi',
    // AMER
    'AMER REG': 'Mark Sullivan',
    'TMT': 'Lenore Lang',
    'PACE & AFD360': 'Connor Marsden',
    'CBS': 'Scot Blocker'
};

// Leader to OU mapping (reverse)
const LEADER_TO_OU = {};
for (const [ou, leader] of Object.entries(OU_TO_LEADER)) {
    LEADER_TO_OU[leader] = ou;
}

// EMEA Leaders & OUs
const EMEA_OUS = [
    'Alexander Wallner',    // CENTRAL
    'Bob Vanstraelen',       // NORTH
    'Emilie Sidiqian',       // FRANCE
    'Marco Hernansanz',      // SOUTH
    'Zahra Bahrololoumi'     // UKI
];

// AMER Leaders & OUs
const AMER_OUS = [
    'Mark Sullivan',         // AMER REG
    'Lenore Lang',           // TMT
    'Connor Marsden',        // PACE & AFD360
    'Scot Blocker'           // CBS
];

// Cloud Logo URLs (from Salesforce official site)
const CLOUD_LOGOS = {
    'Service': 'https://wp.sfdcdigital.com/en-us/wp-content/uploads/sites/4/2024/06/icon-service.svg?w=64',
    'Sales': 'https://wp.sfdcdigital.com/en-us/wp-content/uploads/sites/4/2024/06/icon-sales.svg?w=64',
    'Marketing': 'https://wp.sfdcdigital.com/en-us/wp-content/uploads/sites/4/2024/06/icon-marketing.svg?w=64',
    'Commerce': 'https://wp.sfdcdigital.com/en-us/wp-content/uploads/sites/4/2024/06/icon-commerce.svg?w=64',
    'AI and Data': 'https://wp.sfdcdigital.com/en-us/wp-content/uploads/sites/4/2024/06/icon-data-cloud.svg?w=64',
    'Analytics': 'https://wp.sfdcdigital.com/en-us/wp-content/uploads/sites/4/2024/06/icon-tableau.svg?w=64',
    'Integration': 'https://wp.sfdcdigital.com/en-us/wp-content/uploads/sites/4/2024/06/icon-mulesoft.svg?w=64',
    'Salesforce Platform': 'https://wp.sfdcdigital.com/en-us/wp-content/uploads/sites/4/2024/06/icon-platform.svg?w=64',
    'Slack': 'https://wp.sfdcdigital.com/en-us/wp-content/uploads/sites/4/2024/06/icon-slack.svg?w=64',
    'Core Success Plans': '🎯', // Emoji fallback
    'Agentforce': 'https://wp.sfdcdigital.com/en-us/wp-content/uploads/sites/4/2024/06/icon-agentforce.svg?w=64',
    'Other': '☁️' // Emoji fallback
};

// Cloud-specific insights from your deck
const CLOUD_INSIGHTS = {
    Service: {
        highlights: [
            "Strong overall performance +13% YoY, all regions showing growth, UKI standout +34%",
            "Webinar L2 increase +62% YoY, totalling 8% of MDP share",
            "Email continues to grow for Service +8% YoY",
            "BDR contribution strong with double-digit growth in multiple regions"
        ],
        lowlights: [
            "Central performance decreased -32% YoY",
            "MDP percentage 32%, -2.5 ppts vs Q1 FY26",
            "AE contribution down -14% YoY, only horseman in decline",
            "Paid budget underutilized at -62% vs allocated Cloud budget"
        ],
        actions: [
            "<strong>Q2 Webinar Momentum:</strong> 9 Service-focused webinars planned in Q2. BoM active across Organic channels to drive registration.",
            "<strong>Central Recovery Plan:</strong> Partner with GIC team to audit email offer mix and boost engagement in Central region.",
            "<strong>Paid Optimization:</strong> Assist Paid team to ensure budget spent efficiently. Current -62% Cloud budget requires immediate attention.",
            "<strong>AE Enablement:</strong> Launch targeted enablement for AE segment to reverse -14% YoY decline."
        ]
    },
    Sales: {
        highlights: [
            "Webinars continue strong growth +44%, share gradually increasing",
            "North experiencing +45% YoY growth, contributing 34%",
            "BrightTalk on-demand program active and performing well",
            "Email engagement improving across key segments"
        ],
        lowlights: [
            "Central decline -3% (excl CH), driven by paid -18% and organic -34%",
            "Paid and organic search declining -31% and -33% YoY",
            "Localised demos overwritten by English versions impacting regional performance",
            "South region showing slower growth vs other OUs"
        ],
        actions: [
            "<strong>Webinar Scale-Up:</strong> Continue webinar momentum with Q2 lineup. On-demand promotion via DSE to extend reach.",
            "<strong>Email Focus Week:</strong> Apr 20-24 focus week to activate localised emails across all regions.",
            "<strong>Demo Localization:</strong> Demo localisation project underway for organic growth. Fix overwrite issues priority.",
            "<strong>SEM Recovery:</strong> Partner with Paid team to diagnose and reverse -31% search decline."
        ]
    },
    Marketing: {
        highlights: [
            "Strong BDR w/ double-digit growth Central +32%, South +28%, France +11%",
            "Digital Specialist ramping $16.4M generated across OUs",
            "Paid growth strong +57% YoY driven by content synd $4.9M",
            "Webinar performance trending positive across regions"
        ],
        lowlights: [
            "Double-digit AE decline across 5 OUs, notably Central -77%, South -60%",
            "Email 'other' offers down -23% YoY (demos, guides, newsletters)",
            "Organic -48% and paid -31% search decline",
            "North region underperforming vs EMEA average"
        ],
        actions: [
            "<strong>Q2 GIC BOM Activation:</strong> Execute Q2 GIC BOM: 7 UK, 3 FR, 3 DE, 3 IT, 3 NL, 3 ES offers ready to deploy.",
            "<strong>CNX'26 Follow-Up:</strong> Post-CNX'26 webinar + nurture targeting attendees to convert engagement to pipeline.",
            "<strong>Webinar Series:</strong> Continue webinar momentum w/ Q2 execution (4 Marketing webinars scheduled).",
            "<strong>AE Turnaround:</strong> Address double-digit AE decline with targeted sales enablement and content refresh."
        ]
    },
    Commerce: {
        highlights: [
            "MDP tracking enabled and performing above expectations",
            "Regional distribution balanced across EMEA and AMER",
            "BDR contribution showing strong momentum"
        ],
        lowlights: [
            "Limited historical data for YoY comparison",
            "Monitor channel mix for optimization opportunities"
        ],
        actions: [
            "<strong>Baseline Establishment:</strong> Continue building FY27 baseline for future YoY tracking.",
            "<strong>Channel Optimization:</strong> Review traffic source mix and identify high-performing channels for scale."
        ]
    },
    Data: {
        highlights: [
            "Strong growth trajectory in Data Cloud adoption",
            "Specialist contribution ramping across regions"
        ],
        lowlights: [
            "Early stage tracking, building baseline metrics",
            "Regional coverage expanding"
        ],
        actions: [
            "<strong>Market Development:</strong> Focus on building awareness and consideration through webinars and content.",
            "<strong>Specialist Enablement:</strong> Continue ramping Digital Specialist coverage."
        ]
    }
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('Health of Cloud app initialized');

    // Track page view
    trackEvent('page_view', { page: 'health_of_cloud' });

    // Load preferences
    // loadSidebarState(); // Disabled to keep sidebar visible
    loadDarkMode();
    loadAdminMode();

    // Update quarter progress
    updateQuarterProgress();

    // Initialize selection banner
    updateSelectionBanner();

    // Initialize Tableau links
    initTableauLinks();

    // Load data
    loadData();
});

// Initialize Tableau links
function initTableauLinks() {
    document.getElementById('regionalTableauLink').href = TABLEAU_LINKS.regional;
    document.getElementById('horsemanTableauLink').href = TABLEAU_LINKS.horseman;
    document.getElementById('trafficTableauLink').href = TABLEAU_LINKS.traffic;
    document.getElementById('offerTableauLink').href = TABLEAU_LINKS.offer;
    document.getElementById('webinarTableauLink').href = TABLEAU_LINKS.webinar;
    document.getElementById('webinarCloudTableauLink').href = TABLEAU_LINKS.webinar;

    // Track clicks
    document.querySelectorAll('.tableau-link').forEach(link => {
        link.addEventListener('click', (e) => {
            const tableName = e.currentTarget.id.replace('TableauLink', '').replace('Cloud', '');
            trackEvent('tableau_link_clicked', { table: tableName });
        });
    });
}

// Calculate and display quarter progress
function updateQuarterProgress() {
    const now = new Date();
    const currentMonth = now.getMonth(); // 0-11
    const currentDay = now.getDate();
    const currentYear = now.getFullYear();

    // Determine current quarter
    let quarter, quarterStart, quarterEnd;
    if (currentMonth >= 3 && currentMonth <= 5) {
        quarter = 'Q2';
        quarterStart = new Date(currentYear, 3, 1); // Apr 1
        quarterEnd = new Date(currentYear, 5, 30); // Jun 30
    } else if (currentMonth >= 0 && currentMonth <= 2) {
        quarter = 'Q1';
        quarterStart = new Date(currentYear, 0, 1); // Jan 1
        quarterEnd = new Date(currentYear, 2, 31); // Mar 31
    } else if (currentMonth >= 6 && currentMonth <= 8) {
        quarter = 'Q3';
        quarterStart = new Date(currentYear, 6, 1); // Jul 1
        quarterEnd = new Date(currentYear, 8, 30); // Sep 30
    } else {
        quarter = 'Q4';
        quarterStart = new Date(currentYear, 9, 1); // Oct 1
        quarterEnd = new Date(currentYear, 11, 31); // Dec 31
    }

    // Calculate days elapsed and total days
    const daysElapsed = Math.floor((now - quarterStart) / (1000 * 60 * 60 * 24));
    const totalDays = Math.floor((quarterEnd - quarterStart) / (1000 * 60 * 60 * 24)) + 1;
    const percentComplete = Math.round((daysElapsed / totalDays) * 100);

    // Format date
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const dateString = `${monthNames[currentMonth]} ${currentDay}, ${currentYear}`;

    // Check if data is stale (more than 25 hours old)
    const lastRefreshHour = 23; // 23:00 CET
    const hoursAgo = (now.getHours() - lastRefreshHour + 24) % 24;
    const isStale = hoursAgo > 25;
    const staleWarning = isStale ? ' ⚠️ <span style="color: #f59e0b;">Data may be outdated</span>' : '';

    // Update quarter progress in header
    const progressEl = document.getElementById('quarterProgress');
    if (progressEl) {
        progressEl.innerHTML = `| ${percentComplete}% of ${quarter} completed${staleWarning}`;
    }

    // Update refresh badge
    const refreshEl = document.getElementById('dataRefreshText');
    if (refreshEl) {
        refreshEl.textContent = 'Daily refresh at 23:00 CET';
    }
}

// Load all data from API
async function loadData() {
    showLoading();
    try {
        // Build leaders parameter based on current region filter
        let leadersParam = '';
        if (currentOUFilter) {
            // Specific OU selected - use only that leader
            const leader = OU_TO_LEADER[currentOUFilter];
            if (leader) {
                leadersParam = `&leaders=${encodeURIComponent(leader)}`;
            }
        } else if (currentRegionFilter === 'EMEA') {
            leadersParam = `&leaders=${encodeURIComponent(EMEA_OUS.join(','))}`;
        } else if (currentRegionFilter === 'AMER') {
            leadersParam = `&leaders=${encodeURIComponent(AMER_OUS.join(','))}`;
        } else {
            // BOTH = pass all 9 leaders (EMEA + AMER)
            const allLeaders = [...EMEA_OUS, ...AMER_OUS];
            leadersParam = `&leaders=${encodeURIComponent(allLeaders.join(','))}`;
        }

        // Convert YTD to Q1,Q2 for Health of Cloud endpoints
        const quartersParam = currentQuarter === 'YTD' ? 'Q1,Q2' : currentQuarter;

        const [regional, horseman, traffic, offer, clouds] = await Promise.all([
            fetch(`${API_BASE}/regional?quarters=${encodeURIComponent(quartersParam)}`).then(r => r.json()),
            fetch(`${API_BASE}/horseman?cloud=${encodeURIComponent(currentCloud)}&quarters=${encodeURIComponent(quartersParam)}${leadersParam}`).then(r => r.json()),
            fetch(`${API_BASE}/traffic?cloud=${encodeURIComponent(currentCloud)}&quarters=${encodeURIComponent(quartersParam)}${leadersParam}`).then(r => r.json()),
            fetch(`${API_BASE}/offer?cloud=${encodeURIComponent(currentCloud)}&quarters=${encodeURIComponent(quartersParam)}${leadersParam}`).then(r => r.json()),
            fetch(`${API_BASE}/clouds`).then(r => r.json())
        ]);

        data = { regional, horseman, traffic, offer, clouds };

        // Debug: Check all unique leaders
        const allLeaders = [...new Set(data.regional.data.map(r => r.leader))];
        console.log('🔍 All unique leaders in data:', allLeaders);
        console.log('🔍 EMEA_OUS configured:', EMEA_OUS);
        console.log('🔍 AMER_OUS configured:', AMER_OUS);

        // Check which leaders are matched
        const emeaMatched = allLeaders.filter(l => EMEA_OUS.some(ou => ou.trim() === l.trim()));
        const amerMatched = allLeaders.filter(l => AMER_OUS.some(ou => ou.trim() === l.trim()));
        const unmatched = allLeaders.filter(l =>
            !EMEA_OUS.some(ou => ou.trim() === l.trim()) &&
            !AMER_OUS.some(ou => ou.trim() === l.trim())
        );

        console.log(`✅ EMEA matched (${emeaMatched.length}):`, emeaMatched);
        console.log(`✅ AMER matched (${amerMatched.length}):`, amerMatched);
        if (unmatched.length > 0) {
            console.warn(`⚠️ Unmatched leaders (${unmatched.length}):`, unmatched);
        }

        // Hide loading, show content
        document.getElementById('loadingState').style.display = 'none';
        showTabContent(currentTab);

        renderScorecard();
    } catch (error) {
        console.error('Error loading data:', error);
    } finally {
        hideLoading();
        document.getElementById('loadingState').innerHTML =
            '<div style="color: #ef4444;">Failed to load data. Make sure the API is running on localhost:8000</div>';
    }
}

// Update active filters display
function updateActiveFilters() {
    // Update cloud
    const cloudEl = document.getElementById('filterCloud');
    if (cloudEl) cloudEl.textContent = currentCloud;

    // Update region
    const regionEl = document.getElementById('filterRegion');
    if (regionEl) {
        if (currentRegionFilter === 'BOTH') {
            regionEl.textContent = 'EMEA + AMER';
        } else {
            regionEl.textContent = currentRegionFilter;
        }
    }

    // Update period (Q2 FY27 hardcoded for now - will be dynamic later)
    const periodEl = document.getElementById('filterPeriod');
    if (periodEl) periodEl.textContent = 'Q2 FY27';

    // Update data freshness
    const freshnessEl = document.getElementById('dataFreshness');
    if (freshnessEl) {
        // Try to get last_refresh.txt timestamp
        fetch('${API_BASE_URL}/api/data/last_refresh')
            .then(r => r.json())
            .then(data => {
                if (data.last_refresh) {
                    freshnessEl.textContent = `Last updated: ${data.last_refresh}`;
                } else {
                    freshnessEl.textContent = 'Last updated: Today at 23:00 CET';
                }
            })
            .catch(() => {
                freshnessEl.textContent = 'Last updated: Today at 23:00 CET';
            });
    }
}

// Render scorecard for current cloud
function renderScorecard() {
    updateActiveFilters();
    renderRegionTable();
    renderHorsemanTable();
    renderTrafficTable();
    renderOfferTable();
    renderInsights();
    renderActions();

    // Log totals for verification
    console.log('🔍 Verifying data consistency...');
    verifyDataConsistency();
}

// Apply conditional formatting for percentage values
function getPerformanceClass(value, type) {
    if (type === 'contrib_diff') {
        // MDP Contrib Diff ppts: negative = red, 0 = orange, positive = green
        if (value < -1) return 'negative';     // Rouge si < -1 ppt
        if (value < 1) return 'neutral';       // Orange si entre -1 et +1 ppt
        return 'positive';                     // Vert si > +1 ppt
    } else if (type === 'yoy') {
        // YoY %: < 0% = red, 0-10% = orange, > 10% = green
        const percent = value * 100;
        if (percent < 0) return 'negative';     // Rouge si négatif
        if (percent < 10) return 'neutral';     // Orange si 0-10%
        return 'positive';                      // Vert si > 10%
    }
    return '';
}

// Sort table by column
function sortTable(tableId, columnIndex) {
    const table = document.getElementById(tableId);
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr:not(.total-row)'));
    const header = table.querySelectorAll('th')[columnIndex];

    // Determine sort direction
    const currentSort = header.classList.contains('sort-asc') ? 'desc' : 'asc';

    // Clear all sort indicators
    table.querySelectorAll('th').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
    });

    // Add sort indicator
    header.classList.add(currentSort === 'asc' ? 'sort-asc' : 'sort-desc');

    // Sort rows
    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();

        // Try to parse as number (remove $, M, K, %, ppts)
        const aNum = parseFloat(aValue.replace(/[$,MKppts%]/g, ''));
        const bNum = parseFloat(bValue.replace(/[$,MKppts%]/g, ''));

        if (!isNaN(aNum) && !isNaN(bNum)) {
            return currentSort === 'asc' ? aNum - bNum : bNum - aNum;
        }

        // String comparison
        return currentSort === 'asc'
            ? aValue.localeCompare(bValue)
            : bValue.localeCompare(aValue);
    });

    // Re-append rows
    rows.forEach(row => tbody.appendChild(row));

    // Re-append total row at the end
    const totalRow = tbody.querySelector('.total-row');
    if (totalRow) tbody.appendChild(totalRow);
}

// Set region filter
async function setRegionFilter(region) {
    currentRegionFilter = region;

    // Update button states
    document.querySelectorAll('.region-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.region === region) {
            btn.classList.add('active');
        }
    });

    // If in OU mode, clicking region doesn't reload data (OU is always one leader)
    if (currentOUFilter) {
        return; // Don't reload data in OU mode
    }

    // Not in OU mode - proceed with region filter change
    currentOUFilter = null; // Reset OU filter when changing region

    // Track region filter change
    trackEvent('region_filter_changed', { region: region });

    // Update button states
    document.querySelectorAll('.region-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.region === region) {
            btn.classList.add('active');
        }
    });

    // Update filter badge
    updateActiveFilters();

    // Reload data for Health of Cloud tab
    if (currentTab === 'health' && data.regional) {
        showLoading();

        try {
            // Build leaders parameter based on new region filter
            let leadersParam = '';
            if (currentRegionFilter === 'EMEA') {
                leadersParam = `&leaders=${encodeURIComponent(EMEA_OUS.join(','))}`;
            } else if (currentRegionFilter === 'AMER') {
                leadersParam = `&leaders=${encodeURIComponent(AMER_OUS.join(','))}`;
            } else {
                // BOTH = pass all 9 leaders
                const allLeaders = [...EMEA_OUS, ...AMER_OUS];
                leadersParam = `&leaders=${encodeURIComponent(allLeaders.join(','))}`;
            }

            // Convert YTD to Q1,Q2 for Health of Cloud endpoints
            const quartersParam = currentQuarter === 'YTD' ? 'Q1,Q2' : currentQuarter;

            // Reload Horseman, Traffic, Offer with new region filter
            const [horseman, traffic, offer] = await Promise.all([
                fetch(`${API_BASE}/horseman?cloud=${encodeURIComponent(currentCloud)}&quarters=${encodeURIComponent(quartersParam)}${leadersParam}`).then(r => r.json()),
                fetch(`${API_BASE}/traffic?cloud=${encodeURIComponent(currentCloud)}&quarters=${encodeURIComponent(quartersParam)}${leadersParam}`).then(r => r.json()),
                fetch(`${API_BASE}/offer?cloud=${encodeURIComponent(currentCloud)}&quarters=${encodeURIComponent(quartersParam)}${leadersParam}`).then(r => r.json())
            ]);

            data.horseman = horseman;
            data.traffic = traffic;
            data.offer = offer;

            // Re-render all tables
            renderScorecard();

            hideLoading();
        } catch (error) {
            console.error('Error reloading data for region filter:', error);
            hideLoading();
        }
    }

    // Reload campaign data if on campaign tab
    if (currentTab === 'campaign') {
        if (currentCampaignTab === 'webinar') {
            webinarData = null; // Reset to force reload
            await loadWebinarData();
        } else if (currentCampaignTab === 'email') {
            emailData = null; // Reset to force reload
            await loadEmailData();
        }
    }

    // Lead tab: Coming soon
    if (currentTab === 'lead') {
        console.log('Lead Scorecard: Coming Soon');
    }
}

function setOUFilter(ouName) {
    currentOUFilter = ouName || null; // Empty string = null (All OUs)

    // Track OU filter change
    trackEvent('ou_filter_changed', { ou: ouName || 'all' });

    // Update dropdown value
    const dropdown = document.getElementById('ouSelector');
    if (dropdown) {
        dropdown.value = ouName || '';
    }

    // Update filter badge
    updateActiveFilters();

    // Re-render tables with OU filter
    if (currentTab === 'health' && data.regional) {
        renderScorecard();
    }
}

// Filter data by region
function filterByRegion(regionalData) {
    // Apply OU filter first if set
    if (currentOUFilter) {
        const targetLeader = OU_TO_LEADER[currentOUFilter];
        if (targetLeader) {
            const filtered = regionalData.filter(r => {
                const leaderNorm = (r.leader || '').trim();
                return leaderNorm === targetLeader.trim();
            });
            console.log(`🔍 OU filter (${currentOUFilter}): ${filtered.length} rows matched`);
            return filtered;
        }
    }

    // Otherwise apply region filter
    if (currentRegionFilter === 'BOTH') {
        // BOTH = EMEA + AMER only (exclude other leaders)
        const allValidOUs = [...EMEA_OUS, ...AMER_OUS];
        const filtered = regionalData.filter(r => {
            const leaderNorm = (r.leader || '').trim();
            return allValidOUs.some(ou => ou.trim() === leaderNorm);
        });
        console.log(`🔍 BOTH filter: ${filtered.length} rows matched (EMEA + AMER only)`);
        return filtered;
    }

    if (currentRegionFilter === 'EMEA') {
        const filtered = regionalData.filter(r => {
            // Normalize: trim spaces and compare
            const leaderNorm = (r.leader || '').trim();
            return EMEA_OUS.some(ou => ou.trim() === leaderNorm);
        });
        console.log(`🔍 EMEA filter: ${filtered.length} rows matched`);
        return filtered;
    } else if (currentRegionFilter === 'AMER') {
        const filtered = regionalData.filter(r => {
            // Normalize: trim spaces and compare
            const leaderNorm = (r.leader || '').trim();
            return AMER_OUS.some(ou => ou.trim() === leaderNorm);
        });
        console.log(`🔍 AMER filter: ${filtered.length} rows matched`);
        return filtered;
    }

    return regionalData;
}

// Render MDP by Region table - REAL DATA ONLY
function renderRegionTable() {
    const table = document.getElementById('regionTable');

    let regionalData;

    // In OU mode: show all clouds for this OU (no cloud filter)
    if (currentOUFilter) {
        regionalData = data.regional.data;
        // Filter to show only configured visible clouds for OU mode
        regionalData = regionalData.filter(r => ouModeVisibleClouds.includes(r.cloud));
        console.log(`📊 OU Mode: showing ${regionalData.length} visible clouds for OU`);
    } else {
        // In Cloud mode: filter by current cloud
        regionalData = data.regional.data.filter(r => r.cloud === currentCloud);
        console.log(`📊 Cloud Mode: ${regionalData.length} rows for Cloud: ${currentCloud}`);

        // Apply region filter
        regionalData = filterByRegion(regionalData);
        console.log(`📊 After region filter (${currentRegionFilter}): ${regionalData.length} rows`);
        console.log('Leaders in filtered data:', regionalData.map(r => r.leader));
    }

    // Update table title based on context
    const titleElement = document.getElementById('regionTableTitle');
    if (titleElement) {
        titleElement.textContent = currentOUFilter ? 'MDP by Cloud' : 'MDP by Region';
    }

    // Change header based on context
    const headerLabel = currentOUFilter ? 'Cloud' : 'Region';

    let html = `
        <thead>
            <tr>
                <th class="sortable" onclick="sortTable('regionTable', 0)" style="width: 35%;">${headerLabel}</th>
                <th class="sortable" onclick="sortTable('regionTable', 1)" style="width: 25%;">Current FY MDP</th>
                <th class="sortable" onclick="sortTable('regionTable', 2)" style="width: 20%;">% YoY</th>
                <th class="sortable" onclick="sortTable('regionTable', 3)" style="width: 20%;">CFY Contrib</th>
            </tr>
        </thead>
        <tbody>
    `;

    let totalMDP = 0;
    regionalData.forEach(row => {
        totalMDP += row.mdp;
    });

    regionalData.forEach(row => {
        const yoyValue = row.yoy_change || 0;
        const yoySign = yoyValue >= 0 ? '+' : '';
        const yoyClass = getPerformanceClass(yoyValue, 'yoy');

        // Use REAL data from CSV (already in decimal format: 0.29 = 29%)
        // If contribution exists, use it directly (already a decimal), otherwise calculate
        const cfyContrib = row.contribution !== null && row.contribution !== undefined
            ? row.contribution
            : (row.mdp / totalMDP);

        const contribDiff = row.contribution_diff || 0;
        const contribDiffSign = contribDiff >= 0 ? '+' : '';
        const contribDiffClass = getPerformanceClass(contribDiff, 'contrib_diff');

        // Display Cloud when in OU mode, otherwise OU/Leader name
        let displayName;
        if (currentOUFilter) {
            // In OU mode: show Cloud name
            displayName = row.cloud || row.leader;
        } else {
            // In Cloud mode: show OU name or leader
            const ouName = LEADER_TO_OU[row.leader] || row.leader;
            displayName = ouName;
        }

        html += `
            <tr>
                <td>${displayName}</td>
                <td class="number-cell">${formatCurrency(row.mdp)}</td>
                <td class="number-cell ${yoyClass}">${row.yoy_change !== null ? yoySign + (yoyValue * 100).toFixed(0) + '%' : '-'}</td>
                <td class="number-cell">${(cfyContrib * 100).toFixed(1)}%</td>
            </tr>
        `;
    });

    // Total row - Calculate true YoY from actual data
    let totalMDPLastYear = 0;
    regionalData.forEach(row => {
        const yoyChange = row.yoy_change || 0;
        const mdpLastYear = row.mdp / (1 + yoyChange);
        totalMDPLastYear += mdpLastYear;
    });
    const trueYoY = totalMDPLastYear > 0 ? (totalMDP - totalMDPLastYear) / totalMDPLastYear : 0;
    const yoyClass = trueYoY >= 0 ? 'positive' : 'negative';
    const yoySign = trueYoY >= 0 ? '+' : '';

    // Store global YoY for use in other tables
    window.globalYoY = trueYoY;

    html += `
        <tr class="total-row">
            <td style="font-weight: 700;"><strong>Grand Total</strong></td>
            <td class="number-cell" style="font-weight: 700;">${formatCurrency(totalMDP)}</td>
            <td class="number-cell ${yoyClass}" style="font-weight: 700;">${yoySign}${(trueYoY * 100).toFixed(1)}%</td>
            <td class="number-cell" style="font-weight: 700;">-</td>
        </tr>
    `;

    html += '</tbody>';
    table.innerHTML = html;
}

// Render MDP by Horseman table - REAL DATA ONLY
function renderHorsemanTable() {
    const table = document.getElementById('horsemanTable');

    const horsemanData = data.horseman.breakdown;
    const total = data.horseman.total.mdp;

    let html = `
        <thead>
            <tr>
                <th class="sortable" onclick="sortTable('horsemanTable', 0)" style="width: 35%;">Opp Source</th>
                <th class="sortable" onclick="sortTable('horsemanTable', 1)" style="width: 25%;">Current FY MDP</th>
                <th class="sortable" onclick="sortTable('horsemanTable', 2)" style="width: 20%;">% YoY</th>
                <th class="sortable" onclick="sortTable('horsemanTable', 3)" style="width: 20%;">% MDP Share</th>
            </tr>
        </thead>
        <tbody>
    `;

    // Order: AE, BDR, Specialist, ECS
    const order = ['AE', 'BDR', 'Specialist', 'ECS'];
    order.forEach(key => {
        if (horsemanData[key]) {
            const row = horsemanData[key];

            // Use REAL data from CSV
            const yoy = row.yoy_change || 0;
            const yoySign = yoy >= 0 ? '+' : '';
            const yoyClass = getPerformanceClass(yoy, 'yoy');

            // Calculate MDP Share locally (CSV values are based on global total)
            const share = (row.mdp / total) * 100;

            // MDP Share Diff should be in CSV as 'MDP Share Diff vs FY-1 (ppts)'
            const shareDiff = row.share_diff || 0;
            const shareDiffSign = shareDiff >= 0 ? '+' : '';
            const shareDiffClass = getPerformanceClass(shareDiff, 'contrib_diff');

            html += `
                <tr>
                    <td>${key}</td>
                    <td class="number-cell">${formatCurrency(row.mdp)}</td>
                    <td class="number-cell ${yoyClass}">${yoySign}${(yoy * 100).toFixed(1)}%</td>
                    <td class="number-cell">${share.toFixed(1)}%</td>
                </tr>
            `;
        }
    });

    // Total row - Use global YoY from Regional table
    const globalYoY = window.globalYoY || 0;
    const yoyClass = globalYoY >= 0 ? 'positive' : 'negative';
    const yoySign = globalYoY >= 0 ? '+' : '';

    html += `
        <tr class="total-row">
            <td style="font-weight: 700;"><strong>Grand Total</strong></td>
            <td class="number-cell" style="font-weight: 700;">${formatCurrency(total)}</td>
            <td class="number-cell ${yoyClass}" style="font-weight: 700;">${yoySign}${(globalYoY * 100).toFixed(1)}%</td>
            <td class="number-cell" style="font-weight: 700;">100%</td>
        </tr>
    `;

    html += '</tbody>';
    table.innerHTML = html;
}

// Render MDP by Traffic Source table - WITH L1+L2 HIERARCHY
function renderTrafficTable() {
    const table = document.getElementById('trafficTable');

    // Safety check: ensure data is loaded
    if (!data.traffic || !data.traffic.breakdown) {
        table.innerHTML = '<tbody><tr><td colspan="6">Loading traffic data...</td></tr></tbody>';
        return;
    }

    const trafficData = data.traffic.breakdown;
    const total = data.traffic.total.mdp;

    // Sort L1 by MDP descending
    const sortedL1 = Object.entries(trafficData)
        .sort((a, b) => b[1].mdp - a[1].mdp);

    let html = `
        <thead>
            <tr>
                <th style="width: 35%;">Traffic Source</th>
                <th style="width: 25%;">Current FY MDP</th>
                <th style="width: 20%;">% YoY</th>
                <th style="width: 20%;">% MDP Share</th>
            </tr>
        </thead>
        <tbody>
    `;

    sortedL1.forEach(([sourceL1, l1Data]) => {
        const share = (l1Data.mdp / total) * 100;
        const yoyClass = l1Data.yoy_change > 0 ? 'positive' : l1Data.yoy_change < 0 ? 'negative' : '';
        const yoyDisplay = l1Data.yoy_change != null ? formatPercent(l1Data.yoy_change) : '-';
        // Calculate MDP Share locally (CSV values are based on global total, not filtered subset)
        const mdpShareDisplay = share > 0 ? `${share.toFixed(1)}%` : '-';
        const shareDiffClass = l1Data.share_diff > 0 ? 'positive' : l1Data.share_diff < 0 ? 'negative' : '';
        // Share Diff from CSV is in decimal format - need to multiply by 100 for ppts
        // However, these values are based on global total and may be very small
        const shareDiffDisplay = l1Data.share_diff != null ? `${l1Data.share_diff >= 0 ? '+' : ''}${(l1Data.share_diff * 100).toFixed(1)} ppts` : '-';

        // L1 row (BOLD)
        html += `
            <tr style="font-weight: 600; background-color: rgba(0,0,0,0.02);">
                <td><strong>${sourceL1}</strong></td>
                <td class="number-cell">${formatCurrency(l1Data.mdp)}</td>
                <td class="number-cell ${yoyClass}">${yoyDisplay}</td>
                <td class="number-cell">${mdpShareDisplay}</td>
            </tr>
        `;

        // L2 children (indented)
        if (l1Data.children && Object.keys(l1Data.children).length > 0) {
            const sortedL2 = Object.entries(l1Data.children)
                .sort((a, b) => b[1].mdp - a[1].mdp);

            sortedL2.forEach(([sourceL2, l2Data]) => {
                const l2Share = (l2Data.mdp / total) * 100;
                const l2YoyClass = l2Data.yoy_change > 0 ? 'positive' : l2Data.yoy_change < 0 ? 'negative' : '';
                const l2YoyDisplay = l2Data.yoy_change != null ? formatPercent(l2Data.yoy_change) : '-';
                // Calculate L2 MDP Share locally
                const l2MdpShareDisplay = l2Share > 0 ? `${l2Share.toFixed(1)}%` : '-';
                const l2ShareDiffClass = l2Data.share_diff > 0 ? 'positive' : l2Data.share_diff < 0 ? 'negative' : '';
                const l2ShareDiffDisplay = l2Data.share_diff != null ? `${l2Data.share_diff >= 0 ? '+' : ''}${(l2Data.share_diff * 100).toFixed(1)} ppts` : '-';

                html += `
                    <tr style="font-size: 0.95em;">
                        <td style="padding-left: 40px !important;">↳ ${sourceL2}</td>
                        <td class="number-cell">${formatCurrency(l2Data.mdp)}</td>
                        <td class="number-cell ${l2YoyClass}">${l2YoyDisplay}</td>
                        <td class="number-cell">${l2MdpShareDisplay}</td>
                    </tr>
                `;
            });

        }
    });

    // Total row - Use global YoY from Regional table
    const globalYoY = window.globalYoY || 0;
    const yoyClass = globalYoY >= 0 ? 'positive' : 'negative';
    const yoySign = globalYoY >= 0 ? '+' : '';

    html += `
        <tr class="total-row">
            <td><strong>Grand Total</strong></td>
            <td class="number-cell" style="font-weight: 700;">${formatCurrency(total)}</td>
            <td class="number-cell ${yoyClass}" style="font-weight: 700;">${yoySign}${(globalYoY * 100).toFixed(1)}%</td>
            <td class="number-cell" style="font-weight: 700;">100%</td>
        </tr>
    `;

    html += '</tbody>';
    table.innerHTML = html;
}

// Quarter filter function
async function setFiscalYearFilter(fiscalYear) {
    showLoading();
    currentFiscalYear = fiscalYear;

    // Track fiscal year filter change
    trackEvent('fiscal_year_filter_changed', { fiscal_year: fiscalYear });

    // Update active button
    document.querySelectorAll('[data-fy]').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.fy === fiscalYear) {
            btn.classList.add('active');
        }
    });

    // Save current view title to restore after reload
    const currentTitle = document.getElementById('currentCloud')?.textContent;

    // Reload data - use OU data loader if in OU mode
    if (currentOUFilter) {
        const leader = OU_TO_LEADER[currentOUFilter];
        if (leader) {
            await loadOUData(leader);
        }
    } else {
        await loadData();
    }

    // Restore title if it was changed
    if (currentTitle && currentOUFilter) {
        document.getElementById('currentCloud').textContent = currentTitle;
    }

    // Reload Lead Cockpit if on lead tab
    if (currentTab === 'lead') {
        await loadLeadCockpitData();
    }

    // Reload Email if on campaign > email tab
    if (currentTab === 'campaign' && currentCampaignTab === 'email') {
        await loadEmailData();
    }

    // Reload Webinar if on campaign > webinar tab
    if (currentTab === 'campaign' && currentCampaignTab === 'webinar') {
        await loadWebinarData();
    }

    hideLoading();
}

async function setQuarterFilter(quarter) {
    showLoading();
    currentQuarter = quarter;

    // Track quarter filter change
    trackEvent('quarter_filter_changed', { quarter: quarter });

    // Update active button
    document.querySelectorAll('[data-quarter]').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.quarter === quarter) {
            btn.classList.add('active');
        }
    });

    // Save current view title to restore after reload
    const currentTitle = document.getElementById('currentCloud')?.textContent;

    // Reload data - use OU data loader if in OU mode
    if (currentOUFilter) {
        const leader = OU_TO_LEADER[currentOUFilter];
        if (leader) {
            await loadOUData(leader);
        }
    } else {
        await loadData();
    }

    // Restore title if it was changed
    if (currentTitle && currentOUFilter) {
        document.getElementById('currentCloud').textContent = currentTitle;
    } else if (currentTitle && currentCloud) {
        document.getElementById('currentCloud').textContent = currentTitle;
    }

    // Reload campaign data if on campaign tab
    if (currentTab === 'campaign') {
        if (currentCampaignTab === 'webinar') {
            webinarData = null; // Reset to force reload
            await loadWebinarData();
        } else if (currentCampaignTab === 'email') {
            emailData = null; // Reset to force reload
            await loadEmailData();
        }
    }

    // Lead tab: Coming soon
    if (currentTab === 'lead') {
        console.log('Lead Scorecard: Coming Soon');
    }

    hideLoading();
}

// Make functions available globally
window.sortTable = sortTable;
window.setRegionFilter = setRegionFilter;
window.setQuarterFilter = setQuarterFilter;

// Render MDP by Offer table - WITH L1+L2 HIERARCHY
function renderOfferTable() {
    const table = document.getElementById('offerTable');

    // Safety check: ensure data is loaded
    if (!data.offer || !data.offer.breakdown) {
        table.innerHTML = '<tbody><tr><td colspan="6">Loading offer data...</td></tr></tbody>';
        return;
    }

    const offerData = data.offer.breakdown;
    // Use Horseman total (already filtered by visible clouds) as reference
    // Offer may miss uncategorized deals, so we use Horseman as the true total
    const referenceTotal = data.horseman?.total?.mdp || data.offer.total.mdp;
    const totalMDP = referenceTotal;

    // Sort L1 by MDP descending
    const sortedL1 = Object.entries(offerData)
        .sort((a, b) => b[1].mdp - a[1].mdp);

    let html = `
        <thead>
            <tr>
                <th style="width: 35%;">Offer Grouping</th>
                <th style="width: 25%;">Current FY MDP</th>
                <th style="width: 20%;">% YoY</th>
                <th style="width: 20%;">% MDP Share</th>
            </tr>
        </thead>
        <tbody>
    `;

    sortedL1.forEach(([offerL1, l1Data]) => {
        const share = (l1Data.mdp / totalMDP) * 100;
        const yoyClass = l1Data.yoy_change > 0 ? 'positive' : l1Data.yoy_change < 0 ? 'negative' : '';
        const yoyDisplay = l1Data.yoy_change != null ? formatPercent(l1Data.yoy_change) : '-';
        // Calculate MDP Share locally
        const mdpShareDisplay = share > 0 ? `${share.toFixed(1)}%` : '-';
        const shareDiffClass = l1Data.share_diff > 0 ? 'positive' : l1Data.share_diff < 0 ? 'negative' : '';
        const shareDiffDisplay = l1Data.share_diff != null ? `${l1Data.share_diff >= 0 ? '+' : ''}${(l1Data.share_diff * 100).toFixed(1)} ppts` : '-';

        // L1 row (BOLD)
        html += `
            <tr style="font-weight: 600; background-color: rgba(0,0,0,0.02);">
                <td><strong>${offerL1}</strong></td>
                <td class="number-cell">${formatCurrency(l1Data.mdp)}</td>
                <td class="number-cell ${yoyClass}">${yoyDisplay}</td>
                <td class="number-cell">${mdpShareDisplay}</td>
            </tr>
        `;

        // L2 children (indented) - if any
        if (l1Data.children && Object.keys(l1Data.children).length > 0) {
            const sortedL2 = Object.entries(l1Data.children)
                .sort((a, b) => b[1].mdp - a[1].mdp);

            sortedL2.forEach(([offerL2, l2Data]) => {
                const l2Share = (l2Data.mdp / totalMDP) * 100;
                const l2YoyClass = l2Data.yoy_change > 0 ? 'positive' : l2Data.yoy_change < 0 ? 'negative' : '';
                const l2YoyDisplay = l2Data.yoy_change != null ? formatPercent(l2Data.yoy_change) : '-';
                // Calculate L2 MDP Share locally
                const l2MdpShareDisplay = l2Share > 0 ? `${l2Share.toFixed(1)}%` : '-';
                const l2ShareDiffClass = l2Data.share_diff > 0 ? 'positive' : l2Data.share_diff < 0 ? 'negative' : '';
                const l2ShareDiffDisplay = l2Data.share_diff != null ? `${l2Data.share_diff >= 0 ? '+' : ''}${(l2Data.share_diff * 100).toFixed(1)} ppts` : '-';

                html += `
                    <tr style="font-size: 0.95em;">
                        <td style="padding-left: 40px !important;">↳ ${offerL2}</td>
                        <td class="number-cell">${formatCurrency(l2Data.mdp)}</td>
                        <td class="number-cell ${l2YoyClass}">${l2YoyDisplay}</td>
                        <td class="number-cell">${l2MdpShareDisplay}</td>
                    </tr>
                `;
            });
        }
    });

    // Total row - Use global YoY (includes ALL deals, even those without Offer category)
    const globalYoY = window.globalYoY || 0;
    const yoyClass = globalYoY >= 0 ? 'positive' : 'negative';
    const yoySign = globalYoY >= 0 ? '+' : '';

    html += `
        <tr class="total-row">
            <td><strong>Grand Total</strong></td>
            <td class="number-cell" style="font-weight: 700;">${formatCurrency(totalMDP)}</td>
            <td class="number-cell ${yoyClass}" style="font-weight: 700;">${yoySign}${(globalYoY * 100).toFixed(1)}%</td>
            <td class="number-cell" style="font-weight: 700;">100%</td>
        </tr>
    `;

    html += '</tbody>';
    table.innerHTML = html;
}

// Render Insights
function renderInsights() {
    const insights = CLOUD_INSIGHTS[currentCloud] || CLOUD_INSIGHTS.Service;

    // Highlights
    const highlightsList = document.getElementById('highlightsList');
    highlightsList.innerHTML = insights.highlights
        .map(h => `<li class="insight-item">${h}</li>`)
        .join('');

    // Lowlights
    const lowlightsList = document.getElementById('lowlightsList');
    lowlightsList.innerHTML = insights.lowlights
        .map(l => `<li class="insight-item">${l}</li>`)
        .join('');
}

// Render Actions
function renderActions() {
    const insights = CLOUD_INSIGHTS[currentCloud] || CLOUD_INSIGHTS.Service;

    const actionsList = document.getElementById('actionsList');
    actionsList.innerHTML = insights.actions
        .map(a => `<li class="action-item">${a}</li>`)
        .join('');
}

// Format currency
function formatCurrency(value) {
    if (!value) return '$0';
    if (value >= 1000000000) {
        return `$${(value / 1000000000).toFixed(1)}B`;
    }
    if (value >= 1000000) {
        return `$${(value / 1000000).toFixed(1)}M`;
    }
    return `$${(value / 1000).toFixed(0)}K`;
}

function formatPercent(value) {
    if (value == null) return '-';
    const percent = (value * 100).toFixed(0);
    return value >= 0 ? `+${percent}%` : `${percent}%`;
}

// Theme toggle
// Dark Mode Toggle
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const isCollapsed = sidebar.classList.toggle('collapsed');

    // Save to localStorage
    try {
        localStorage.setItem('scorecard_sidebar_collapsed', isCollapsed ? '1' : '0');
    } catch (e) {
        console.error('Failed to save sidebar state:', e);
    }
}

function toggleDarkMode() {
    const isDark = document.body.classList.toggle('dark');

    // Update icon and label
    const icon = document.getElementById('darkModeIcon');
    const label = document.getElementById('darkModeLabel');
    if (icon) icon.textContent = isDark ? '☀' : '☾';
    if (label) label.textContent = isDark ? 'Light Mode' : 'Dark Mode';

    // Save to localStorage
    try {
        localStorage.setItem('scorecard_dark_mode', isDark ? '1' : '0');
    } catch (e) {
        console.error('Failed to save dark mode preference:', e);
    }
}

// Load sidebar state on init
function loadSidebarState() {
    try {
        const isCollapsed = localStorage.getItem('scorecard_sidebar_collapsed') === '1';
        if (isCollapsed) {
            const sidebar = document.querySelector('.sidebar');
            if (sidebar) sidebar.classList.add('collapsed');
        }
    } catch (e) {
        console.error('Failed to load sidebar state:', e);
    }
}

// Load dark mode preference on init
function loadDarkMode() {
    try {
        const isDark = localStorage.getItem('scorecard_dark_mode') === '1';
        if (isDark) {
            document.body.classList.add('dark');
            const icon = document.getElementById('darkModeIcon');
            const label = document.getElementById('darkModeLabel');
            if (icon) icon.textContent = '☀';
            if (label) label.textContent = 'Light Mode';
        }
    } catch (e) {
        console.error('Failed to load dark mode preference:', e);
    }
}

// ==========================================
// ADMIN MODE & AUTHENTICATION
// ==========================================

const ADMIN_PASSWORD = 'admin'; // Change this to your desired password
let isAdminMode = false;
let isAdminAuthenticated = false; // New: tracks if user has entered correct password this session

function toggleAdminMode() {
    // If trying to activate admin mode, require password
    if (!isAdminMode) {
        // Show login modal instead of browser prompt
        showAdminLoginModal();
        return;
    }

    // If deactivating, just deactivate (no password needed)
    deactivateAdminMode();
}

function showAdminLoginModal() {
    const modal = document.getElementById('adminLoginModal');
    const input = document.getElementById('adminPasswordInput');
    const error = document.getElementById('adminLoginError');

    modal.style.display = 'flex';
    error.style.display = 'none';
    input.value = '';

    // Focus on input after modal opens
    setTimeout(() => input.focus(), 100);
}

function closeAdminLoginModal() {
    const modal = document.getElementById('adminLoginModal');
    modal.style.display = 'none';
}

function submitAdminLogin() {
    const input = document.getElementById('adminPasswordInput');
    const error = document.getElementById('adminLoginError');
    const password = input.value;

    if (password === ADMIN_PASSWORD) {
        // Password correct!
        isAdminAuthenticated = true;
        activateAdminMode();
        closeAdminLoginModal();
        console.log('✅ Admin password verified');

        // If login was triggered from Admin Settings button, go to admin tab
        switchTab('admin');
    } else {
        // Password incorrect
        error.style.display = 'block';
        input.value = '';
        input.focus();

        // Shake animation
        input.style.animation = 'shake 0.5s';
        setTimeout(() => input.style.animation = '', 500);
    }
}

function activateAdminMode() {
    isAdminMode = true;

    // Update sidebar button
    const sidebarBtn = document.getElementById('adminModeSidebarBtn');
    const sidebarLabel = document.getElementById('adminModeSidebarLabel');

    // Update top-bar badge
    const topBarBadge = document.getElementById('userBadgeTopBar');
    const topBarIcon = document.getElementById('userBadgeIcon');
    const topBarText = document.getElementById('userBadgeText');

    // Show Admin Settings in sidebar
    const adminSection = document.getElementById('adminSidebarSection');
    if (adminSection) adminSection.style.display = 'block';

    // Sidebar
    if (sidebarBtn) {
        sidebarBtn.style.background = 'rgba(245, 158, 11, 0.2)';
        sidebarBtn.style.borderColor = 'rgba(245, 158, 11, 0.5)';
    }
    if (sidebarLabel) sidebarLabel.textContent = 'Deactivate Admin Mode';

    // Top-bar
    if (topBarBadge) topBarBadge.classList.add('admin');
    if (topBarIcon) topBarIcon.textContent = '⚡';
    if (topBarText) topBarText.textContent = 'Admin';

    console.log('🔓 Admin mode activated');

    // Save to localStorage
    saveAdminMode();
}

function deactivateAdminMode() {
    isAdminMode = false;
    isAdminAuthenticated = false; // Reset authentication

    // Update sidebar button
    const sidebarBtn = document.getElementById('adminModeSidebarBtn');
    const sidebarLabel = document.getElementById('adminModeSidebarLabel');

    // Update top-bar badge
    const topBarBadge = document.getElementById('userBadgeTopBar');
    const topBarIcon = document.getElementById('userBadgeIcon');
    const topBarText = document.getElementById('userBadgeText');

    // Hide Admin Settings in sidebar
    const adminSection = document.getElementById('adminSidebarSection');
    if (adminSection) adminSection.style.display = 'none';

    // Sidebar
    if (sidebarBtn) {
        sidebarBtn.style.background = 'rgba(255,255,255,0.05)';
        sidebarBtn.style.borderColor = 'rgba(255,255,255,0.1)';
    }
    if (sidebarLabel) sidebarLabel.textContent = 'Activate Admin Mode';

    // Top-bar
    if (topBarBadge) topBarBadge.classList.remove('admin');
    if (topBarIcon) topBarIcon.textContent = '👤';
    if (topBarText) topBarText.textContent = 'Guest';

    // If currently on admin tab, switch back to health
    if (currentTab === 'admin') {
        switchTab('health');
    }

    console.log('🔒 Admin mode deactivated');

    // Save to localStorage
    saveAdminMode();
}

function openAdminSettings() {
    // When clicking Admin Settings in sidebar, always ask for password
    // (even if admin mode is active, for extra security)
    showAdminLoginModal();
}

function saveAdminMode() {
    try {
        localStorage.setItem('scorecard_admin_mode', isAdminMode ? '1' : '0');
    } catch (e) {
        console.error('Failed to save admin mode preference:', e);
    }
}

// Load admin mode preference on init
function loadAdminMode() {
    try {
        const savedAdminMode = localStorage.getItem('scorecard_admin_mode') === '1';

        if (savedAdminMode) {
            // Admin mode was active previously, but DON'T auto-activate
            // User must re-authenticate with password
            isAdminMode = false;
            isAdminAuthenticated = false;

            // Keep UI in guest mode
            const sidebarBtn = document.getElementById('adminModeSidebarBtn');
            const sidebarLabel = document.getElementById('adminModeSidebarLabel');
            if (sidebarBtn) {
                sidebarBtn.style.background = 'rgba(255,255,255,0.05)';
                sidebarBtn.style.borderColor = 'rgba(255,255,255,0.1)';
            }
            if (sidebarLabel) sidebarLabel.textContent = 'Activate Admin Mode';

            // Top-bar stays in guest mode
            const topBarBadge = document.getElementById('userBadgeTopBar');
            const topBarIcon = document.getElementById('userBadgeIcon');
            const topBarText = document.getElementById('userBadgeText');
            if (topBarBadge) topBarBadge.classList.remove('admin');
            if (topBarIcon) topBarIcon.textContent = '👤';
            if (topBarText) topBarText.textContent = 'Guest';

            // Admin Settings button stays hidden
            const adminSection = document.getElementById('adminSidebarSection');
            if (adminSection) adminSection.style.display = 'none';

            console.log('🔒 Admin mode available but requires authentication');
        }
    } catch (e) {
        console.error('Failed to load admin mode preference:', e);
    }
}

// Export Snapshot to Google Slides
function exportSnapshot() {
    alert('📸 Export to Google Slides\n\nFeature coming soon!\n\nThis will:\n1. Capture current scorecard view\n2. Generate Google Slides format\n3. Append to your deck\n\nStay tuned! 🚀');

    // TODO: Implement actual export
    // 1. Capture current filters (cloud, region, period)
    // 2. Take screenshot or export table data
    // 3. Use Google Slides API to create/append slide
    // 4. Format with Salesforce branding

    console.log('Export requested:', {
        cloud: currentCloud,
        region: currentRegionFilter,
        timestamp: new Date().toISOString()
    });
}

// Toggle sidebar sections
function toggleSection(section) {
    const sectionEl = document.getElementById(`${section}-section`);
    const toggle = event.target;

    if (sectionEl.style.display === 'none') {
        sectionEl.style.display = 'block';
        toggle.classList.add('expanded');
    } else {
        sectionEl.style.display = 'none';
        toggle.classList.remove('expanded');
    }
}

// Update selection banner
function updateSelectionBanner() {
    const banner = document.getElementById('selectionBanner');
    const cloudSelection = document.getElementById('cloudSelection');
    const ouSelection = document.getElementById('ouSelection');
    const selectedCloudName = document.getElementById('selectedCloudName');
    const selectedCloudIcon = document.getElementById('selectedCloudIcon');
    const selectedOUName = document.getElementById('selectedOUName');

    // Check if we're in Cloud Mode or OU Mode
    const isCloudMode = currentCloud && !currentOUFilter;
    const isOUMode = currentOUFilter;

    if (isCloudMode) {
        // Show banner with selected cloud
        banner.classList.remove('hidden');
        cloudSelection.style.display = 'flex';
        ouSelection.style.display = 'none';
        selectedCloudName.textContent = currentCloud;

        // Update cloud icon/logo
        const logoUrl = CLOUD_LOGOS[currentCloud];
        if (logoUrl && logoUrl.startsWith('http')) {
            // Use SVG logo
            selectedCloudIcon.innerHTML = `<img src="${logoUrl}" alt="${currentCloud}" style="width: 24px; height: 24px;">`;
        } else {
            // Use emoji fallback
            selectedCloudIcon.textContent = logoUrl || '☁️';
        }
    } else if (isOUMode) {
        // Show banner with selected OU
        banner.classList.remove('hidden');
        cloudSelection.style.display = 'none';
        ouSelection.style.display = 'flex';
        selectedOUName.textContent = currentOUFilter;
    } else {
        // Hide banner - showing all clouds
        banner.classList.add('hidden');
    }
}

// Select cloud
async function selectCloud(cloudName) {
    currentCloud = cloudName;
    currentOUFilter = null; // Reset OU filter when switching to Cloud mode

    // Reset region filter to BOTH (show all OUs)
    // Update the active button in the UI
    document.querySelectorAll('[data-region]').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector('[data-region="BOTH"]')?.classList.add('active');
    currentRegionFilter = 'BOTH';

    document.getElementById('currentCloud').textContent = cloudName;

    // Track cloud selection
    trackEvent('cloud_selected', { cloud: cloudName });

    // Reload Lead Cockpit if on lead tab
    if (currentTab === 'lead') {
        await loadLeadCockpitData();
    }

    // Reload Email if on campaign > email tab
    if (currentTab === 'campaign' && currentCampaignTab === 'email') {
        await loadEmailData();
    }

    // Update active state in sidebar
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    // Find and activate the cloud nav item by matching the onclick attribute
    const cloudItems = document.querySelectorAll('.nav-subitem');
    cloudItems.forEach(item => {
        const onclick = item.getAttribute('onclick');
        if (onclick && onclick.includes(`selectCloud('${cloudName}')`)) {
            item.classList.add('active');
        }
    });

    // Reload ALL data for new cloud
    try {
        // Build leaders parameter based on current region filter
        let leadersParam = '';
        if (currentOUFilter) {
            // Specific OU selected - use only that leader
            const leader = OU_TO_LEADER[currentOUFilter];
            if (leader) {
                leadersParam = `&leaders=${encodeURIComponent(leader)}`;
            }
        } else if (currentRegionFilter === 'EMEA') {
            leadersParam = `&leaders=${encodeURIComponent(EMEA_OUS.join(','))}`;
        } else if (currentRegionFilter === 'AMER') {
            leadersParam = `&leaders=${encodeURIComponent(AMER_OUS.join(','))}`;
        } else {
            // BOTH = pass all 9 leaders (EMEA + AMER)
            const allLeaders = [...EMEA_OUS, ...AMER_OUS];
            leadersParam = `&leaders=${encodeURIComponent(allLeaders.join(','))}`;
        }

        // Convert YTD to Q1,Q2 for Health of Cloud endpoints
        const quartersParam = currentQuarter === 'YTD' ? 'Q1,Q2' : currentQuarter;

        const [regional, horseman, traffic, offer] = await Promise.all([
            fetch(`${API_BASE}/regional?cloud=${encodeURIComponent(currentCloud)}&quarters=${encodeURIComponent(quartersParam)}`).then(r => r.json()),
            fetch(`${API_BASE}/horseman?cloud=${encodeURIComponent(currentCloud)}&quarters=${encodeURIComponent(quartersParam)}${leadersParam}`).then(r => r.json()),
            fetch(`${API_BASE}/traffic?cloud=${encodeURIComponent(currentCloud)}&quarters=${encodeURIComponent(quartersParam)}${leadersParam}`).then(r => r.json()),
            fetch(`${API_BASE}/offer?cloud=${encodeURIComponent(currentCloud)}&quarters=${encodeURIComponent(quartersParam)}${leadersParam}`).then(r => r.json())
        ]);

        data.regional = regional;
        data.horseman = horseman;
        data.traffic = traffic;
        data.offer = offer;
    } catch (error) {
        console.error('Error reloading cloud-specific data:', error);
    }

    // Update selection banner
    updateSelectionBanner();

    // Re-render current tab with new cloud
    if (currentTab === 'health') {
        renderScorecard();
    } else if (currentTab === 'lead') {
        // TODO: Load lead data for this cloud
    } else if (currentTab === 'campaign') {
        // Reload campaign data and re-render
        if (currentCampaignTab === 'webinar') {
            webinarData = null;
            await loadWebinarData();
        } else if (currentCampaignTab === 'email') {
            emailData = null;
            await loadEmailData();
        }
    }
}

// Switch between tabs
function switchTab(tab) {
    currentTab = tab;

    // Update tab active state
    document.querySelectorAll('.tab-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tab}"]`).classList.add('active');

    // Update header
    const headers = {
        health: { icon: '🏥', title: 'Health of the Cloud Scorecard' },
        lead: { icon: '🎯', title: 'Lead Scorecard' },
        campaign: { icon: '📧', title: 'Campaign Scorecard' },
        admin: { icon: '🔐', title: 'Admin Dashboard' }
    };
    if (headers[tab]) {
        document.getElementById('headerIcon').textContent = headers[tab].icon;
        document.getElementById('headerTitle').textContent = headers[tab].title;
    }

    // Show correct content
    showTabContent(tab);

    // Load/reload data when switching tabs to ensure correct quarter
    if (tab === 'health') {
        if (currentOUFilter) {
            const leader = OU_TO_LEADER[currentOUFilter];
            if (leader) {
                setTimeout(() => loadOUData(leader), 100);
            }
        } else if (data.regional) {
            // Re-render with current data
            renderScorecard();
        }
    }

    // Initialize admin config if switching to admin tab
    if (tab === 'admin') {
        setTimeout(() => initializeAdminConfig(), 100);
    }

    // Load campaign data if switching to campaign tab
    if (tab === 'campaign') {
        webinarData = null; // Force reload with current quarter
        setTimeout(() => loadWebinarData(), 100);
    }
}

// Manual refresh
async function manualRefresh() {
    const btn = document.querySelector('.refresh-btn');
    const icon = document.getElementById('refreshIcon');

    // Add refreshing state
    btn.classList.add('refreshing');

    console.log('🔄 Manual refresh triggered');
    trackEvent('manual_refresh', { cloud: currentCloud, ou: currentOUFilter });

    try {
        // Reload current view data
        if (currentOUFilter) {
            // Refresh OU scorecard
            const leader = OU_TO_LEADER[currentOUFilter];
            await loadOUData(leader);
        } else {
            // Refresh Cloud scorecard
            await selectCloud(currentCloud);
        }

        console.log('✅ Refresh complete');
    } catch (error) {
        console.error('❌ Refresh failed:', error);
        alert('Failed to refresh data. Please try again.');
    } finally {
        // Remove refreshing state after 1 second
        setTimeout(() => {
            btn.classList.remove('refreshing');
        }, 1000);
    }
}

// Show tab content
function showTabContent(tab) {
    // Hide all
    document.getElementById('healthContent').style.display = 'none';
    document.getElementById('leadContent').style.display = 'none';
    document.getElementById('campaignContent').style.display = 'none';
    document.getElementById('adminContent').style.display = 'none';

    // Show selected
    document.getElementById(`${tab}Content`).style.display = 'block';
}

// Select OU
async function selectOU(leaderName) {
    // Get OU name from leader
    const ouName = LEADER_TO_OU[leaderName] || leaderName;

    console.log(`📍 Selecting OU: ${ouName} (${leaderName})`);

    // Track OU selection
    trackEvent('ou_scorecard_opened', { ou: ouName, leader: leaderName });

    // Update current filters
    currentOUFilter = ouName;
    currentRegionFilter = EMEA_OUS.includes(leaderName) ? 'EMEA' : 'AMER';
    currentCloud = null; // Reset cloud filter when switching to OU mode

    // Reload Lead Cockpit if on lead tab
    if (currentTab === 'lead') {
        await loadLeadCockpitData();
    }

    // Reload Email if on campaign > email tab
    if (currentTab === 'campaign' && currentCampaignTab === 'email') {
        await loadEmailData();
    }

    // Update region button to match OU's region
    document.querySelectorAll('.region-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.region === currentRegionFilter) {
            btn.classList.add('active');
        }
    });

    // Update page title
    document.getElementById('currentCloud').textContent = ouName;

    // Update active state in sidebar
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    // Find and activate the OU nav item by matching the onclick attribute
    const ouItems = document.querySelectorAll('.nav-subitem');
    ouItems.forEach(item => {
        const onclick = item.getAttribute('onclick');
        if (onclick && onclick.includes(`selectOU('${leaderName}')`)) {
            item.classList.add('active');
        }
    });

    // Update selection banner
    updateSelectionBanner();

    // Load data for this OU across all clouds
    await loadOUData(leaderName);
}

async function loadOUData(leaderName) {
    showLoading();
    try {
        const leadersParam = `&leaders=${encodeURIComponent(leaderName)}`;

        // Convert YTD to Q1,Q2 for Health of Cloud endpoints
        const quartersParam = currentQuarter === 'YTD' ? 'Q1,Q2' : currentQuarter;

        // Load regional data for ALL clouds
        const regional = await fetch(`${API_BASE}/regional?quarters=${encodeURIComponent(quartersParam)}`).then(r => r.json());

        // Filter regional data to this leader only
        regional.data = regional.data.filter(r => r.leader === leaderName);

        // Filter to show only visible clouds
        const visibleRegionalData = regional.data.filter(r => ouModeVisibleClouds.includes(r.cloud));
        const visibleCloudNames = visibleRegionalData.map(r => r.cloud);

        console.log(`📊 Loading OU data for ${leaderName} with ${visibleCloudNames.length} visible clouds:`, visibleCloudNames);

        // Load data for each visible cloud
        const cloudDataPromises = visibleCloudNames.map(async (cloudName) => {
            const cloudParam = `&cloud=${encodeURIComponent(cloudName)}`;
            try {
                const [horseman, traffic, offer] = await Promise.all([
                    fetch(`${API_BASE}/horseman?quarters=${encodeURIComponent(quartersParam)}${leadersParam}${cloudParam}`).then(r => r.json()),
                    fetch(`${API_BASE}/traffic?quarters=${encodeURIComponent(quartersParam)}${leadersParam}${cloudParam}`).then(r => r.json()),
                    fetch(`${API_BASE}/offer?quarters=${encodeURIComponent(quartersParam)}${leadersParam}${cloudParam}`).then(r => r.json())
                ]);
                return { cloudName, horseman, traffic, offer };
            } catch (error) {
                console.error(`Error loading data for cloud ${cloudName}:`, error);
                return { cloudName, horseman: {total: {mdp: 0}, breakdown: {}}, traffic: {total: {mdp: 0}, breakdown: {}}, offer: {total: {mdp: 0}, breakdown: {}} };
            }
        });

        const cloudDataArray = await Promise.all(cloudDataPromises);

        console.log(`📊 Cloud data array:`, cloudDataArray);

        // Aggregate data across visible clouds
        const aggregatedHorseman = aggregateHorsemanData(cloudDataArray);
        const aggregatedTraffic = aggregateTrafficData(cloudDataArray);
        const aggregatedOffer = aggregateOfferData(cloudDataArray);

        console.log(`📊 Aggregated data:`, {
            horseman: aggregatedHorseman,
            traffic: aggregatedTraffic,
            offer: aggregatedOffer
        });

        data = {
            regional,
            horseman: aggregatedHorseman,
            traffic: aggregatedTraffic,
            offer: aggregatedOffer,
            clouds: null
        };

        // Render OU scorecard (shows only visible clouds for this OU)
        renderOUScorecard();

        // Reload webinar data if on campaign tab
        if (currentTab === 'campaign') {
            webinarData = null;
            await loadWebinarData();
        }

        hideLoading();

    } catch (error) {
        console.error('Failed to load OU data:', error);
        hideLoading();
        alert('Failed to load OU data. Please try again.');
    }
}

// Aggregate Horseman data from multiple clouds
function aggregateHorsemanData(cloudDataArray) {
    const aggregated = {
        breakdown: {},
        total: { mdp: 0 }
    };

    const keys = ['AE', 'BDR', 'Specialist', 'ECS'];

    cloudDataArray.forEach(({ horseman }) => {
        keys.forEach(key => {
            if (horseman.breakdown[key]) {
                if (!aggregated.breakdown[key]) {
                    aggregated.breakdown[key] = {
                        mdp: 0,
                        previous_mdp: 0,
                        yoy_change: 0,
                        share_diff: 0,
                        count: 0
                    };
                }
                aggregated.breakdown[key].mdp += horseman.breakdown[key].mdp || 0;
                aggregated.breakdown[key].previous_mdp += horseman.breakdown[key].previous_mdp || 0;
                aggregated.breakdown[key].share_diff += horseman.breakdown[key].share_diff || 0;
                aggregated.breakdown[key].count++;
            }
        });
        aggregated.total.mdp += horseman.total.mdp || 0;
    });

    // Recalculate YoY from aggregated MDP values (not average!)
    keys.forEach(key => {
        if (aggregated.breakdown[key] && aggregated.breakdown[key].count > 0) {
            if (aggregated.breakdown[key].previous_mdp > 0) {
                aggregated.breakdown[key].yoy_change = (aggregated.breakdown[key].mdp - aggregated.breakdown[key].previous_mdp) / aggregated.breakdown[key].previous_mdp;
            }
            aggregated.breakdown[key].share_diff /= aggregated.breakdown[key].count;
        }
    });

    return aggregated;
}

// Aggregate Traffic data from multiple clouds
function aggregateTrafficData(cloudDataArray) {
    const aggregated = {
        breakdown: {},
        total: { mdp: 0 }
    };

    cloudDataArray.forEach(({ traffic }) => {
        Object.entries(traffic.breakdown).forEach(([sourceL1, l1Data]) => {
            if (!aggregated.breakdown[sourceL1]) {
                aggregated.breakdown[sourceL1] = {
                    mdp: 0,
                    previous_mdp: 0,
                    yoy_change: 0,
                    share_diff: 0,
                    children: {},
                    count: 0
                };
            }
            aggregated.breakdown[sourceL1].mdp += l1Data.mdp || 0;
            aggregated.breakdown[sourceL1].previous_mdp += l1Data.previous_mdp || 0;
            aggregated.breakdown[sourceL1].share_diff += l1Data.share_diff || 0;
            aggregated.breakdown[sourceL1].count++;

            // Aggregate L2 children
            if (l1Data.children) {
                Object.entries(l1Data.children).forEach(([sourceL2, l2Data]) => {
                    if (!aggregated.breakdown[sourceL1].children[sourceL2]) {
                        aggregated.breakdown[sourceL1].children[sourceL2] = {
                            mdp: 0,
                            previous_mdp: 0,
                            yoy_change: 0,
                            share_diff: 0,
                            count: 0
                        };
                    }
                    aggregated.breakdown[sourceL1].children[sourceL2].mdp += l2Data.mdp || 0;
                    aggregated.breakdown[sourceL1].children[sourceL2].previous_mdp += l2Data.previous_mdp || 0;
                    aggregated.breakdown[sourceL1].children[sourceL2].share_diff += l2Data.share_diff || 0;
                    aggregated.breakdown[sourceL1].children[sourceL2].count++;
                });
            }
        });
        aggregated.total.mdp += traffic.total.mdp || 0;
    });

    // Recalculate YoY from aggregated MDP values (not average!)
    Object.values(aggregated.breakdown).forEach(l1Data => {
        if (l1Data.previous_mdp > 0) {
            l1Data.yoy_change = (l1Data.mdp - l1Data.previous_mdp) / l1Data.previous_mdp;
        }
        if (l1Data.count > 0) {
            l1Data.share_diff /= l1Data.count;
        }
        Object.values(l1Data.children || {}).forEach(l2Data => {
            if (l2Data.previous_mdp > 0) {
                l2Data.yoy_change = (l2Data.mdp - l2Data.previous_mdp) / l2Data.previous_mdp;
            }
            if (l2Data.count > 0) {
                l2Data.share_diff /= l2Data.count;
            }
        });
    });

    return aggregated;
}

// Aggregate Offer data from multiple clouds
function aggregateOfferData(cloudDataArray) {
    const aggregated = {
        breakdown: {},
        total: { mdp: 0 }
    };

    cloudDataArray.forEach(({ offer }) => {
        Object.entries(offer.breakdown).forEach(([offerL1, l1Data]) => {
            if (!aggregated.breakdown[offerL1]) {
                aggregated.breakdown[offerL1] = {
                    mdp: 0,
                    previous_mdp: 0,
                    yoy_change: 0,
                    share_diff: 0,
                    children: {},
                    count: 0
                };
            }
            aggregated.breakdown[offerL1].mdp += l1Data.mdp || 0;
            aggregated.breakdown[offerL1].previous_mdp += l1Data.previous_mdp || 0;
            aggregated.breakdown[offerL1].share_diff += l1Data.share_diff || 0;
            aggregated.breakdown[offerL1].count++;

            // Aggregate L2 children
            if (l1Data.children) {
                Object.entries(l1Data.children).forEach(([offerL2, l2Data]) => {
                    if (!aggregated.breakdown[offerL1].children[offerL2]) {
                        aggregated.breakdown[offerL1].children[offerL2] = {
                            mdp: 0,
                            previous_mdp: 0,
                            yoy_change: 0,
                            share_diff: 0,
                            count: 0
                        };
                    }
                    aggregated.breakdown[offerL1].children[offerL2].mdp += l2Data.mdp || 0;
                    aggregated.breakdown[offerL1].children[offerL2].previous_mdp += l2Data.previous_mdp || 0;
                    aggregated.breakdown[offerL1].children[offerL2].share_diff += l2Data.share_diff || 0;
                    aggregated.breakdown[offerL1].children[offerL2].count++;
                });
            }
        });
        aggregated.total.mdp += offer.total.mdp || 0;
    });

    // Recalculate YoY from aggregated MDP values (not average!)
    Object.values(aggregated.breakdown).forEach(l1Data => {
        if (l1Data.previous_mdp > 0) {
            l1Data.yoy_change = (l1Data.mdp - l1Data.previous_mdp) / l1Data.previous_mdp;
        }
        if (l1Data.count > 0) {
            l1Data.share_diff /= l1Data.count;
        }
        Object.values(l1Data.children || {}).forEach(l2Data => {
            if (l2Data.previous_mdp > 0) {
                l2Data.yoy_change = (l2Data.mdp - l2Data.previous_mdp) / l2Data.previous_mdp;
            }
            if (l2Data.count > 0) {
                l2Data.share_diff /= l2Data.count;
            }
        });
    });

    return aggregated;
}

function renderOUScorecard() {
    // Render Regional table (shows MDP by Cloud for this OU)
    renderRegionTable();

    // Render other tables (Horseman, Traffic, Offer aggregated across all clouds)
    renderHorsemanTable();
    renderTrafficTable();
    renderOfferTable();

    // Render insights
    renderInsights();
    renderActions();

    // Update header to show OU name
    const ouName = LEADER_TO_OU[data.regional.data[0]?.leader] || 'Operating Unit';
    document.getElementById('currentCloud').textContent = ouName;

    console.log('✅ OU Scorecard rendered');
}

// Verify data consistency across all 4 tables
function verifyDataConsistency() {
    try {
        // Get totals from each table
        const regionTotal = getTableTotal('regionTable');
        const horsemanTotal = getTableTotal('horsemanTable');
        const trafficTotal = getTableTotal('trafficTable');
        const offerTotal = getTableTotal('offerTable');

        console.log('📊 MDP Totals by table:');
        console.log(`  Region:   $${regionTotal}M (filtered by Cloud: ${currentCloud})`);
        console.log(`  Horseman: $${horsemanTotal}M (NOT filtered - shows all clouds)`);
        console.log(`  Traffic:  $${trafficTotal}M (NOT filtered - shows all clouds)`);
        console.log(`  Offer:    $${offerTotal}M (NOT filtered - shows all clouds)`);

        // Check if all totals match (within 0.1M tolerance for rounding)
        const totals = [regionTotal, horsemanTotal, trafficTotal, offerTotal].filter(t => t > 0);
        if (totals.length > 0) {
            const maxDiff = Math.max(...totals) - Math.min(...totals);
            if (maxDiff > 10) {
                console.warn(`⚠️ WARNING: Totals don't match! Difference: $${maxDiff.toFixed(2)}M`);
                console.warn('⚠️ CAUSE: Horseman/Traffic/Offer tables show ALL CLOUDS data, not filtered by current Cloud.');
                console.warn('⚠️ SOLUTION: Export Horseman/Traffic/Offer views in Tableau WITH Cloud filter applied.');
            } else {
                console.log('✅ All totals match! Data is consistent.');
            }
        }
    } catch (error) {
        console.error('Error verifying data consistency:', error);
    }
}

// Get MDP total from a table's Grand Total row
function getTableTotal(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return 0;

    const totalRow = table.querySelector('.total-row');
    if (!totalRow) return 0;

    // MDP is typically in column index 1 (after the label column)
    const mdpCell = totalRow.cells[1];
    if (!mdpCell) return 0;

    // Parse value like "$123.4M" or "123.4M"
    const text = mdpCell.textContent.trim();
    const match = text.match(/[\d,.]+/);
    if (!match) return 0;

    return parseFloat(match[0].replace(/,/g, ''));
}

// Loading functions
function showLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.classList.add('active');
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.classList.remove('active');
}

// Admin Config Functions
function initializeAdminConfig() {
    console.log('🔧 Initializing admin config UI');

    // Cloud Mode Clouds
    const cloudModeList = document.getElementById('cloudModeCloudsList');
    if (cloudModeList) {
        cloudModeList.innerHTML = ALL_CLOUDS.map(cloud => {
            const checked = cloudModeVisibleClouds.includes(cloud) ? 'checked' : '';
            return `
                <div class="cloud-checkbox-item">
                    <input type="checkbox" id="cloudMode_${cloud.replace(/\s+/g, '_')}" value="${cloud}" ${checked} onchange="updateCloudModeSelection()">
                    <label for="cloudMode_${cloud.replace(/\s+/g, '_')}">
                        <span>${cloud}</span>
                    </label>
                </div>
            `;
        }).join('');
    }

    // OU Mode Clouds
    const ouModeList = document.getElementById('ouModeCloudsList');
    if (ouModeList) {
        ouModeList.innerHTML = ALL_CLOUDS.map(cloud => {
            const checked = ouModeVisibleClouds.includes(cloud) ? 'checked' : '';
            return `
                <div class="cloud-checkbox-item">
                    <input type="checkbox" id="ouMode_${cloud.replace(/\s+/g, '_')}" value="${cloud}" ${checked} onchange="updateOUModeSelection()">
                    <label for="ouMode_${cloud.replace(/\s+/g, '_')}">
                        <span>${cloud}</span>
                    </label>
                </div>
            `;
        }).join('');
    }
}

function updateCloudModeSelection() {
    const checkboxes = document.querySelectorAll('#cloudModeCloudsList input[type="checkbox"]');
    cloudModeVisibleClouds = Array.from(checkboxes)
        .filter(cb => cb.checked)
        .map(cb => cb.value);
    console.log('Cloud Mode selection updated:', cloudModeVisibleClouds);
}

function updateOUModeSelection() {
    const checkboxes = document.querySelectorAll('#ouModeCloudsList input[type="checkbox"]');
    ouModeVisibleClouds = Array.from(checkboxes)
        .filter(cb => cb.checked)
        .map(cb => cb.value);
    console.log('OU Mode selection updated:', ouModeVisibleClouds);
}

function saveCloudModeConfig() {
    try {
        localStorage.setItem('cloudModeVisibleClouds', JSON.stringify(cloudModeVisibleClouds));
        alert(`✅ Cloud Mode configuration saved!\n\n${cloudModeVisibleClouds.length} clouds will appear in the sidebar.\n\nRefresh to see changes.`);
        console.log('✅ Cloud Mode config saved:', cloudModeVisibleClouds);
        trackEvent('admin_config_saved', { type: 'cloud_mode', clouds: cloudModeVisibleClouds });

        // Update sidebar immediately
        updateSidebarClouds();
    } catch (e) {
        alert('❌ Failed to save configuration: ' + e.message);
        console.error('Failed to save Cloud Mode config:', e);
    }
}

function saveOUModeConfig() {
    try {
        localStorage.setItem('ouModeVisibleClouds', JSON.stringify(ouModeVisibleClouds));
        alert(`✅ OU Mode configuration saved!\n\n${ouModeVisibleClouds.length} clouds will be shown in OU scorecard tables.\n\nClick on an OU to see changes.`);
        console.log('✅ OU Mode config saved:', ouModeVisibleClouds);
        trackEvent('admin_config_saved', { type: 'ou_mode', clouds: ouModeVisibleClouds });

        // Reload current OU if in OU mode
        if (currentOUFilter) {
            const leader = OU_TO_LEADER[currentOUFilter];
            if (leader) {
                loadOUData(leader);
            }
        }
    } catch (e) {
        alert('❌ Failed to save configuration: ' + e.message);
        console.error('Failed to save OU Mode config:', e);
    }
}

function updateSidebarClouds() {
    // This will be implemented to dynamically update sidebar based on cloudModeVisibleClouds
    console.log('📝 Sidebar cloud list should be updated with:', cloudModeVisibleClouds);
    // For now, user needs to refresh. Can be enhanced later to update DOM directly.
}

// ========================================
// CAMPAIGN SCORECARD - WEBINAR
// ========================================

let webinarData = null;
let emailData = null;
let emailCurrentView = 'ou'; // 'ou' or 'cloud'
let currentCampaignTab = 'webinar'; // Track which campaign sub-tab is active

// Switch between campaign sub-tabs
function switchCampaignTab(tab) {
    currentCampaignTab = tab; // Track current campaign tab

    // Update active state
    document.querySelectorAll('.campaign-subtab').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-campaign-tab="${tab}"]`)?.classList.add('active');

    // Show/hide content
    document.getElementById('webinarTabContent').style.display = tab === 'webinar' ? 'block' : 'none';
    document.getElementById('emailTabContent').style.display = tab === 'email' ? 'block' : 'none';
    document.getElementById('customTabContent').style.display = tab === 'custom' ? 'block' : 'none';
    document.getElementById('customEmailTabContent').style.display = tab === 'custom-email' ? 'block' : 'none';

    // Load data if needed
    if (tab === 'webinar' && !webinarData) {
        loadWebinarData();
    }

    if (tab === 'email') {
        loadEmailData(); // Always reload to reflect sidebar filters
    }

    if (tab === 'custom') {
        const quarterDisplay = document.getElementById('globalCurrentQuarter');
        if (quarterDisplay) {
            quarterDisplay.textContent = currentQuarter === 'YTD' ? 'YTD' : currentQuarter;
        }
    }

    if (tab === 'custom-email') {
        const quarterDisplay = document.getElementById('globalEmailCurrentQuarter');
        if (quarterDisplay) {
            quarterDisplay.textContent = currentQuarter === 'YTD' ? 'YTD' : currentQuarter;
        }
    }
}

// Load webinar data
async function loadWebinarData() {
    try {
        console.log('🔄 Loading webinar data...');
        console.log('Current state:', { currentCloud, currentOUFilter, currentRegionFilter, currentQuarter });

        showLoading();

        // Build parameters
        let leadersParam = '';
        if (currentOUFilter) {
            const leader = OU_TO_LEADER[currentOUFilter];
            console.log('🎯 OU Mode detected:', currentOUFilter, '→', leader);
            if (leader) {
                leadersParam = `&leaders=${encodeURIComponent(leader)}`;
            }
        } else if (currentRegionFilter === 'EMEA') {
            console.log('🌍 Region filter: EMEA');
            leadersParam = `&leaders=${encodeURIComponent(EMEA_OUS.join(','))}`;
        } else if (currentRegionFilter === 'AMER') {
            console.log('🌎 Region filter: AMER');
            leadersParam = `&leaders=${encodeURIComponent(AMER_OUS.join(','))}`;
        } else {
            console.log('🌐 No region filter - loading all leaders');
            const allLeaders = [...EMEA_OUS, ...AMER_OUS];
            leadersParam = `&leaders=${encodeURIComponent(allLeaders.join(','))}`;
        }

        // Never filter by cloud in API call - we filter in frontend instead
        // Only filter by leaders in OU mode

        const url = `${CAMPAIGN_API}/webinar?quarters=${encodeURIComponent(currentQuarter)}${leadersParam}`;
        console.log('📡 Fetching webinar:', url);

        const response = await fetch(url);
        webinarData = await response.json();

        console.log('✅ Webinar data loaded:', webinarData);
        console.log('Grand total:', webinarData.grand_total);
        console.log('Leaders count:', Object.keys(webinarData.by_leader || {}).length);

        renderWebinarTables();
        hideLoading();

    } catch (error) {
        console.error('❌ Failed to load webinar data:', error);
        hideLoading();
    }
}

// Render webinar tables
function renderWebinarTables() {
    if (!webinarData) return;

    renderWebinarLeaderTable();
    renderWebinarCloudTable();
}

// Render webinar by leader table
function renderWebinarLeaderTable() {
    const table = document.getElementById('webinarLeaderTable');
    if (!webinarData) {
        table.innerHTML = '<tbody><tr><td>No data available</td></tr></tbody>';
        return;
    }

    const allOULeaders = [...EMEA_OUS, ...AMER_OUS];

    if (currentCloud && !currentOUFilter) {
        // CLOUD MODE: Show breakdown by OU (Leaders)
        let html = `
            <thead>
                <tr>
                    <th style="width: 40%;">Operating Unit</th>
                    <th style="width: 20%;">Current FY MDP</th>
                    <th style="width: 20%;">MDP YoY</th>
                    <th style="width: 20%;">% MDP Share</th>
                </tr>
            </thead>
            <tbody>
        `;

        let grandTotal = 0;
        const leaderRows = [];

        // Extract MDP for current cloud from each leader
        Object.entries(webinarData.by_leader || {}).forEach(([leader, leaderData]) => {
            if (!allOULeaders.includes(leader)) return;

            const cloudData = leaderData.clouds?.[currentCloud];
            if (!cloudData) return;

            const ouName = LEADER_TO_OU[leader] || leader;
            leaderRows.push({
                ouName,
                mdp: cloudData.mdp || 0,
                yoy: cloudData.yoy || 0,
                share: cloudData.share || 0
            });

            grandTotal += (cloudData.mdp || 0);
        });

        // Sort by MDP descending
        leaderRows.sort((a, b) => b.mdp - a.mdp);

        // Render rows
        leaderRows.forEach(row => {
            const yoyClass = row.yoy >= 0 ? 'positive' : 'negative';
            const yoySign = row.yoy >= 0 ? '+' : '';
            const share = grandTotal > 0 ? (row.mdp / grandTotal * 100) : 0;

            html += `
                <tr>
                    <td><strong>${row.ouName}</strong></td>
                    <td class="number-cell">${formatCurrency(row.mdp)}</td>
                    <td class="number-cell ${yoyClass}">${yoySign}${(row.yoy * 100).toFixed(1)}%</td>
                    <td class="number-cell">${share.toFixed(1)}%</td>
                </tr>
            `;
        });

        // Grand total
        const cloudTotal = webinarData.by_cloud?.[currentCloud] || {};
        const grandYoY = cloudTotal.yoy || 0;
        const grandYoYClass = grandYoY >= 0 ? 'positive' : 'negative';
        const grandYoYSign = grandYoY >= 0 ? '+' : '';

        html += `
            <tr class="total-row">
                <td><strong>Grand Total</strong></td>
                <td class="number-cell" style="font-weight: 700;">${formatCurrency(grandTotal)}</td>
                <td class="number-cell ${grandYoYClass}" style="font-weight: 700;">${grandYoYSign}${(grandYoY * 100).toFixed(1)}%</td>
                <td class="number-cell" style="font-weight: 700;">100%</td>
            </tr>
        `;

        html += '</tbody>';
        table.innerHTML = html;

    } else if (currentOUFilter) {
        // OU MODE: Show breakdown by Cloud
        let html = `
            <thead>
                <tr>
                    <th style="width: 40%;">Cloud (APM L1)</th>
                    <th style="width: 20%;">Current FY MDP</th>
                    <th style="width: 20%;">MDP YoY</th>
                    <th style="width: 20%;">% MDP Share</th>
                </tr>
            </thead>
            <tbody>
        `;

        const leader = OU_TO_LEADER[currentOUFilter];
        const leaderData = webinarData.by_leader?.[leader];

        if (!leaderData) {
            table.innerHTML = '<tbody><tr><td>No data available</td></tr></tbody>';
            return;
        }

        let grandTotal = 0;

        // Sort clouds by MDP descending, filter out "All" and filter by visible clouds from Admin
        const sortedClouds = Object.entries(leaderData.clouds || {})
            .filter(([cloud]) => cloud !== 'All' && ouModeVisibleClouds.includes(cloud))
            .sort((a, b) => b[1].mdp - a[1].mdp);

        // Recalculate grand total and previous total with only visible clouds
        let grandTotalPrevious = 0;
        sortedClouds.forEach(([cloud, metrics]) => {
            grandTotal += metrics.mdp || 0;
            grandTotalPrevious += metrics.previous_mdp || 0;
        });

        sortedClouds.forEach(([cloud, metrics]) => {
            const yoy = metrics.yoy || 0;
            const yoyClass = yoy >= 0 ? 'positive' : 'negative';
            const yoySign = yoy >= 0 ? '+' : '';
            const share = grandTotal > 0 ? (metrics.mdp / grandTotal * 100) : 0;

            html += `
                <tr>
                    <td><strong>${cloud}</strong></td>
                    <td class="number-cell">${formatCurrency(metrics.mdp)}</td>
                    <td class="number-cell ${yoyClass}">${yoySign}${(yoy * 100).toFixed(1)}%</td>
                    <td class="number-cell">${share.toFixed(1)}%</td>
                </tr>
            `;
        });

        // Grand total - calculate YoY from visible clouds only
        const grandYoY = grandTotalPrevious > 0 ? (grandTotal - grandTotalPrevious) / grandTotalPrevious : 0;
        const grandYoYClass = grandYoY >= 0 ? 'positive' : 'negative';
        const grandYoYSign = grandYoY >= 0 ? '+' : '';

        html += `
            <tr class="total-row">
                <td><strong>Grand Total</strong></td>
                <td class="number-cell" style="font-weight: 700;">${formatCurrency(grandTotal)}</td>
                <td class="number-cell ${grandYoYClass}" style="font-weight: 700;">${grandYoYSign}${(grandYoY * 100).toFixed(1)}%</td>
                <td class="number-cell" style="font-weight: 700;">100%</td>
            </tr>
        `;

        html += '</tbody>';
        table.innerHTML = html;

    } else {
        // Global mode: show all clouds
        let html = `
            <thead>
                <tr>
                    <th style="width: 40%;">Cloud (APM L1)</th>
                    <th style="width: 20%;">Current FY MDP</th>
                    <th style="width: 20%;">MDP YoY</th>
                    <th style="width: 20%;">% MDP Share</th>
                </tr>
            </thead>
            <tbody>
        `;

        const sortedClouds = Object.entries(webinarData.by_cloud)
            .filter(([cloud]) => cloud !== 'All')
            .sort((a, b) => b[1].mdp - a[1].mdp);

        sortedClouds.forEach(([cloud, metrics]) => {
            const yoy = metrics.yoy || 0;
            const yoyClass = yoy >= 0 ? 'positive' : 'negative';
            const yoySign = yoy >= 0 ? '+' : '';
            const share = metrics.share || 0;

            html += `
                <tr>
                    <td><strong>${cloud}</strong></td>
                    <td class="number-cell">${formatCurrency(metrics.mdp)}</td>
                    <td class="number-cell ${yoyClass}">${yoySign}${(yoy * 100).toFixed(1)}%</td>
                    <td class="number-cell">${(share * 100).toFixed(1)}%</td>
                </tr>
            `;
        });

        const grandTotal = webinarData.grand_total || 0;
        const allCloud = webinarData.by_cloud['All'] || {};
        const grandYoY = allCloud.yoy || 0;
        const grandYoYClass = grandYoY >= 0 ? 'positive' : 'negative';
        const grandYoYSign = grandYoY >= 0 ? '+' : '';

        html += `
            <tr class="total-row">
                <td><strong>Grand Total</strong></td>
                <td class="number-cell" style="font-weight: 700;">${formatCurrency(grandTotal)}</td>
                <td class="number-cell ${grandYoYClass}" style="font-weight: 700;">${grandYoYSign}${(grandYoY * 100).toFixed(1)}%</td>
                <td class="number-cell" style="font-weight: 700;">100%</td>
            </tr>
        `;

        html += '</tbody>';
        table.innerHTML = html;
    }
}

// Render webinar by cloud table - hide it as it's redundant
function renderWebinarCloudTable() {
    const table = document.getElementById('webinarCloudTable');
    const tableBox = table.closest('.table-box');
    if (tableBox) {
        tableBox.style.display = 'none';
    }
}

// ========================================
// CAMPAIGN GLOBAL VIEW
// ========================================

let globalWebinarData = null;

async function loadGlobalCampaignData() {
    showLoading();

    try {
        // Get selected clouds
        const cloudSelect = document.getElementById('globalCloudFilter');
        const selectedClouds = Array.from(cloudSelect.selectedOptions).map(opt => opt.value);

        // Get selected OUs (leaders)
        const ouSelect = document.getElementById('globalOUFilter');
        const selectedLeaders = Array.from(ouSelect.selectedOptions).map(opt => opt.value);

        // Get view mode
        const viewMode = document.getElementById('globalViewMode').value;

        // Build API URL
        let url = `${CAMPAIGN_API}/webinar?quarters=${encodeURIComponent(currentQuarter)}`;

        if (selectedClouds.length > 0) {
            url += `&clouds=${encodeURIComponent(selectedClouds.join(','))}`;
        }

        if (selectedLeaders.length > 0) {
            url += `&leaders=${encodeURIComponent(selectedLeaders.join(','))}`;
        }

        console.log('📡 Loading global campaign data:', url);

        const response = await fetch(url);
        globalWebinarData = await response.json();

        console.log('✅ Global data loaded:', globalWebinarData);

        renderGlobalWebinarTable(viewMode);

    } catch (error) {
        console.error('❌ Error loading global campaign data:', error);
        alert('Erreur lors du chargement des données');
    } finally {
        hideLoading();
    }
}

function renderGlobalWebinarTable(viewMode) {
    const table = document.getElementById('globalWebinarTable');
    const headerRow = document.getElementById('globalTableHeader');

    if (!globalWebinarData) {
        table.querySelector('tbody').innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 40px;">No data available</td></tr>';
        return;
    }

    let html = '';

    if (viewMode === 'by-cloud') {
        // View by Cloud
        headerRow.innerHTML = `
            <th style="width: 40%;">Cloud (APM L1)</th>
            <th style="width: 20%;">Current FY MDP</th>
            <th style="width: 20%;">Previous FY MDP</th>
            <th style="width: 20%;">MDP YoY</th>
        `;

        // Sort clouds by MDP descending, filter out "All"
        const sortedClouds = Object.entries(globalWebinarData.by_cloud || {})
            .filter(([cloud]) => cloud !== 'All')
            .sort((a, b) => b[1].mdp - a[1].mdp);

        sortedClouds.forEach(([cloud, metrics]) => {
            // Use previous_mdp from backend (not recalculated)
            const previousMdp = metrics.previous_mdp || 0;
            const yoy = metrics.yoy || 0;
            const yoyClass = yoy >= 0 ? 'positive' : 'negative';
            const yoySign = yoy >= 0 ? '+' : '';

            html += `
                <tr>
                    <td><strong>${cloud}</strong></td>
                    <td class="number-cell">${formatCurrency(metrics.mdp)}</td>
                    <td class="number-cell">${formatCurrency(previousMdp)}</td>
                    <td class="number-cell ${yoyClass}">${yoySign}${(yoy * 100).toFixed(1)}%</td>
                </tr>
            `;
        });

        // Grand total - use backend calculated values
        const grandTotal = globalWebinarData.grand_total || 0;
        const grandPreviousTotal = globalWebinarData.grand_total_previous || 0;
        const grandYoY = globalWebinarData.grand_total_yoy || 0;
        const grandYoYClass = grandYoY >= 0 ? 'positive' : 'negative';
        const grandYoYSign = grandYoY >= 0 ? '+' : '';

        html += `
            <tr class="total-row">
                <td><strong>Grand Total</strong></td>
                <td class="number-cell">${formatCurrency(grandTotal)}</td>
                <td class="number-cell">${formatCurrency(grandPreviousTotal)}</td>
                <td class="number-cell ${grandYoYClass}">${grandYoYSign}${(grandYoY * 100).toFixed(1)}%</td>
            </tr>
        `;

    } else {
        // View by OU
        headerRow.innerHTML = `
            <th style="width: 40%;">Operating Unit</th>
            <th style="width: 20%;">Current FY MDP</th>
            <th style="width: 20%;">Previous FY MDP</th>
            <th style="width: 20%;">MDP YoY</th>
        `;

        const allOULeaders = [...EMEA_OUS, ...AMER_OUS];

        // Sort leaders by total MDP descending
        const sortedLeaders = Object.entries(globalWebinarData.by_leader || {})
            .filter(([leader]) => allOULeaders.includes(leader))
            .sort((a, b) => b[1].total_mdp - a[1].total_mdp);

        sortedLeaders.forEach(([leader, leaderData]) => {
            const ouName = LEADER_TO_OU[leader] || leader;
            const totalMdp = leaderData.total_mdp || 0;

            // Calculate previous MDP by summing individual clouds' previous_mdp (from backend)
            let previousMdp = 0;
            Object.entries(leaderData.clouds || {}).forEach(([cloud, metrics]) => {
                if (cloud !== 'All') {
                    previousMdp += metrics.previous_mdp || 0;
                }
            });

            // Calculate YoY from totals
            const yoy = previousMdp > 0 ? (totalMdp - previousMdp) / previousMdp : 0;
            const yoyClass = yoy >= 0 ? 'positive' : 'negative';
            const yoySign = yoy >= 0 ? '+' : '';

            html += `
                <tr>
                    <td><strong>${ouName}</strong></td>
                    <td class="number-cell">${formatCurrency(totalMdp)}</td>
                    <td class="number-cell">${formatCurrency(previousMdp)}</td>
                    <td class="number-cell ${yoyClass}">${yoySign}${(yoy * 100).toFixed(1)}%</td>
                </tr>
            `;
        });

        // Grand total - use backend calculated values
        const grandTotal = globalWebinarData.grand_total || 0;
        const grandPreviousTotal = globalWebinarData.grand_total_previous || 0;
        const grandYoY = globalWebinarData.grand_total_yoy || 0;
        const grandYoYClass = grandYoY >= 0 ? 'positive' : 'negative';
        const grandYoYSign = grandYoY >= 0 ? '+' : '';

        html += `
            <tr class="total-row">
                <td><strong>Grand Total</strong></td>
                <td class="number-cell">${formatCurrency(grandTotal)}</td>
                <td class="number-cell">${formatCurrency(grandPreviousTotal)}</td>
                <td class="number-cell ${grandYoYClass}">${grandYoYSign}${(grandYoY * 100).toFixed(1)}%</td>
            </tr>
        `;
    }

    table.querySelector('tbody').innerHTML = html;
}


// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Health of Cloud Scorecard initialized');

    // Force sidebar to be visible (reset collapsed state)
    localStorage.removeItem('scorecard_sidebar_collapsed');
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) sidebar.classList.remove('collapsed');

    // Initialize quarter button to Q2 (default)
    document.querySelectorAll('[data-quarter]').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.quarter === 'Q2') {
            btn.classList.add('active');
        }
    });

    loadData();

    // Initialize admin config when switching to admin tab
    setTimeout(() => {
        initializeAdminConfig();
    }, 500);
});

// ==========================================
// EMAIL SCORECARD FUNCTIONS
// ==========================================

// Variables declared at top of file with webinarData

// Load email data from API (uses sidebar filters: currentCloud, currentOUFilter, currentRegionFilter)
async function loadEmailData() {
    try {
        console.log('📧 Loading email data...');
        console.log('Current filters:', { currentCloud, currentOUFilter, currentRegionFilter, currentQuarter });
        showLoading();

        // Build API URL with filters
        let url = `${API_BASE_URL}/api/email/scorecard?`;
        const params = [];

        // Add quarter filter
        if (currentQuarter) {
            params.push(`quarters=${encodeURIComponent(currentQuarter)}`);
        }

        // Filter by OU if an OU is selected in sidebar
        if (currentOUFilter) {
            // Special handling for AMER sub-OUs
            // Email data doesn't have granular AMER OUs (REG, TMT, CBS, PACE)
            // It only has 'AMER' and 'Canada', so filter by region instead
            const amerSubOUs = ['AMER REG', 'TMT', 'PACE & AFD360', 'CBS'];

            if (amerSubOUs.includes(currentOUFilter)) {
                // For AMER sub-OUs, filter by AMER region
                params.push(`regions=AMER`);
                console.log(`⚠️ Email: AMER sub-OU "${currentOUFilter}" → filtering by region=AMER`);
            } else if (currentOUFilter === 'Canada') {
                // Canada has its own OU in email data
                params.push(`ous=Canada`);
            } else {
                // EMEA OUs (CENTRAL, NORTH, FRANCE, SOUTH, UKI) map directly
                params.push(`ous=${encodeURIComponent(currentOUFilter)}`);
            }
        }
        // Otherwise filter by region
        else if (currentRegionFilter && currentRegionFilter !== 'BOTH') {
            params.push(`regions=${encodeURIComponent(currentRegionFilter)}`);
        }

        // Filter by Cloud if a cloud is selected in sidebar
        if (currentCloud) {
            params.push(`clouds=${encodeURIComponent(currentCloud)}`);
        }

        url += params.join('&');

        console.log('📡 Fetching email data:', url);

        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        emailData = await response.json();

        console.log('✅ Email data loaded:', emailData);

        renderEmailTable();

    } catch (error) {
        console.error('❌ Error loading email data:', error);
        const tbody = document.querySelector('#emailTable tbody');
        if (tbody) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; padding: 40px; color: var(--red);">Error: ${error.message}</td></tr>`;
        }
    } finally {
        hideLoading();
    }
}

// Format number with thousands separator
function formatEmailNumber(value) {
    if (!value && value !== 0) return '-';
    return Math.round(value).toLocaleString('fr-FR');
}

// Format percentage
function formatEmailPercent(value) {
    if (!value && value !== 0) return '-';
    return `${value.toFixed(1)}%`;
}

// Get metric color class based on benchmarks
function getEmailMetricClass(metricName, value) {
    if (metricName === 'unique_ctr') {
        // Unique CTR: Red <= 2.10%, Green >= 2.60%, Yellow between
        if (value <= 2.10) return 'metric-bad';
        if (value >= 2.60) return 'metric-good';
        return 'metric-warning';
    }
    if (metricName === 'ucr') {
        // U:CR: Green <= 16.40%, Red >= 23.74%, Yellow between
        if (value <= 16.40) return 'metric-good';
        if (value >= 23.74) return 'metric-bad';
        return 'metric-warning';
    }
    if (metricName === 'dse_coverage') {
        // DSE Coverage: Green > 90%, Orange 70-90%, Red < 70%
        if (value >= 90) return 'metric-good';
        if (value >= 70) return 'metric-warning';
        return 'metric-bad';
    }
    return '';
}

// Render email table (adapts to sidebar context)
function renderEmailTable() {
    const tbody = document.querySelector('#emailTable tbody');
    const titleEl = document.getElementById('emailTableTitle');

    if (!tbody || !emailData) return;

    let html = '';
    let title = '📧 Email Performance';

    // Determine rendering mode based on sidebar selection
    if (currentOUFilter) {
        // OU Mode: Show clouds for this OU (filtered by ouModeVisibleClouds)
        title = `📧 Email Performance - ${currentOUFilter}`;
        const ouData = emailData.by_ou?.[currentOUFilter];

        if (!ouData) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 40px; color: var(--muted);">No data for this OU</td></tr>';
            if (titleEl) titleEl.textContent = title;
            return;
        }

        // Filter clouds by ouModeVisibleClouds and sort
        const allClouds = Object.keys(ouData.clouds || {});
        const visibleClouds = allClouds.filter(cloud => ouModeVisibleClouds.includes(cloud)).sort();

        console.log(`📊 OU Mode Email: showing ${visibleClouds.length}/${allClouds.length} clouds for ${currentOUFilter}`);

        // Recalculate totals with only visible clouds
        let totalDseCoverage = 0, totalEmails = 0, totalCtr = 0, totalUcr = 0;
        let cloudCount = visibleClouds.length;

        visibleClouds.forEach(cloud => {
            const metrics = ouData.clouds[cloud];

            // Render cloud row
            html += `
                <tr>
                    <td style="font-weight: 700; color: var(--brand);">${cloud}</td>
                    <td class="${getEmailMetricClass('dse_coverage', metrics.dse_coverage)}">
                        ${formatEmailPercent(metrics.dse_coverage)}
                    </td>
                    <td>${formatEmailNumber(metrics.emails_delivered)}</td>
                    <td class="${getEmailMetricClass('unique_ctr', metrics.unique_ctr)}">
                        ${formatEmailPercent(metrics.unique_ctr)}
                    </td>
                    <td class="${getEmailMetricClass('ucr', metrics.ucr)}">
                        ${formatEmailPercent(metrics.ucr)}
                    </td>
                </tr>
            `;

            // Accumulate for totals (weighted by emails for CTR/UCR)
            totalDseCoverage += metrics.dse_coverage || 0;
            totalEmails += metrics.emails_delivered || 0;
            totalCtr += (metrics.unique_ctr || 0) * (metrics.emails_delivered || 0);
            totalUcr += (metrics.ucr || 0) * (metrics.emails_delivered || 0);
        });

        // Calculate weighted averages for totals
        const avgDseCoverage = cloudCount > 0 ? totalDseCoverage / cloudCount : 0;
        const avgCtr = totalEmails > 0 ? totalCtr / totalEmails : 0;
        const avgUcr = totalEmails > 0 ? totalUcr / totalEmails : 0;

        // OU total row
        html += `
            <tr class="total-row">
                <td style="font-weight: 700;">TOTAL ${currentOUFilter}</td>
                <td class="${getEmailMetricClass('dse_coverage', avgDseCoverage)}">
                    ${formatEmailPercent(avgDseCoverage)}
                </td>
                <td>${formatEmailNumber(totalEmails)}</td>
                <td class="${getEmailMetricClass('unique_ctr', avgCtr)}">
                    ${formatEmailPercent(avgCtr)}
                </td>
                <td class="${getEmailMetricClass('ucr', avgUcr)}">
                    ${formatEmailPercent(avgUcr)}
                </td>
            </tr>
        `;

    } else if (currentCloud && currentCloud !== 'All') {
        // Cloud Mode: Show OUs for this cloud
        title = `📧 Email Performance - ${currentCloud}`;
        const ous = Object.keys(emailData.by_ou || {}).sort();

        ous.forEach(ou => {
            const ouData = emailData.by_ou[ou];
            const cloudMetrics = ouData.clouds?.[currentCloud];

            if (cloudMetrics) {
                html += `
                    <tr>
                        <td style="font-weight: 700; color: var(--brand);">${ou}</td>
                        <td class="${getEmailMetricClass('dse_coverage', cloudMetrics.dse_coverage)}">
                            ${formatEmailPercent(cloudMetrics.dse_coverage)}
                        </td>
                        <td>${formatEmailNumber(cloudMetrics.emails_delivered)}</td>
                        <td class="${getEmailMetricClass('unique_ctr', cloudMetrics.unique_ctr)}">
                            ${formatEmailPercent(cloudMetrics.unique_ctr)}
                        </td>
                        <td class="${getEmailMetricClass('ucr', cloudMetrics.ucr)}">
                            ${formatEmailPercent(cloudMetrics.ucr)}
                        </td>
                    </tr>
                `;
            }
        });

        // Cloud total
        const cloudTotal = emailData.by_cloud?.[currentCloud];
        if (cloudTotal) {
            html += `
                <tr class="total-row">
                    <td style="font-weight: 700;">TOTAL ${currentCloud}</td>
                    <td class="${getEmailMetricClass('dse_coverage', cloudTotal.dse_coverage)}">
                        ${formatEmailPercent(cloudTotal.dse_coverage)}
                    </td>
                    <td>${formatEmailNumber(cloudTotal.emails_delivered)}</td>
                    <td class="${getEmailMetricClass('unique_ctr', cloudTotal.unique_ctr)}">
                        ${formatEmailPercent(cloudTotal.unique_ctr)}
                    </td>
                    <td class="${getEmailMetricClass('ucr', cloudTotal.ucr)}">
                        ${formatEmailPercent(cloudTotal.ucr)}
                    </td>
                </tr>
            `;
        }

    } else {
        // Global view: Show all OUs with their clouds (filtered by ouModeVisibleClouds)
        const ous = Object.keys(emailData.by_ou || {}).sort();

        if (ous.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 40px; color: var(--muted);">No data available</td></tr>';
            if (titleEl) titleEl.textContent = title;
            return;
        }

        console.log(`📊 Global Email view: filtering clouds by ouModeVisibleClouds`);

        ous.forEach(ou => {
            const ouData = emailData.by_ou[ou];
            const allClouds = Object.keys(ouData.clouds || {});
            const visibleClouds = allClouds.filter(cloud => ouModeVisibleClouds.includes(cloud)).sort();

            // Skip OU if no visible clouds
            if (visibleClouds.length === 0) return;

            // Recalculate OU totals with only visible clouds
            let totalDseCoverage = 0, totalEmails = 0, totalCtr = 0, totalUcr = 0;

            visibleClouds.forEach(cloud => {
                const metrics = ouData.clouds[cloud];
                totalDseCoverage += metrics.dse_coverage || 0;
                totalEmails += metrics.emails_delivered || 0;
                totalCtr += (metrics.unique_ctr || 0) * (metrics.emails_delivered || 0);
                totalUcr += (metrics.ucr || 0) * (metrics.emails_delivered || 0);
            });

            const avgDseCoverage = visibleClouds.length > 0 ? totalDseCoverage / visibleClouds.length : 0;
            const avgCtr = totalEmails > 0 ? totalCtr / totalEmails : 0;
            const avgUcr = totalEmails > 0 ? totalUcr / totalEmails : 0;

            // OU header with recalculated totals
            html += `
                <tr style="background: var(--bg-subtle); font-weight: 700;">
                    <td style="color: var(--brand);">${ou}</td>
                    <td class="${getEmailMetricClass('dse_coverage', avgDseCoverage)}">
                        ${formatEmailPercent(avgDseCoverage)}
                    </td>
                    <td>${formatEmailNumber(totalEmails)}</td>
                    <td class="${getEmailMetricClass('unique_ctr', avgCtr)}">
                        ${formatEmailPercent(avgCtr)}
                    </td>
                    <td class="${getEmailMetricClass('ucr', avgUcr)}">
                        ${formatEmailPercent(avgUcr)}
                    </td>
                </tr>
            `;

            // Visible clouds under OU
            visibleClouds.forEach(cloud => {
                const metrics = ouData.clouds[cloud];
                html += `
                    <tr>
                        <td style="padding-left: 32px; color: var(--muted);">${cloud}</td>
                        <td class="${getEmailMetricClass('dse_coverage', metrics.dse_coverage)}">
                            ${formatEmailPercent(metrics.dse_coverage)}
                        </td>
                        <td>${formatEmailNumber(metrics.emails_delivered)}</td>
                        <td class="${getEmailMetricClass('unique_ctr', metrics.unique_ctr)}">
                            ${formatEmailPercent(metrics.unique_ctr)}
                        </td>
                        <td class="${getEmailMetricClass('ucr', metrics.ucr)}">
                            ${formatEmailPercent(metrics.ucr)}
                        </td>
                    </tr>
                `;
            });
        });

        // Grand total
        if (emailData.grand_total) {
            html += `
                <tr class="total-row">
                    <td style="font-weight: 700;">GRAND TOTAL</td>
                    <td class="${getEmailMetricClass('dse_coverage', emailData.grand_total.dse_coverage)}">
                        ${formatEmailPercent(emailData.grand_total.dse_coverage)}
                    </td>
                    <td>${formatEmailNumber(emailData.grand_total.emails_delivered)}</td>
                    <td class="${getEmailMetricClass('unique_ctr', emailData.grand_total.unique_ctr)}">
                        ${formatEmailPercent(emailData.grand_total.unique_ctr)}
                    </td>
                    <td class="${getEmailMetricClass('ucr', emailData.grand_total.ucr)}">
                        ${formatEmailPercent(emailData.grand_total.ucr)}
                    </td>
                </tr>
            `;
        }
    }

    tbody.innerHTML = html;
    if (titleEl) titleEl.textContent = title;
}

// Make functions available globally
window.loadEmailData = loadEmailData;

// ==========================================
// CUSTOM EMAIL VIEW (Global Filters)
// ==========================================

async function loadGlobalEmailData() {
    try {
        console.log('📧 Loading custom email data...');
        showLoading();

        // Get selected clouds
        const cloudSelect = document.getElementById('globalEmailCloudFilter');
        const selectedClouds = Array.from(cloudSelect.selectedOptions).map(opt => opt.value);

        // Get selected OUs
        const ouSelect = document.getElementById('globalEmailOUFilter');
        const selectedOUs = Array.from(ouSelect.selectedOptions).map(opt => opt.value);

        // Get view mode
        const viewMode = document.getElementById('globalEmailViewMode').value;

        // Build API URL
        let url = `${API_BASE_URL}/api/email/scorecard?quarters=${encodeURIComponent(currentQuarter)}`;

        if (selectedClouds.length > 0) {
            url += `&clouds=${encodeURIComponent(selectedClouds.join(','))}`;
        }

        if (selectedOUs.length > 0) {
            url += `&ous=${encodeURIComponent(selectedOUs.join(','))}`;
        }

        console.log('📡 Fetching custom email:', url);

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('✅ Custom email data loaded:', data);

        renderGlobalEmailTable(data, viewMode);

    } catch (error) {
        console.error('❌ Error loading custom email data:', error);
        const tbody = document.querySelector('#globalEmailTable tbody');
        if (tbody) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; padding: 40px; color: var(--red);">Error: ${error.message}</td></tr>`;
        }
    } finally {
        hideLoading();
    }
}

function renderGlobalEmailTable(data, viewMode) {
    const table = document.getElementById('globalEmailTable');
    const tbody = table.querySelector('tbody');

    if (!data || (!data.by_ou && !data.by_cloud)) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 40px; color: var(--muted);">No data available</td></tr>';
        return;
    }

    let html = '';

    if (viewMode === 'by-ou') {
        // View by OU
        const ous = Object.keys(data.by_ou || {}).sort();

        ous.forEach(ou => {
            const ouData = data.by_ou[ou];
            const clouds = Object.keys(ouData.clouds || {}).sort();

            // OU header row
            html += `
                <tr style="background: var(--bg-subtle); font-weight: 700;">
                    <td style="color: var(--brand);">${ou}</td>
                    <td class="${getEmailMetricClass('dse_coverage', ouData.total.dse_coverage)}">
                        ${formatEmailPercent(ouData.total.dse_coverage)}
                    </td>
                    <td>${formatEmailNumber(ouData.total.emails_delivered)}</td>
                    <td class="${getEmailMetricClass('unique_ctr', ouData.total.unique_ctr)}">
                        ${formatEmailPercent(ouData.total.unique_ctr)}
                    </td>
                    <td class="${getEmailMetricClass('ucr', ouData.total.ucr)}">
                        ${formatEmailPercent(ouData.total.ucr)}
                    </td>
                </tr>
            `;

            // Cloud rows
            clouds.forEach(cloud => {
                const metrics = ouData.clouds[cloud];
                html += `
                    <tr>
                        <td style="padding-left: 32px; color: var(--muted);">${cloud}</td>
                        <td class="${getEmailMetricClass('dse_coverage', metrics.dse_coverage)}">
                            ${formatEmailPercent(metrics.dse_coverage)}
                        </td>
                        <td>${formatEmailNumber(metrics.emails_delivered)}</td>
                        <td class="${getEmailMetricClass('unique_ctr', metrics.unique_ctr)}">
                            ${formatEmailPercent(metrics.unique_ctr)}
                        </td>
                        <td class="${getEmailMetricClass('ucr', metrics.ucr)}">
                            ${formatEmailPercent(metrics.ucr)}
                        </td>
                    </tr>
                `;
            });
        });

    } else {
        // View by Cloud
        const clouds = Object.keys(data.by_cloud || {}).sort();

        clouds.forEach(cloud => {
            const metrics = data.by_cloud[cloud];
            html += `
                <tr>
                    <td style="font-weight: 700; color: var(--brand);">${cloud}</td>
                    <td class="${getEmailMetricClass('dse_coverage', metrics.dse_coverage)}">
                        ${formatEmailPercent(metrics.dse_coverage)}
                    </td>
                    <td>${formatEmailNumber(metrics.emails_delivered)}</td>
                    <td class="${getEmailMetricClass('unique_ctr', metrics.unique_ctr)}">
                        ${formatEmailPercent(metrics.unique_ctr)}
                    </td>
                    <td class="${getEmailMetricClass('ucr', metrics.ucr)}">
                        ${formatEmailPercent(metrics.ucr)}
                    </td>
                </tr>
            `;
        });
    }

    // Grand total
    if (data.grand_total) {
        html += `
            <tr class="total-row">
                <td style="font-weight: 700;">GRAND TOTAL</td>
                <td class="${getEmailMetricClass('dse_coverage', data.grand_total.dse_coverage)}">
                    ${formatEmailPercent(data.grand_total.dse_coverage)}
                </td>
                <td>${formatEmailNumber(data.grand_total.emails_delivered)}</td>
                <td class="${getEmailMetricClass('unique_ctr', data.grand_total.unique_ctr)}">
                    ${formatEmailPercent(data.grand_total.unique_ctr)}
                </td>
                <td class="${getEmailMetricClass('ucr', data.grand_total.ucr)}">
                    ${formatEmailPercent(data.grand_total.ucr)}
                </td>
            </tr>
        `;
    }

    tbody.innerHTML = html;
}

window.loadGlobalEmailData = loadGlobalEmailData;
