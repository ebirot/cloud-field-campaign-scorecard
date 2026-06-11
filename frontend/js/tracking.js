/**
 * Analytics Tracking Client
 * Lightweight auto-tracking for user engagement
 */

class AnalyticsTracker {
    constructor() {
        this.apiUrl = this.getApiUrl();
        this.sessionId = this.getOrCreateSessionId();
        this.userId = this.getOrCreateUserId();
        this.userName = localStorage.getItem('analytics_user_name') || null;
        this.pageLoadTime = Date.now();
        this.lastActivityTime = Date.now();

        this.init();
    }

    getApiUrl() {
        const hostname = window.location.hostname;
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return 'http://localhost:8000';
        }
        return window.location.origin;
    }

    getOrCreateSessionId() {
        let sid = sessionStorage.getItem('analytics_session_id');
        if (!sid) {
            sid = 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            sessionStorage.setItem('analytics_session_id', sid);
        }
        return sid;
    }

    getOrCreateUserId() {
        let uid = localStorage.getItem('analytics_user_id');
        if (!uid) {
            uid = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('analytics_user_id', uid);
        }
        return uid;
    }

    init() {
        // Track page load
        this.track('page_view', {
            page: this.getCurrentPage(),
            referrer: document.referrer,
            url: window.location.href
        });

        // Track page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.track('page_hidden', {
                    page: this.getCurrentPage(),
                    time_spent_seconds: Math.round((Date.now() - this.pageLoadTime) / 1000)
                });
            } else {
                this.track('page_visible', { page: this.getCurrentPage() });
                this.pageLoadTime = Date.now();
            }
        });

        // Track before unload
        window.addEventListener('beforeunload', () => {
            this.track('page_unload', {
                page: this.getCurrentPage(),
                time_spent_seconds: Math.round((Date.now() - this.pageLoadTime) / 1000)
            });
        });

        // Track activity (debounced)
        let activityTimeout;
        ['click', 'scroll', 'keypress', 'mousemove'].forEach(event => {
            document.addEventListener(event, () => {
                this.lastActivityTime = Date.now();

                clearTimeout(activityTimeout);
                activityTimeout = setTimeout(() => {
                    // User inactive for 30 seconds
                    if (Date.now() - this.lastActivityTime > 30000) {
                        this.track('user_inactive', { page: this.getCurrentPage() });
                    }
                }, 30000);
            }, { passive: true });
        });
    }

    getCurrentPage() {
        const path = window.location.pathname;
        if (path === '/' || path.includes('health_of_cloud')) return 'Health of Cloud';
        if (path.includes('admin')) return 'Admin Dashboard';
        if (path.includes('email')) return 'Email Scorecard';
        if (path.includes('lead')) return 'Lead Scorecard';
        return 'Unknown';
    }

    async track(eventType, data = {}) {
        try {
            const event = {
                event_type: eventType,
                page: this.getCurrentPage(),
                data: data,
                user_id: this.userId,
                user_name: this.userName,
                session_id: this.sessionId
            };

            // Send to API (fire and forget)
            fetch(`${this.apiUrl}/api/analytics/track`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(event)
            }).catch(() => {}); // Silently fail

        } catch (error) {
            // Fail silently
        }
    }

    identify(userName, metadata = {}) {
        this.userName = userName;
        localStorage.setItem('analytics_user_name', userName);

        fetch(`${this.apiUrl}/api/analytics/identify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: this.userId,
                user_name: userName,
                metadata: metadata
            })
        }).catch(() => {});
    }

    // Helper methods for common events
    trackClick(element, label) {
        this.track('click', {
            element: element,
            label: label,
            page: this.getCurrentPage()
        });
    }

    trackFilter(filterType, value) {
        this.track('filter_change', {
            filter_type: filterType,
            value: value,
            page: this.getCurrentPage()
        });
    }

    trackExport(exportType) {
        this.track('export', {
            export_type: exportType,
            page: this.getCurrentPage()
        });
    }

    trackCloudChange(cloud) {
        this.track('cloud_change', {
            cloud: cloud,
            page: this.getCurrentPage()
        });
    }

    trackQuarterChange(quarter) {
        this.track('quarter_change', {
            quarter: quarter,
            page: this.getCurrentPage()
        });
    }

    trackRegionChange(region) {
        this.track('region_change', {
            region: region,
            page: this.getCurrentPage()
        });
    }
}

// Initialize global tracker
window.analyticsTracker = new AnalyticsTracker();

// Expose simple API
window.trackEvent = (eventType, data) => {
    window.analyticsTracker.track(eventType, data);
};

window.identifyUser = (userName, metadata) => {
    window.analyticsTracker.identify(userName, metadata);
};
