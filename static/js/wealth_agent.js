/**
 * AI Wealth Agent JavaScript
 */

// Mobile menu toggle
document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.querySelector('.sidebar');

    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('open');
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function(e) {
            if (window.innerWidth <= 768) {
                if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
                    sidebar.classList.remove('open');
                }
            }
        });
    }

    // User dropdown
    const userMenu = document.querySelector('.user-menu');
    const dropdownMenu = document.querySelector('.dropdown-menu');

    if (userMenu && dropdownMenu) {
        userMenu.addEventListener('click', function(e) {
            e.stopPropagation();
            dropdownMenu.classList.toggle('show');
        });

        document.addEventListener('click', function() {
            dropdownMenu.classList.remove('show');
        });
    }
});

// Utility functions
function formatCurrency(amount, currency = 'SEK') {
    return new Intl.NumberFormat('sv-SE', {
        style: 'decimal',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount) + ' ' + currency;
}

function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('sv-SE');
}

function formatTime(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleTimeString('sv-SE', { hour: '2-digit', minute: '2-digit' });
}

// API helper
async function apiCall(url, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(url, options);
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'API error');
        }

        return result;
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Toast notifications
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    document.body.appendChild(toast);

    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 10);

    // Remove after delay
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Add toast styles dynamically
const toastStyles = document.createElement('style');
toastStyles.textContent = `
    .toast {
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 1000;
        transform: translateY(100px);
        opacity: 0;
        transition: all 0.3s ease;
    }
    .toast.show {
        transform: translateY(0);
        opacity: 1;
    }
    .toast-info { background: #6366f1; }
    .toast-success { background: #22c55e; }
    .toast-warning { background: #f59e0b; }
    .toast-error { background: #ef4444; }
`;
document.head.appendChild(toastStyles);

// Loading spinner
function showLoading(element) {
    element.innerHTML = '<div class="loading-spinner"></div>';
}

// Confirm dialog
function confirmAction(message) {
    return new Promise((resolve) => {
        const result = confirm(message);
        resolve(result);
    });
}

// Dashboard-specific functions
async function loadDashboardData() {
    try {
        const data = await apiCall('/wealth/api/dashboard');
        if (data.success) {
            updateDashboard(data.data);
        }
    } catch (error) {
        console.error('Failed to load dashboard:', error);
    }
}

function updateDashboard(data) {
    // Update goals progress
    if (data.goals) {
        const progressElement = document.getElementById('overallProgress');
        if (progressElement) {
            progressElement.textContent = `${data.goals.overall_progress}%`;
        }
    }

    // Update insights count
    if (data.insights) {
        const insightsCount = document.getElementById('unreadInsights');
        if (insightsCount) {
            insightsCount.textContent = data.insights.unread_count;
        }
    }
}

// Mark insight as read
async function markInsightRead(insightId) {
    try {
        await apiCall(`/wealth/api/insights/${insightId}/read`, 'PUT');
        const insightElement = document.querySelector(`[data-insight-id="${insightId}"]`);
        if (insightElement) {
            insightElement.classList.remove('unread');
        }
    } catch (error) {
        console.error('Failed to mark insight as read:', error);
    }
}

// Dismiss insight
async function dismissInsight(insightId) {
    try {
        await apiCall(`/wealth/api/insights/${insightId}/dismiss`, 'PUT');
        const insightElement = document.querySelector(`[data-insight-id="${insightId}"]`);
        if (insightElement) {
            insightElement.remove();
        }
        showToast('Insikt avvisad', 'success');
    } catch (error) {
        console.error('Failed to dismiss insight:', error);
        showToast('Kunde inte avvisa insikt', 'error');
    }
}

// Export for use in templates
window.WealthAgent = {
    apiCall,
    showToast,
    confirmAction,
    formatCurrency,
    formatDate,
    formatTime,
    loadDashboardData,
    markInsightRead,
    dismissInsight
};
