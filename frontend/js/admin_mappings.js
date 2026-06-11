/**
 * Admin Mappings Management - Modern UI with Dropdowns
 * Country to OU and Product to Cloud mappings
 */

// Auto-detect API URL based on environment
const getMappingsApiUrl = () => {
    const hostname = window.location.hostname;
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return 'http://localhost:8000';
    }
    return window.location.origin;
};

const MAPPINGS_API = `${getMappingsApiUrl()}/api/mappings`;

let countryMappings = {};
let productMappings = {};
let availableOUs = ['UKI', 'FRANCE', 'CENTRAL', 'NORTH', 'SOUTH', 'AMER', 'Canada', 'Others'];
let availableClouds = ['Agentforce', 'Sales', 'Service', 'Marketing', 'Commerce', 'Data', 'Platform', 'Mulesoft', 'Tableau', 'Slack', 'Others'];
let currentMappingTab = 'country';
let editingCountry = null;
let editingProduct = null;

// ==========================================
// TAB SWITCHING
// ==========================================

function switchMappingTab(tab) {
    currentMappingTab = tab;

    const countryTab = document.getElementById('countryMappingTab');
    const productTab = document.getElementById('productMappingTab');
    const countryPanel = document.getElementById('countryMappingPanel');
    const productPanel = document.getElementById('productMappingPanel');

    if (tab === 'country') {
        countryTab.style.borderBottom = '3px solid var(--brand)';
        countryTab.style.color = 'var(--brand)';
        productTab.style.borderBottom = 'none';
        productTab.style.color = 'var(--muted)';
        countryPanel.style.display = 'block';
        productPanel.style.display = 'none';
    } else {
        productTab.style.borderBottom = '3px solid var(--brand)';
        productTab.style.color = 'var(--brand)';
        countryTab.style.borderBottom = 'none';
        countryTab.style.color = 'var(--muted)';
        productPanel.style.display = 'block';
        countryPanel.style.display = 'none';
    }
}

// ==========================================
// COUNTRY MAPPINGS
// ==========================================

async function loadCountryMappings() {
    try {
        const response = await fetch(`${MAPPINGS_API}/country`);
        countryMappings = await response.json();
        renderCountryMappings();
        updateCountryStats();
    } catch (error) {
        console.error('Error loading country mappings:', error);
        countryMappings = getDefaultCountryMappings();
        renderCountryMappings();
        updateCountryStats();
    }
}

function getDefaultCountryMappings() {
    return {
        'Ireland': 'UKI', 'India': 'Others', 'South Korea': 'Others',
        'Germany': 'CENTRAL', 'Sweden': 'NORTH', 'Japan': 'Others',
        'Spain': 'SOUTH', 'CEE': 'SOUTH', 'Italy': 'SOUTH',
        'UK': 'UKI', 'Turkey': 'SOUTH', 'United States': 'AMER',
        'Finland': 'NORTH', 'Norway': 'NORTH', 'Brazil': 'Others',
        'Luxembourg': 'NORTH', 'Denmark': 'NORTH', 'Portugal': 'SOUTH',
        'Austria': 'CENTRAL', 'Canada': 'Canada', 'Mexico': 'Others',
        'Israel': 'SOUTH', 'Mediterranean': 'SOUTH', 'France': 'FRANCE',
        'MDE': 'SOUTH', 'ANZ': 'Others', 'Iceland': 'NORTH',
        'Africa': 'SOUTH', 'Switzerland & Liechtenstein': 'CENTRAL',
        'Thailand': 'Others', 'Netherlands': 'NORTH', 'Belgium': 'NORTH',
        'United Kingdom': 'UKI'
    };
}

