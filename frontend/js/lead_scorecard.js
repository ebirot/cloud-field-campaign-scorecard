/**
 * Lead Scorecard Functions
 */

const LEAD_API = 'http://localhost:8000/api/lead/lead-scorecard';
let leadScorecardData = null;

// OU lists for region filtering
const EMEA_OU_NAMES = ['UKI', 'France', 'EMEA Central', 'EMEA North', 'EMEA South'];
const AMER_OU_NAMES = ['AMER CBS', 'AMER PACE & AFD360', 'AMER REG', 'AMER TMT'];

/**
 * Load Lead Scorecard data from API
 */
async function loadLeadScorecardData() {
    try {
        showLoading();

        // Use the global currentQuarter from the main app
        const quarter = currentQuarter || 'Q2';

        // Build URL with filters
        let url = `${LEAD_API}?quarter=${encodeURIComponent(quarter)}`;

        // Add cloud filter if a cloud is selected
        if (currentCloud && !currentOUFilter) {
            url += `&cloud=${encodeURIComponent(currentCloud)}`;
        }

        // Add OU filter if an OU is selected
        if (currentOUFilter && !currentCloud) {
            // Use the OU name directly (not the leader name)
            // The CSV uses OU names like "UKI", "France", "AMER CBS", etc.
            const ouName = currentOUFilter.includes('AMER') || currentOUFilter.includes('EMEA') ?
                currentOUFilter : // Already formatted (e.g., "AMER CBS")
                currentOUFilter;  // Use as-is (e.g., "UKI", "France")
            url += `&ou=${encodeURIComponent(ouName)}`;
        }

        console.log(`[LEAD] Fetching: ${url}`);

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        leadScorecardData = await response.json();

        console.log('[LEAD] Data loaded:', leadScorecardData);

        // Render the table
        renderLeadScorecardTable();

        // Update sidebar metrics (placeholder for now)
        updateLeadSidebar();

    } catch (error) {
        console.error('[LEAD] Error loading data:', error);
        document.getElementById('leadScorecardTableBody').innerHTML = `
            <tr><td colspan="11" style="text-align: center; padding: 40px; color: var(--red);">
                Error loading data: ${error.message}
            </td></tr>
        `;
    } finally {
        hideLoading();
    }
}

/**
 * Render Lead Scorecard table
 */
function renderLeadScorecardTable() {
    const tbody = document.getElementById('leadScorecardTableBody');
    const thead = document.getElementById('leadScorecardTable').querySelector('thead tr');

    if (!leadScorecardData || !leadScorecardData.data) {
        tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; padding: 40px;">No data available</td></tr>';
        return;
    }

    let html = '';
    let totalRows = 0;
    let totals = { metric2: 0, metric7: 0 }; // Track VL # and S2 $
    let headerLabel = 'OU'; // Default header

    // Determine which region OUs to show
    let allowedOUs = null;
    if (currentRegionFilter === 'EMEA') {
        allowedOUs = EMEA_OU_NAMES;
    } else if (currentRegionFilter === 'AMER') {
        allowedOUs = AMER_OU_NAMES;
    }
    // If BOTH, allowedOUs stays null (show all)

    // Handle different data structures based on filters
    if (leadScorecardData.cloud) {
        // CLOUD MODE: data.by_ou contains OUs for this cloud
        headerLabel = 'OU';
        const cloudName = leadScorecardData.cloud;
        const ous = leadScorecardData.data.by_ou || {};

        Object.entries(ous).forEach(([ouName, metrics]) => {
            // Apply region filter
            if (allowedOUs && !allowedOUs.includes(ouName)) {
                return;
            }
            totalRows++;
            html += renderTableRow(ouName, metrics);
            totals.metric2 += metrics.metric2 || 0;
            totals.metric7 += metrics.metric7 || 0;
        });

    } else if (leadScorecardData.ou) {
        // OU MODE: data contains clouds for this OU
        headerLabel = 'Cloud';
        const ouName = leadScorecardData.ou;
        const clouds = leadScorecardData.data || {};

        // Filter by OU mode visible clouds from admin config
        Object.entries(clouds).forEach(([cloudName, metrics]) => {
            // Check if cloud is visible in OU mode (use ouModeVisibleClouds from admin config)
            if (typeof ouModeVisibleClouds !== 'undefined' && !ouModeVisibleClouds.includes(cloudName)) {
                return; // Skip this cloud
            }
            totalRows++;
            html += renderTableRow(cloudName, metrics);
            totals.metric2 += metrics.metric2 || 0;
            totals.metric7 += metrics.metric7 || 0;
        });

    } else {
        // ALL DATA MODE: data.by_cloud contains everything
        headerLabel = 'OU';
        const quarters = leadScorecardData.data.by_cloud || {};

        Object.entries(quarters).forEach(([cloudName, cloudData]) => {
            // Skip if not the current cloud (when a cloud is selected)
            if (currentCloud && cloudName !== currentCloud) {
                return;
            }

            // Check if cloud is visible (use VISIBLE_CLOUDS from admin config)
            if (typeof VISIBLE_CLOUDS !== 'undefined' && !VISIBLE_CLOUDS.includes(cloudName)) {
                return; // Skip this cloud
            }

            const ous = cloudData.by_ou || {};

            Object.entries(ous).forEach(([ouName, metrics]) => {
                // Apply region filter
                if (allowedOUs && !allowedOUs.includes(ouName)) {
                    return;
                }
                totalRows++;
                html += renderTableRow(ouName, metrics);
                totals.metric2 += metrics.metric2 || 0;
                totals.metric7 += metrics.metric7 || 0;
            });
        });
    }

    // Update table header dynamically
    thead.innerHTML = `
        <th>${headerLabel}</th>
        <th>MQL > VL #</th>
        <th>VL #</th>
        <th>VL % YoY</th>
        <th>S1 % YoY</th>
        <th>VL > S2 # % YoY</th>
        <th>VL > S2 # - Diff pnts</th>
        <th>S2 $</th>
        <th>S2 $ % YoY</th>
    `;

    // Add Total row
    if (totalRows > 0) {
        html += `
            <tr class="total-row">
                <td><strong>Grand Total</strong></td>
                <td class="number-cell">-</td>
                <td class="number-cell"><strong>${formatMetric(totals.metric2, '#')}</strong></td>
                <td class="number-cell">-</td>
                <td class="number-cell">-</td>
                <td class="number-cell">-</td>
                <td class="number-cell">-</td>
                <td class="number-cell"><strong>${formatMetric(totals.metric7, '$')}</strong></td>
                <td class="number-cell">-</td>
            </tr>
        `;
    }

    if (totalRows === 0) {
        html = '<tr><td colspan="9" style="text-align: center; padding: 40px;">No data for this quarter</td></tr>';
    }

    tbody.innerHTML = html;

    console.log(`[LEAD] Rendered ${totalRows} rows`);
}

