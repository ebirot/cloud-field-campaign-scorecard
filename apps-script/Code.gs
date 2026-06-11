/**
 * Cloud Field Campaign Scorecard - Google Apps Script
 * Main server-side code
 */

// Configuration - Change this to your backend URL when deployed
const BACKEND_URL = 'http://localhost:8000';

/**
 * Serve the main HTML page
 */
function doGet(e) {
  const htmlOutput = HtmlService.createTemplateFromFile('index')
    .evaluate()
    .setTitle('Cloud Field Campaign Scorecard')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL)
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');

  return htmlOutput;
}

/**
 * Include other HTML files (for CSS, JS)
 */
function include(filename) {
  return HtmlService.createHtmlOutputFromFile(filename).getContent();
}

/**
 * Get user email (for analytics)
 */
function getUserEmail() {
  return Session.getActiveUser().getEmail();
}

/**
 * Proxy API calls to backend (to avoid CORS issues)
 */
function proxyApiCall(endpoint, method, data) {
  const url = BACKEND_URL + endpoint;

  const options = {
    'method': method || 'get',
    'contentType': 'application/json',
    'muteHttpExceptions': true
  };

  if (data && method.toLowerCase() !== 'get') {
    options.payload = JSON.stringify(data);
  }

  try {
    const response = UrlFetchApp.fetch(url, options);
    return {
      statusCode: response.getResponseCode(),
      content: response.getContentText()
    };
  } catch (error) {
    return {
      statusCode: 500,
      content: JSON.stringify({ error: error.toString() })
    };
  }
}

/**
 * Get backend URL for client-side
 */
function getBackendUrl() {
  return BACKEND_URL;
}