function renderCountryMappings() {
    const grid = document.getElementById('countryMappingsGrid');
    const searchInput = document.getElementById('countrySearchInput');
    const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';

    const sortedCountries = Object.keys(countryMappings).sort();
    const filtered = searchTerm ?
        sortedCountries.filter(c => c.toLowerCase().includes(searchTerm)) :
        sortedCountries;

    let html = '';

    filtered.forEach(country => {
        const ou = countryMappings[country];
        const ouColor = getOUColor(ou);
        const ouBg = getOUBackground(ou);

        html += `
            <div class="mapping-card" style="background: var(--bg-white); border: 2px solid ${ouBg}; border-radius: 10px; padding: 14px; position: relative; transition: all 0.2s; cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,0.08);"
                 onmouseover="this.style.boxShadow='0 6px 20px rgba(0,0,0,0.12)'; this.style.transform='translateY(-2px)'"
                 onmouseout="this.style.boxShadow='0 2px 8px rgba(0,0,0,0.08)'; this.style.transform='translateY(0)'">

                <!-- Country Name -->
                <div style="font-size: 15px; font-weight: 600; color: var(--text); margin-bottom: 10px; padding-right: 30px;">
                    ${country}
                </div>

                <!-- OU Badge -->
                <div style="display: inline-flex; align-items: center; padding: 6px 12px; background: ${ouBg}; border-radius: 6px; font-size: 12px; font-weight: 700; color: ${ouColor};">
                    → ${ou}
                </div>

                <!-- Edit Button -->
                <div style="position: absolute; top: 12px; right: 12px; display: flex; gap: 4px;">
                    <button onclick="editCountryMapping('${country.replace(/'/g, "\\'")}', '${ou}')"
                            style="padding: 6px 10px; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 600;"
                            title="Edit">
                        ✏️
                    </button>
                    <button onclick="deleteCountryMapping('${country.replace(/'/g, "\\'")}' )"
                            style="padding: 6px 10px; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 600;"
                            title="Delete">
                        🗑️
                    </button>
                </div>
            </div>
        `;
    });

    if (filtered.length === 0) {
        html = `<div style="grid-column: 1/-1; text-align: center; padding: 60px; color: var(--muted);">
            <div style="font-size: 48px; margin-bottom: 16px;">🔍</div>
            <div style="font-size: 16px; font-weight: 600;">No countries found</div>
            <div style="font-size: 13px; margin-top: 8px;">Try a different search term</div>
        </div>`;
    }

    grid.innerHTML = html;
}

function filterCountryMappings() {
    renderCountryMappings();
}

function updateCountryStats() {
    const total = Object.keys(countryMappings).length;
    const emea = Object.values(countryMappings).filter(ou => ['UKI', 'FRANCE', 'CENTRAL', 'NORTH', 'SOUTH'].includes(ou)).length;
    const amer = Object.values(countryMappings).filter(ou => ['AMER', 'Canada'].includes(ou)).length;

    document.getElementById('countryTotalCount').textContent = total;
    document.getElementById('countryEmeaCount').textContent = emea;
    document.getElementById('countryAmerCount').textContent = amer;
    document.getElementById('countryMappingTab').innerHTML = `🌍 Countries (${total})`;
}

function showAddCountryModal() {
    editingCountry = null;
    document.getElementById('countryModalTitle').textContent = 'Add Country Mapping';
    document.getElementById('countryModalInput').value = '';
    populateOUDropdown();
    showModal('countryMappingModal');
}

function editCountryMapping(country, currentOU) {
    editingCountry = country;
    document.getElementById('countryModalTitle').textContent = 'Edit Country Mapping';
    document.getElementById('countryModalInput').value = country;
    document.getElementById('countryModalInput').disabled = true;
    populateOUDropdown(currentOU);
    showModal('countryMappingModal');
}

function populateOUDropdown(selectedOU = null) {
    const select = document.getElementById('countryModalSelect');
    let html = '<option value="">-- Select OU --</option>';

    availableOUs.forEach(ou => {
        const selected = ou === selectedOU ? 'selected' : '';
        html += `<option value="${ou}" ${selected}>${ou}</option>`;
    });

    select.innerHTML = html;
}

