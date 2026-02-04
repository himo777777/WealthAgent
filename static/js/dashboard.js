/**
 * ComplicationAI Dashboard - JavaScript
 */

// Sidebar Toggle
document.getElementById('menuToggle')?.addEventListener('click', () => {
    document.querySelector('.sidebar').classList.toggle('open');
});

// Close sidebar when clicking outside on mobile
document.addEventListener('click', (e) => {
    const sidebar = document.querySelector('.sidebar');
    const menuToggle = document.getElementById('menuToggle');

    if (window.innerWidth <= 768 &&
        !sidebar.contains(e.target) &&
        !menuToggle.contains(e.target)) {
        sidebar.classList.remove('open');
    }
});

// Format numbers
function formatNumber(num, decimals = 1) {
    return Number(num).toFixed(decimals);
}

// Format percentage
function formatPercent(num) {
    return (num * 100).toFixed(1) + '%';
}

// Risk level colors
const riskColors = {
    low: '#10b981',
    moderate: '#f59e0b',
    elevated: '#f97316',
    high: '#ef4444'
};

// Risk level labels
const riskLabels = {
    low: 'Låg Risk',
    moderate: 'Måttlig Risk',
    elevated: 'Förhöjd Risk',
    high: 'Hög Risk'
};

// Create animated counter
function animateValue(element, start, end, duration = 1000) {
    const range = end - start;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Easing function
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = start + (range * eased);

        element.textContent = formatPercent(current / 100);

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

// Loading spinner
function showLoading(button) {
    button.disabled = true;
    button.dataset.originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Laddar...';
}

function hideLoading(button) {
    button.disabled = false;
    button.innerHTML = button.dataset.originalText;
}

// Toast notifications
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;

    document.body.appendChild(toast);

    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 10);

    // Remove after 3 seconds
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
        background: white;
        border-radius: 8px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        gap: 0.75rem;
        transform: translateY(100px);
        opacity: 0;
        transition: all 0.3s ease;
        z-index: 9999;
    }
    .toast.show {
        transform: translateY(0);
        opacity: 1;
    }
    .toast-success i { color: #10b981; }
    .toast-error i { color: #ef4444; }
    .toast-info i { color: #3b82f6; }
`;
document.head.appendChild(toastStyles);

// API helper
async function apiCall(endpoint, method = 'GET', data = null) {
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
        const response = await fetch(endpoint, options);
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.message || 'API request failed');
        }

        return result;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Initialize tooltips
function initTooltips() {
    document.querySelectorAll('[data-tooltip]').forEach(element => {
        element.addEventListener('mouseenter', (e) => {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = e.target.dataset.tooltip;
            document.body.appendChild(tooltip);

            const rect = e.target.getBoundingClientRect();
            tooltip.style.left = `${rect.left + rect.width / 2 - tooltip.offsetWidth / 2}px`;
            tooltip.style.top = `${rect.top - tooltip.offsetHeight - 8}px`;
        });

        element.addEventListener('mouseleave', () => {
            document.querySelectorAll('.tooltip').forEach(t => t.remove());
        });
    });
}

// Sortable tables
function initSortableTables() {
    document.querySelectorAll('.data-table.sortable th[data-sort]').forEach(th => {
        th.style.cursor = 'pointer';
        th.addEventListener('click', () => {
            const table = th.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const column = th.dataset.sort;
            const columnIndex = Array.from(th.parentElement.children).indexOf(th);

            // Toggle sort direction
            const isAsc = th.classList.contains('asc');
            table.querySelectorAll('th').forEach(h => h.classList.remove('asc', 'desc'));
            th.classList.add(isAsc ? 'desc' : 'asc');

            rows.sort((a, b) => {
                const aVal = a.children[columnIndex]?.textContent || '';
                const bVal = b.children[columnIndex]?.textContent || '';

                // Try numeric comparison first
                const aNum = parseFloat(aVal);
                const bNum = parseFloat(bVal);

                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return isAsc ? bNum - aNum : aNum - bNum;
                }

                // Fall back to string comparison
                return isAsc
                    ? bVal.localeCompare(aVal)
                    : aVal.localeCompare(bVal);
            });

            rows.forEach(row => tbody.appendChild(row));
        });
    });
}

// Chart.js default configuration
if (typeof Chart !== 'undefined') {
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.font.size = 12;
    Chart.defaults.color = '#6b7280';
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    initTooltips();
    initSortableTables();
});

// Export functions for use in templates
window.ComplicationAI = {
    showLoading,
    hideLoading,
    showToast,
    apiCall,
    formatPercent,
    riskColors,
    riskLabels
};