/**
 * Render a single table row
 * @param {string} label - Either OU name or Cloud name depending on mode
 * @param {object} metrics - Metric values
 */
function renderTableRow(label, metrics) {
    return `
        <tr>
            <td><strong>${label}</strong></td>
            <td class="number-cell">${formatMetric(metrics.metric1, '%')}</td>
            <td class="number-cell">${formatMetric(metrics.metric2, '#')}</td>
            <td class="number-cell ${getMetricClass(metrics.metric3)}">${formatMetric(metrics.metric3, '%')}</td>
            <td class="number-cell ${getMetricClass(metrics.metric4)}">${formatMetric(metrics.metric4, '%')}</td>
            <td class="number-cell ${getMetricClass(metrics.metric5)}">${formatMetric(metrics.metric5, '%')}</td>
            <td class="number-cell ${getMetricClass(metrics.metric6)}">${formatMetric(metrics.metric6, 'ppnts')}</td>
            <td class="number-cell">${formatMetric(metrics.metric7, '$')}</td>
            <td class="number-cell ${getMetricClass(metrics.metric8)}">${formatMetric(metrics.metric8, '%')}</td>
        </tr>
    `;
}

/**
 * Format metric value based on type
 */
function formatMetric(value, type) {
    if (value === undefined || value === null) return '-';

    switch (type) {
        case '%':
            return `${value > 0 ? '+' : ''}${value.toFixed(1)}%`;
        case '#':
            return value.toLocaleString();
        case 'ppnts':
            return `${value > 0 ? '+' : ''}${value.toFixed(1)} ppnts`;
        case '$':
            return formatCurrency(value);
        default:
            return value;
    }
}

/**
 * Get CSS class for metric based on positive/negative
 */
function getMetricClass(value) {
    if (value === undefined || value === null || value === 0) return '';
    return value > 0 ? 'positive' : 'negative';
}

/**
 * Update Lead Sidebar metrics (placeholder)
 */
function updateLeadSidebar() {
    // TODO: Calculate totals from data
    // For now, use placeholder values
    document.getElementById('leadTotalLeads').textContent = '10.5K';
    document.getElementById('leadYoY').textContent = '+15% YoY';
    document.getElementById('leadCorePercent').textContent = '85%';
    document.getElementById('leadNonCorePercent').textContent = '15%';
}

// DISABLED - Using new Lead Cockpit instead
// Initialize Lead Scorecard when tab is switched
// if (typeof switchTab !== 'undefined') {
//     const originalSwitchTab = switchTab;
//     switchTab = function(tab) {
//         originalSwitchTab(tab);

//         if (tab === 'lead') {
//             setTimeout(() => {
//                 loadLeadScorecardData();
//             }, 100);
//         }
//     };
// }