function saveCountryModal() {
    const country = document.getElementById('countryModalInput').value.trim();
    const ou = document.getElementById('countryModalSelect').value;

    if (!country) {
        alert('❌ Please enter a country name');
        return;
    }

    if (!ou) {
        alert('❌ Please select an Operating Unit');
        return;
    }

    countryMappings[country] = ou;
    renderCountryMappings();
    updateCountryStats();
    closeCountryModal();

    if (editingCountry) {
        alert(`✅ Updated: ${country} → ${ou}\n\n⚠️ Don't forget to click "Save All" to persist!`);
    } else {
        alert(`✅ Added: ${country} → ${ou}\n\n⚠️ Don't forget to click "Save All" to persist!`);
    }
}

function closeCountryModal() {
    hideModal('countryMappingModal');
    document.getElementById('countryModalInput').disabled = false;
    editingCountry = null;
}

function deleteCountryMapping(country) {
    if (confirm(`Delete mapping for "${country}"?\n\nThis will remove the country from the mappings.`)) {
        delete countryMappings[country];
        renderCountryMappings();
        updateCountryStats();
    }
}

async function saveCountryMappings() {
    const count = Object.keys(countryMappings).length;

    if (!confirm(`Save ${count} country mappings to server?\n\nThis will overwrite the existing mappings file and reload the Email parser.`)) {
        return;
    }

    try {
        // Save mappings
        const saveResponse = await fetch(`${MAPPINGS_API}/country`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(countryMappings)
        });

        if (!saveResponse.ok) {
            alert('❌ Failed to save to server. Changes kept locally only.');
            return;
        }

        // Reload parser to apply new mappings immediately
        const reloadResponse = await fetch(`${MAPPINGS_API}/reload`, {
            method: 'POST'
        });

        if (reloadResponse.ok) {
            const result = await reloadResponse.json();
            alert(`✅ Successfully saved ${count} country mappings!\n\n🔄 Email parser reloaded with ${result.country_count} country mappings and ${result.product_count} product mappings.\n\nThe changes are now active!`);
        } else {
            alert(`✅ Saved ${count} country mappings!\n\n⚠️ Failed to reload parser. Restart the backend to apply changes.`);
        }
    } catch (error) {
        console.error('Error saving:', error);
        alert('❌ Network error. Changes kept locally only.');
    }
}

function exportCountryCSV() {
    let csv = 'Country,OU\n';
    Object.keys(countryMappings).sort().forEach(country => {
        csv += `"${country}","${countryMappings[country]}"\n`;
    });

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'country_to_ou_mappings.csv';
    a.click();
    URL.revokeObjectURL(url);
}

// ==========================================
// PRODUCT MAPPINGS
// ==========================================

async function loadProductMappings() {
    try {
        const response = await fetch(`${MAPPINGS_API}/product`);
        productMappings = await response.json();
        renderProductMappings();
        updateProductStats();
    } catch (error) {
        console.error('Error loading product mappings:', error);
        productMappings = getDefaultProductMappings();
        renderProductMappings();
        updateProductStats();
    }
}

function getDefaultProductMappings() {
    return {
        'Agentforce': 'Agentforce',
        'Einstein AI': 'Agentforce',
        'Agentforce Sales': 'Sales',
        'Agentforce Service': 'Service',
        'Marketing Cloud': 'Marketing',
        'Slack': 'Slack'
    };
}

