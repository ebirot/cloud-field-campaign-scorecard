/**
 * Email Scorecard Frontend Logic
 * Handles data fetching, filtering, and display
 */

const API_BASE = 'http://localhost:8000/api/email';

let currentQuarter = 'Q2';
let currentView = 'ou'; // 'ou' or 'cloud'
let emailData = null;

// Load dark mode preference
if (localStorage.getItem('scorecard_dark_mode') === '1') {
  document.body.classList.add('dark');
  document.getElementById('themeIcon').textContent = '☀';
}

function toggleDarkMode() {
  const isDark = document.body.classList.toggle('dark');
  document.getElementById('themeIcon').textContent = isDark ? '☀' : '☾';
  localStorage.setItem('scorecard_dark_mode', isDark ? '1' : '0');
}

function setQuarter(quarter) {
  currentQuarter = quarter;
  document.querySelectorAll('.quarter-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.quarter === quarter);
  });
}

function setView(view) {
  currentView = view;
  document.getElementById('viewOuBtn').classList.toggle('active', view === 'ou');
  document.getElementById('viewCloudBtn').classList.toggle('active', view === 'cloud');

  // Update table title
  document.getElementById('tableTitle').textContent =
    view === 'ou' ? 'Email Performance - Vue par OU' : 'Email Performance - Vue par Cloud';

  // Re-render if data is loaded
  if (emailData) {
    renderTable();
  }
}

function showLoading() {
  document.getElementById('loading').classList.add('active');
}

function hideLoading() {
  document.getElementById('loading').classList.remove('active');
}

function formatNumber(value) {
  if (!value && value !== 0) return '-';
  return value.toLocaleString('fr-FR');
}

function formatPercent(value) {
  if (!value && value !== 0) return '-';
  return `${value.toFixed(2)}%`;
}

function getMetricClass(metricName, value) {
  // Apply color coding based on benchmarks
  if (metricName === 'unique_ctr') {
    // UCTR: Good if > 1.55%
    return value > 1.55 ? 'metric-good' : '';
  }
  if (metricName === 'ucr') {
    // U:CR: Good if < 24.9%
    return value < 24.9 ? 'metric-good' : 'metric-bad';
  }
  if (metricName === 'dse_coverage') {
    // DSE Coverage: Good if > 90%
    return value > 90 ? 'metric-good' : '';
  }
  return '';
}

async function loadData() {
  showLoading();

  try {
    // Get selected region
    const region = document.getElementById('regionFilter').value;

    // Build API URL
    let url = `${API_BASE}/scorecard?`;

    const params = [];

    if (currentQuarter) {
      params.push(`quarters=${encodeURIComponent(currentQuarter)}`);
    }

    if (region) {
      params.push(`regions=${encodeURIComponent(region)}`);
    }

    url += params.join('&');

    console.log('📡 Fetching:', url);

    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    emailData = await response.json();

    console.log('✅ Data loaded:', emailData);

    renderTable();

  } catch (error) {
    console.error('❌ Error loading data:', error);
    alert(`Erreur lors du chargement des données: ${error.message}`);
  } finally {
    hideLoading();
  }
}

function renderTable() {
  const tbody = document.querySelector('#emailTable tbody');

  if (!emailData) {
    tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 40px; color: var(--muted);">Aucune donnée disponible</td></tr>';
    return;
  }

  let html = '';

  if (currentView === 'ou') {
    // Vue par OU
    const ous = Object.keys(emailData.by_ou || {}).sort();

    if (ous.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 40px; color: var(--muted);">Aucune donnée pour les filtres sélectionnés</td></tr>';
      return;
    }

    ous.forEach(ou => {
      const ouData = emailData.by_ou[ou];
      const clouds = Object.keys(ouData.clouds || {}).sort();

      // OU header row
      html += `
        <tr class="ou-row">
          <td class="ou-label">${ou}</td>
          <td class="metric-value ${getMetricClass('dse_coverage', ouData.total.dse_coverage)}">
            ${formatPercent(ouData.total.dse_coverage)}
          </td>
          <td class="metric-value">${formatNumber(ouData.total.emails_delivered)}</td>
          <td class="metric-value ${getMetricClass('unique_ctr', ouData.total.unique_ctr)}">
            ${formatPercent(ouData.total.unique_ctr)}
          </td>
          <td class="metric-value ${getMetricClass('ucr', ouData.total.ucr)}">
            ${formatPercent(ouData.total.ucr)}
          </td>
        </tr>
      `;

      // Cloud rows under this OU
      clouds.forEach(cloud => {
        const metrics = ouData.clouds[cloud];
        html += `
          <tr>
            <td class="cloud-label">${cloud}</td>
            <td class="metric-value ${getMetricClass('dse_coverage', metrics.dse_coverage)}">
              ${formatPercent(metrics.dse_coverage)}
            </td>
            <td class="metric-value">${formatNumber(metrics.emails_delivered)}</td>
            <td class="metric-value ${getMetricClass('unique_ctr', metrics.unique_ctr)}">
              ${formatPercent(metrics.unique_ctr)}
            </td>
            <td class="metric-value ${getMetricClass('ucr', metrics.ucr)}">
              ${formatPercent(metrics.ucr)}
            </td>
          </tr>
        `;
      });
    });

  } else {
    // Vue par Cloud
    const clouds = Object.keys(emailData.by_cloud || {}).sort();

    if (clouds.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 40px; color: var(--muted);">Aucune donnée pour les filtres sélectionnés</td></tr>';
      return;
    }

    clouds.forEach(cloud => {
      const metrics = emailData.by_cloud[cloud];
      html += `
        <tr>
          <td class="ou-label">${cloud}</td>
          <td class="metric-value ${getMetricClass('dse_coverage', metrics.dse_coverage)}">
            ${formatPercent(metrics.dse_coverage)}
          </td>
          <td class="metric-value">${formatNumber(metrics.emails_delivered)}</td>
          <td class="metric-value ${getMetricClass('unique_ctr', metrics.unique_ctr)}">
            ${formatPercent(metrics.unique_ctr)}
          </td>
          <td class="metric-value ${getMetricClass('ucr', metrics.ucr)}">
            ${formatPercent(metrics.ucr)}
          </td>
        </tr>
      `;
    });
  }

  // Grand total row
  if (emailData.grand_total) {
    html += `
      <tr class="total-row">
        <td>GRAND TOTAL</td>
        <td class="metric-value ${getMetricClass('dse_coverage', emailData.grand_total.dse_coverage)}">
          ${formatPercent(emailData.grand_total.dse_coverage)}
        </td>
        <td class="metric-value">${formatNumber(emailData.grand_total.emails_delivered)}</td>
        <td class="metric-value ${getMetricClass('unique_ctr', emailData.grand_total.unique_ctr)}">
          ${formatPercent(emailData.grand_total.unique_ctr)}
        </td>
        <td class="metric-value ${getMetricClass('ucr', emailData.grand_total.ucr)}">
          ${formatPercent(emailData.grand_total.ucr)}
        </td>
      </tr>
    `;
  }

  tbody.innerHTML = html;
}

// Auto-load on page load
window.addEventListener('DOMContentLoaded', () => {
  console.log('📧 Email Scorecard ready');
});