function renderProductMappings() {
    const grid = document.getElementById('productMappingsGrid');
    const searchInput = document.getElementById('productSearchInput');
    const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';

    const sortedProducts = Object.keys(productMappings).sort();
    const filtered = searchTerm ?
        sortedProducts.filter(p => p.toLowerCase().includes(searchTerm)) :
        sortedProducts;

    let html = '';

    filtered.forEach(product => {
        const cloud = productMappings[product];
        const cloudColor = getCloudColor(cloud);
        const cloudBg = getCloudBackground(cloud);

        html += `
            <div class="mapping-card" style="background: var(--bg-white); border: 2px solid ${cloudBg}; border-radius: 10px; padding: 14px; position: relative; transition: all 0.2s; cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,0.08);"
                 onmouseover="this.style.boxShadow='0 6px 20px rgba(0,0,0,0.12)'; this.style.transform='translateY(-2px)'"
                 onmouseout="this.style.boxShadow='0 2px 8px rgba(0,0,0,0.08)'; this.style.transform='translateY(0)'">

                <!-- Product Name -->
                <div style="font-size: 15px; font-weight: 600; color: var(--text); margin-bottom: 10px; padding-right: 30px;">
                    ${product}
                </div>

                <!-- Cloud Badge -->
                <div style="display: inline-flex; align-items: center; padding: 6px 12px; background: ${cloudBg}; border-radius: 6px; font-size: 12px; font-weight: 700; color: ${cloudColor};">
                    → ${cloud}
                </div>

                <!-- Edit Button -->
                <div style="position: absolute; top: 12px; right: 12px; display: flex; gap: 4px;">
                    <button onclick="editProductMapping('${product.replace(/'/g, "\\'")}', '${cloud}')"
                            style="padding: 6px 10px; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 600;"
                            title="Edit">
                        ✏️
                    </button>
                    <button onclick="deleteProductMapping('${product.replace(/'/g, "\\'")}' )"
                            style="padding: 6px 10px; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 600;"
                            title="Delete">
                        🗑️
                    </button>
                </div>
            </div>
        `;
    });

    if (filtered.length === 0) {
        html = `<div style="grid-column: 1/-1; text-align: center; padding: 60px; color: var(--muted);">
            <div style="font-size: 48px; margin-bottom: 16px;">🔍</div>
            <div style="font-size: 16px; font-weight: 600;">No products found</div>
            <div style="font-size: 13px; margin-top: 8px;">Try a different search term</div>
        </div>`;
    }

    grid.innerHTML = html;
}

function filterProductMappings() {
    renderProductMappings();
}

function updateProductStats() {
    const total = Object.keys(productMappings).length;
    const agentforce = Object.values(productMappings).filter(c => c === 'Agentforce').length;
    const core = Object.values(productMappings).filter(c => ['Sales', 'Service', 'Marketing', 'Commerce'].includes(c)).length;

    document.getElementById('productTotalCount').textContent = total;
    document.getElementById('productAgentforceCount').textContent = agentforce;
    document.getElementById('productCoreCount').textContent = core;
    document.getElementById('productMappingTab').innerHTML = `📦 Products (${total})`;
}

function showAddProductModal() {
    editingProduct = null;
    document.getElementById('productModalTitle').textContent = 'Add Product Mapping';
    document.getElementById('productModalInput').value = '';
    populateCloudDropdown();
    showModal('productMappingModal');
}

function editProductMapping(product, currentCloud) {
    editingProduct = product;
    document.getElementById('productModalTitle').textContent = 'Edit Product Mapping';
    document.getElementById('productModalInput').value = product;
    document.getElementById('productModalInput').disabled = true;
    populateCloudDropdown(currentCloud);
    showModal('productMappingModal');
}

function populateCloudDropdown(selectedCloud = null) {
    const select = document.getElementById('productModalSelect');
    let html = '<option value="">-- Select Cloud --</option>';

    availableClouds.forEach(cloud => {
        const selected = cloud === selectedCloud ? 'selected' : '';
        html += `<option value="${cloud}" ${selected}>${cloud}</option>`;
    });

    select.innerHTML = html;
}

function saveProductModal() {
    const product = document.getElementById('productModalInput').value.trim();
    const cloud = document.getElementById('productModalSelect').value;

    if (!product) {
        alert('❌ Please enter a product name');
        return;
    }

    if (!cloud) {
        alert('❌ Please select a Cloud');
        return;
    }

    productMappings[product] = cloud;
    renderProductMappings();
    updateProductStats();
    closeProductModal();

    if (editingProduct) {
        alert(`✅ Updated: ${product} → ${cloud}\n\n⚠️ Don't forget to click "Save All" to persist!`);
    } else {
        alert(`✅ Added: ${product} → ${cloud}\n\n⚠️ Don't forget to click "Save All" to persist!`);
    }
}

function closeProductModal() {
    hideModal('productMappingModal');
    document.getElementById('productModalInput').disabled = false;
    editingProduct = null;
}

function deleteProductMapping(product) {
    if (confirm(`Delete mapping for "${product}"?`)) {
        delete productMappings[product];
        renderProductMappings();
        updateProductStats();
    }
}

async function saveProductMappings() {
    const count = Object.keys(productMappings).length;

    if (!confirm(`Save ${count} product mappings to server?\n\nThis will overwrite the existing mappings file and reload the Email parser.`)) {
        return;
    }

    try {
        // Save mappings
        const saveResponse = await fetch(`${MAPPINGS_API}/product`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(productMappings)
        });

        if (!saveResponse.ok) {
            alert('❌ Failed to save to server.');
            return;
        }

        // Reload parser to apply new mappings immediately
        const reloadResponse = await fetch(`${MAPPINGS_API}/reload`, {
            method: 'POST'
        });

        if (reloadResponse.ok) {
            const result = await reloadResponse.json();
            alert(`✅ Successfully saved ${count} product mappings!\n\n🔄 Email parser reloaded with ${result.country_count} country mappings and ${result.product_count} product mappings.\n\nThe changes are now active!`);
        } else {
            alert(`✅ Saved ${count} product mappings!\n\n⚠️ Failed to reload parser. Restart the backend to apply changes.`);
        }
    } catch (error) {
        console.error('Error saving:', error);
        alert('❌ Network error.');
    }
}

function exportProductCSV() {
    let csv = 'Product,Cloud\n';
    Object.keys(productMappings).sort().forEach(product => {
        csv += `"${product}","${productMappings[product]}"\n`;
    });

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'product_to_cloud_mappings.csv';
    a.click();
    URL.revokeObjectURL(url);
}

// ==========================================
// MANAGE OUs
// ==========================================

function showManageOUsModal() {
    renderOUList();
    showModal('manageOUsModal');
}

function renderOUList() {
    const container = document.getElementById('ouList');
    let html = '';

    availableOUs.forEach(ou => {
        const color = getOUColor(ou);
        const bg = getOUBackground(ou);

        html += `
            <div style="display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; background: ${bg}; border: 2px solid ${color}; border-radius: 8px;">
                <span style="font-size: 15px; font-weight: 600; color: ${color};">${ou}</span>
                <button onclick="deleteOU('${ou}')" style="padding: 6px 12px; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 600;">
                    🗑️ Remove
                </button>
            </div>
        `;
    });

    container.innerHTML = html;
}

function addNewOU() {
    const input = document.getElementById('newOUInput');
    const newOU = input.value.trim();

    if (!newOU) {
        alert('❌ Please enter an OU name');
        return;
    }

    if (availableOUs.includes(newOU)) {
        alert('❌ This OU already exists');
        return;
    }

    availableOUs.push(newOU);
    renderOUList();
    input.value = '';
    alert(`✅ Added new OU: ${newOU}\n\nYou can now use it in country mappings.`);
}

function deleteOU(ou) {
    // Check if OU is in use
    const inUse = Object.values(countryMappings).filter(o => o === ou).length;

    if (inUse > 0) {
        if (!confirm(`⚠️ This OU is used in ${inUse} country mapping(s).\n\nDeleting it will break those mappings. Continue?`)) {
            return;
        }
    }

    availableOUs = availableOUs.filter(o => o !== ou);
    renderOUList();
    alert(`✅ Removed OU: ${ou}`);
}

function closeManageOUsModal() {
    hideModal('manageOUsModal');
}

// ==========================================
// MANAGE CLOUDS
// ==========================================

function showManageCloudsModal() {
    renderCloudList();
    showModal('manageCloudsModal');
}

function renderCloudList() {
    const container = document.getElementById('cloudList');
    let html = '';

    availableClouds.forEach(cloud => {
        const color = getCloudColor(cloud);
        const bg = getCloudBackground(cloud);

        html += `
            <div style="display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; background: ${bg}; border: 2px solid ${color}; border-radius: 8px;">
                <span style="font-size: 15px; font-weight: 600; color: ${color};">${cloud}</span>
                <button onclick="deleteCloud('${cloud}')" style="padding: 6px 12px; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 600;">
                    🗑️ Remove
                </button>
            </div>
        `;
    });

    container.innerHTML = html;
}

function addNewCloud() {
    const input = document.getElementById('newCloudInput');
    const newCloud = input.value.trim();

    if (!newCloud) {
        alert('❌ Please enter a Cloud name');
        return;
    }

    if (availableClouds.includes(newCloud)) {
        alert('❌ This Cloud already exists');
        return;
    }

    availableClouds.push(newCloud);
    renderCloudList();
    input.value = '';
    alert(`✅ Added new Cloud: ${newCloud}\n\nYou can now use it in product mappings.`);
}

function deleteCloud(cloud) {
    // Check if Cloud is in use
    const inUse = Object.values(productMappings).filter(c => c === cloud).length;

    if (inUse > 0) {
        if (!confirm(`⚠️ This Cloud is used in ${inUse} product mapping(s).\n\nDeleting it will break those mappings. Continue?`)) {
            return;
        }
    }

    availableClouds = availableClouds.filter(c => c !== cloud);
    renderCloudList();
    alert(`✅ Removed Cloud: ${cloud}`);
}

function closeManageCloudsModal() {
    hideModal('manageCloudsModal');
}

// ==========================================
// MODAL HELPERS
// ==========================================

function showModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.style.display = 'flex';
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.style.display = 'none';
}

// Close modals on ESC key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        hideModal('countryMappingModal');
        hideModal('productMappingModal');
        hideModal('manageOUsModal');
        hideModal('manageCloudsModal');
    }
});

// ==========================================
// COLOR HELPERS
// ==========================================

function getOUColor(ou) {
    const colors = {
        'UKI': '#10b981', 'FRANCE': '#3b82f6', 'CENTRAL': '#f59e0b',
        'NORTH': '#8b5cf6', 'SOUTH': '#ec4899', 'AMER': '#ef4444',
        'Canada': '#14b8a6', 'Others': '#6b7280'
    };
    return colors[ou] || '#6b7280';
}

function getOUBackground(ou) {
    const backgrounds = {
        'UKI': '#d1fae5', 'FRANCE': '#dbeafe', 'CENTRAL': '#fef3c7',
        'NORTH': '#ede9fe', 'SOUTH': '#fce7f3', 'AMER': '#fee2e2',
        'Canada': '#ccfbf1', 'Others': '#f3f4f6'
    };
    return backgrounds[ou] || '#f3f4f6';
}

function getCloudColor(cloud) {
    const colors = {
        'Agentforce': '#667eea', 'Sales': '#10b981', 'Service': '#3b82f6',
        'Marketing': '#ec4899', 'Commerce': '#f59e0b', 'Data': '#8b5cf6',
        'Platform': '#14b8a6', 'Mulesoft': '#6366f1', 'Tableau': '#f97316',
        'Slack': '#84cc16', 'Others': '#6b7280'
    };
    return colors[cloud] || '#6b7280';
}

function getCloudBackground(cloud) {
    const backgrounds = {
        'Agentforce': '#e0e7ff', 'Sales': '#d1fae5', 'Service': '#dbeafe',
        'Marketing': '#fce7f3', 'Commerce': '#fef3c7', 'Data': '#ede9fe',
        'Platform': '#ccfbf1', 'Mulesoft': '#e0e7ff', 'Tableau': '#ffedd5',
        'Slack': '#ecfccb', 'Others': '#f3f4f6'
    };
    return backgrounds[cloud] || '#f3f4f6';
}

// ==========================================
// INITIALIZATION
// ==========================================

function initMappingsAdmin() {
    loadCountryMappings();
    loadProductMappings();
}

// Hook into switchTab
const originalSwitchTab = window.switchTab;
if (originalSwitchTab) {
    window.switchTab = function(tab) {
        originalSwitchTab(tab);
        if (tab === 'admin') {
            setTimeout(initMappingsAdmin, 100);
        }
    };
}
